from django.contrib.auth.forms import SetPasswordForm
from factory.fuzzy import FuzzyText


class TestPasswordSetValidation:
    def test_password_set_minimum_length_validation(self, user):
        password = FuzzyText(length=5).fuzz()
        form = SetPasswordForm(
            user, data={"new_password1": password, "new_password2": password}
        )
        form.is_valid()
        assert form.has_error("new_password2", "password_too_short")
        assert form.errors

    def test_password_set_maximum_length_validation(self, user):
        password = FuzzyText(length=21).fuzz()
        form = SetPasswordForm(
            user, data={"new_password1": password, "new_password2": password}
        )
        form.is_valid()
        assert form.has_error("new_password2", "password_too_long")
        assert form.errors

    def test_password_set_has_symbol_validation(self, user):
        password = FuzzyText(length=5).fuzz() + "&"
        form = SetPasswordForm(
            user, data={"new_password1": password, "new_password2": password}
        )
        form.is_valid()
        assert form.has_error("new_password2", "password_has_symbol")
        assert form.errors

    def test_password_set_has_no_uppercase_validation(self, user):
        password = FuzzyText(length=5).fuzz()
        form = SetPasswordForm(
            user,
            data={"new_password1": password.lower(), "new_password2": password.lower()},
        )
        form.is_valid()
        assert form.has_error("new_password2", "password_no_upper")
        assert form.errors

    def test_password_set_has_no_lowercase_validation(self, user):
        password = FuzzyText(length=5).fuzz()
        form = SetPasswordForm(
            user,
            data={"new_password1": password.upper(), "new_password2": password.upper()},
        )
        form.is_valid()
        assert form.has_error("new_password2", "password_no_lower")
        assert form.errors
