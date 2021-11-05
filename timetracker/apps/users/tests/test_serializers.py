from django.core.validators import MaxLengthValidator
from factory import build
from factory.fuzzy import FuzzyText
from pytest import raises
from rest_framework.exceptions import ValidationError

from timetracker.apps.users.serializers import UserSerializer
from timetracker.apps.users.tests.factories import UserFactory


class TestUser:
    def test_email_field_length(self):
        user_data = build(
            dict,
            FACTORY_CLASS=UserFactory,
            email=FuzzyText(length=50, suffix="@something.com").fuzz(),
        )
        serializer = UserSerializer(data=user_data)
        with raises(ValidationError) as email_validation_error:
            serializer.is_valid(raise_exception=True)
        assert MaxLengthValidator.code in email_validation_error.value.get_codes().get(
            "email", []
        )
