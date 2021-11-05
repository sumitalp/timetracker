import json

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from factory import Faker
from factory.fuzzy import FuzzyText
from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken

from ...payments.tests.factory import AccountFactory
from ...payments.tests.mock import StripeMocker
from ...payments.tests.utils import ACCOUNT_ID
from ...restaurants.tests.factories import RestaurantRoleFactory
from ...restaurants.tests.fuzz import FuzzyPhoneNumber
from ..constants import TOKEN_OBTAIN_PAIR_ERROR_MESSAGE
from .config import PASSWORD
from .factories import UserFactory


class TestToken:
    obtain_pair_url = reverse("api_v1:token_pair")
    obtain_refresh_url = reverse("api_v1:token_refresh")
    blacklist_url = reverse("api_v1:token_blacklist")

    def validate_access_token(self, access_token, user):
        access_token_payload = token_backend.decode(access_token, True)
        assert access_token_payload.get("token_type", "") == "access"
        assert access_token_payload.get("user_id", "") == user.id

    def validate_refresh_token(self, refresh_token, user):
        refresh_token_payload = token_backend.decode(refresh_token, True)
        assert refresh_token_payload.get("token_type", "") == "refresh"
        assert refresh_token_payload.get("user_id", "") == user.id

    def test_token_obtain_pair(self, client, user):
        response = client.post(
            self.obtain_pair_url, {"email": user.email, "password": PASSWORD}
        )
        assert response.status_code == 200
        access_token = response.data.get("access", "")
        refresh_token = response.data.get("refresh", "")
        self.validate_access_token(access_token, user)
        self.validate_refresh_token(refresh_token, user)

    def test_token_obtain_refresh(self, client, user):
        refresh_token = str(RefreshToken.for_user(user))
        response = client.post(self.obtain_refresh_url, {"refresh": refresh_token})
        assert response.status_code == 200
        access_token = response.data.get("access", "")
        new_refresh_token = response.data.get("refresh", "")
        self.validate_access_token(access_token, user)
        self.validate_refresh_token(new_refresh_token, user)

        with pytest.raises(TokenError) as token_error:
            RefreshToken(refresh_token).check_blacklist()
            assert token_error

    def test_token_blacklist(self, auth_client, user):
        refresh_token = RefreshToken.for_user(user)
        response = auth_client.post(self.blacklist_url, {"refresh": str(refresh_token)})

        with pytest.raises(TokenBackendError) as refresh_token_backend_error:
            token_backend.decode(refresh_token, True)
            assert refresh_token_backend_error

        with pytest.raises(TokenBackendError) as access_token_backend_error:
            token_backend.decode(refresh_token.access_token, True)
            assert access_token_backend_error

        assert response.status_code == 204

    def test_token_blacklist_another_user(self, auth_client):
        refresh_token = RefreshToken.for_user(UserFactory())
        response = auth_client.post(self.blacklist_url, {"refresh": str(refresh_token)})

        assert response.status_code == 400
        assert response.data.get("refresh")

    def test_inactive_user_token_obtain_pair(self, client, user):
        user.is_active = False
        user.save()
        response = client.post(
            self.obtain_pair_url, {"email": user.email, "password": PASSWORD}
        )
        assert response.status_code == 401

    def test_error_message_for_token_obtain_pair(self, client, user):
        response = client.post(
            self.obtain_pair_url, {"email": user.email, "password": "invalid"}
        )
        assert response.status_code == 401
        assert response.data.get("detail") == TOKEN_OBTAIN_PAIR_ERROR_MESSAGE


class TestUserBase:
    @pytest.fixture
    def url(self):
        return reverse("api_v1:auth_user:detail_update")

    @pytest.fixture
    def data(self):
        return {
            "first_name": Faker("first_name").generate(),
            "last_name": Faker("last_name").generate(),
            "phone_number": FuzzyPhoneNumber().fuzz(),
        }


class TestUserDetail(TestUserBase, StripeMocker):
    def test_auth_user_detail(self, auth_client, user, url):
        response = auth_client.get(url)
        assert response.status_code == 200

        assert user.email == response.data.get("email")
        assert not response.data.get("restaurant_id")

    def test_auth_user_detail_with_restaurants(self, mocker, auth_client, user, url):
        account_id = ACCOUNT_ID
        details_submitted = True

        success_payload = {
            "id": account_id,
            "details_submitted": details_submitted,
            **self.success_payload,
        }
        self.request_mock(mocker, self.retrieve_request_method, success_payload)
        restaurant_role = RestaurantRoleFactory(
            user=user, restaurant__paid_onboarding=True
        )
        account = AccountFactory(
            restaurant=restaurant_role.restaurant,
            id=account_id,
            metadata=json.dumps({"details_submitted": False}),
        )
        assert not account.get_metadata_dict().get("details_submitted", False)

        response = auth_client.get(url)
        assert response.status_code == 200

        assert user.email == response.data.get("email")
        assert response.data.get("restaurant_id") == restaurant_role.restaurant_id
        assert response.data.get("restaurant_name") == restaurant_role.restaurant.name
        assert response.data.get("restaurant_role_type") == restaurant_role.role_type
        assert (
            response.data.get("restaurant_created_at")
            == restaurant_role.restaurant.created_at
        )
        assert (
            response.data.get("restaurant_paid_onboarding")
            == restaurant_role.restaurant.paid_onboarding
        )
        assert response.data.get("restaurant_stripe_details") == {
            "id": restaurant_role.restaurant.stripe_account.id,
            "submitted": details_submitted,
        }
        account.refresh_from_db()
        assert account.get_metadata_dict().keys() == success_payload.keys()


class TestUserUpdate(TestUserBase):
    def test_auth_user_update_information(self, url, user, auth_client, data):
        response = auth_client.patch(
            url,
            data=data,
        )

        user.refresh_from_db()
        assert response.status_code == 200
        assert user.first_name == response.data.get("first_name")
        assert user.last_name == response.data.get("last_name")
        assert user.phone_number == response.data.get("phone_number")

    def test_auth_user_email_change(
        self, mailoutbox, synchronize_celery_tasks, user, auth_client, data, url
    ):
        data["email"] = Faker("email").generate()
        response = auth_client.patch(
            url,
            data=data,
        )
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.first_name == response.data.get("first_name")
        assert user.last_name == response.data.get("last_name")
        assert user.phone_number == response.data.get("phone_number")
        assert user.email == response.data.get("email")

        assert len(mailoutbox) == 1

    def test_auth_user_email_change_with_existing_mail(
        self, mailoutbox, synchronize_celery_tasks, user, auth_client, data, url
    ):
        new_user = UserFactory()
        data["email"] = new_user.email
        response = auth_client.patch(
            url,
            data=data,
        )
        user.refresh_from_db()
        assert response.status_code == 400
        assert len(mailoutbox) == 0


class TestPasswordSet:
    url = reverse("api_v1:auth_user:password:set")

    def test_password_set(self, client, inactive_unusable_user):
        new_password = FuzzyText(length=10).fuzz()
        uidb64 = urlsafe_base64_encode(force_bytes(inactive_unusable_user.id))
        token = PasswordResetTokenGenerator().make_token(user=inactive_unusable_user)

        response = client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "uid": uidb64,
                "token": token,
            },
        )

        inactive_unusable_user.refresh_from_db()

        assert response.status_code == 201
        assert inactive_unusable_user.check_password(new_password)
        assert inactive_unusable_user.is_active

    def test_password_set_invalid_uid(self, client, inactive_unusable_user):
        new_password = FuzzyText(length=10).fuzz()
        token = PasswordResetTokenGenerator().make_token(user=inactive_unusable_user)

        response = client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "uid": Faker("word"),
                "token": token,
            },
        )

        inactive_unusable_user.refresh_from_db()

        assert response.status_code == 400
        assert response.data.get("uid")
        assert not inactive_unusable_user.check_password(new_password)
        assert not inactive_unusable_user.is_active

    def test_password_set_invalid_token(self, client, inactive_unusable_user):
        new_password = FuzzyText(length=10).fuzz()
        uidb64 = urlsafe_base64_encode(force_bytes(inactive_unusable_user.id))

        response = client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "uid": uidb64,
                "token": Faker("word"),
            },
        )

        inactive_unusable_user.refresh_from_db()

        assert response.status_code == 400
        assert response.data.get("token")
        assert not inactive_unusable_user.check_password(new_password)
        assert not inactive_unusable_user.is_active


class TestPasswordResetEmail:
    url = reverse("api_v1:auth_user:password:reset_email")

    def test_send_reset_password_email_for_existing_user(
        self, mailoutbox, synchronize_celery_tasks, client, user
    ):
        response = client.post(self.url, data={"email": user.email})
        assert response.status_code == 201
        assert len(mailoutbox) == 1

        for mail in mailoutbox:
            assert user.email in mail.to

    def test_send_reset_password_email_for_unknown_user(
        self, mailoutbox, synchronize_celery_tasks, client
    ):
        response = client.post(self.url, data={"email": Faker("email").generate()})

        assert response.status_code == 201
        assert len(mailoutbox) == 0


class TestPasswordReset:
    url = reverse("api_v1:auth_user:password:reset")

    def test_password_reset(self, mailoutbox, synchronize_celery_tasks, client, user):
        new_password = FuzzyText(length=10).fuzz()

        assert not PASSWORD == new_password
        assert user.check_password(PASSWORD)

        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user=user)

        response = client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "uid": uidb64,
                "token": token,
            },
        )

        user.refresh_from_db()

        assert response.status_code == 201
        assert not user.check_password(PASSWORD)
        assert user.check_password(new_password)

        assert len(mailoutbox) == 1
        for mail in mailoutbox:
            assert user.email in mail.to


class TestPasswordCheck:
    @pytest.fixture
    def url(self):
        return reverse("api_v1:auth_user:password:check")

    def test_password_check(self, user, auth_client, url):
        response = auth_client.post(
            url,
            data={"password": PASSWORD},
        )
        assert response.status_code == 201
        assert response.data.get("is_verified")

    def test_password_check_failed(self, user, auth_client, url):
        random_password = FuzzyText(length=10).fuzz()
        response = auth_client.post(
            url,
            data={"password": random_password},
        )
        assert response.status_code == 201
        assert not response.data.get("is_verified")


class TestPasswordChange:
    url = reverse("api_v1:auth_user:password:change")

    def test_password_change(
        self, mailoutbox, synchronize_celery_tasks, user, auth_client
    ):
        new_password = FuzzyText(length=10).fuzz()

        assert not PASSWORD == new_password
        assert user.check_password(PASSWORD)

        response = auth_client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "old_password": PASSWORD,
            },
        )

        user.refresh_from_db()

        assert response.status_code == 201
        assert not user.check_password(PASSWORD)
        assert user.check_password(new_password)

        assert len(mailoutbox) == 1
        for mail in mailoutbox:
            assert user.email in mail.to

    def test_password_change_failed(
        self, mailoutbox, synchronize_celery_tasks, user, auth_client
    ):
        new_password = FuzzyText(length=10).fuzz()
        random_password = FuzzyText(length=10).fuzz()

        assert not PASSWORD == new_password
        assert not new_password == random_password
        assert user.check_password(PASSWORD)

        response = auth_client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": random_password,
                "old_password": PASSWORD,
            },
        )
        assert response.status_code == 400

        response = auth_client.post(
            self.url,
            data={
                "new_password1": new_password,
                "new_password2": new_password,
                "old_password": random_password,
            },
        )
        assert response.status_code == 400
