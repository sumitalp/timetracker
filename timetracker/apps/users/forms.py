from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
    _unicode_ci_compare,
)

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    class Meta:
        model = User
        fields = ["email"]


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = User
        fields = "__all__"


class CustomAuthForm(AuthenticationForm):
    """
    https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.AdminSite.login_form
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter email", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


class PasswordSetConfirmation(PasswordResetForm):
    def get_users(self, email):
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(
            **{"%s__iexact" % email_field_name: email, "is_active": True}
        )
        return (
            u
            for u in active_users
            if _unicode_ci_compare(email, getattr(u, email_field_name))
        )
