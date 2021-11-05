from typing import Any, Sequence

import factory
from django.contrib.auth import get_user_model
from factory import Faker, post_generation

from timetracker.apps.restaurants.tests.fuzz import FuzzyPhoneNumber

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = factory.Faker("email")
    is_active = True
    phone_number = FuzzyPhoneNumber()

    class Meta:
        model = User
        django_get_or_create = ("email",)

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        if not isinstance(self, dict):
            password = (
                extracted
                if extracted
                else Faker(
                    "password",
                    length=42,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                ).generate(extra_kwargs={})
            )
            self.set_password(password)
            self.save()
