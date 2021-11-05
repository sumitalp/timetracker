from django.db import DataError
from factory.fuzzy import FuzzyText
from pytest import raises
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow, datetime_to_epoch

from timetracker.apps.users.tests.factories import UserFactory


class TestUser:
    """
    https://pytest-django.readthedocs.io/en/latest/helpers.html#django-user-model
    """

    def test_user_email_character_length(self):
        with raises(DataError) as email_length_error:
            UserFactory(email=FuzzyText(length=50, suffix="@something.com").fuzz())
        assert (
            "value too long for type character varying(50)"
            in email_length_error.value.__str__()
        )


class TestTokenRecord:
    def test_token_entry(self, user):
        refresh_token = RefreshToken().for_user(user)
        assert OutstandingToken.objects.filter(
            user_id=user.id, token__exact=str(refresh_token)
        ).exists()
        refresh_token.blacklist()
        assert BlacklistedToken.objects.filter(
            token__user_id=user.id, token__token__exact=str(refresh_token)
        ).exists()


class TestTokenBlacklist:
    def test_blacklist_expired_token(self, user, settings):
        RefreshToken().for_user(user)
        outstanding_token = OutstandingToken.objects.filter(user_id=user.id)
        assert outstanding_token.count() == 1
        payload = token_backend.decode(outstanding_token.first().token, verify=True)
        new_expire_time = aware_utcnow() - settings.SIMPLE_JWT.get(
            "REFRESH_TOKEN_LIFETIME"
        )
        payload["exp"] = datetime_to_epoch(new_expire_time)
        outstanding_token.update(
            token=token_backend.encode(payload=payload), expires_at=new_expire_time
        )

        user.refresh_from_db()
        user.blacklist_outstanding_tokens()

        assert not BlacklistedToken.objects.filter(token__user_id=user.id).count()

    def test_blacklist_valid_token(self, user):
        user_token_count = 2
        for _ in range(user_token_count):
            RefreshToken().for_user(user)

        new_user = UserFactory()
        RefreshToken().for_user(new_user)

        assert (
            OutstandingToken.objects.filter(user_id=user.id).count() == user_token_count
        )

        user.refresh_from_db()
        user.blacklist_outstanding_tokens()

        assert (
            BlacklistedToken.objects.filter(token__user_id=user.id).count()
            == user_token_count
        )
        assert not BlacklistedToken.objects.filter(token__user_id=new_user.id).count()
