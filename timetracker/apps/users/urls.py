from django.urls import include, path

from .schema import blacklist_token_view, token_obtain_pair_view, token_refresh_view
from .views import (
    PasswordChangeAPIView,
    PasswordCheck,
    UserCreateAPIView,
    UserRetrieveUpdateAPIView,
)

app_name = "users"

auth_patterns = [
    path("token/", token_obtain_pair_view, name="token_pair"),
    path("token-refresh/", token_refresh_view, name="token_refresh"),
    path("token-blacklist/", blacklist_token_view, name="token_blacklist"),
]

password_patterns = [
    #     path("reset-email/", PasswordResetEmailAPIView.as_view(), name="reset_email"),
    #     path("set/", PasswordSetAPIView.as_view(), name="set"),
    #     path("reset/", PasswordResetAPIView.as_view(), name="reset"),
    #     path("check/", PasswordCheck.as_view(), name="check"),
    path("change/", PasswordChangeAPIView.as_view(), name="change"),
]

urlpatterns = [
    path("", UserCreateAPIView.as_view(), name="create"),
    path("me/", UserRetrieveUpdateAPIView.as_view(), name="detail_update"),
    path("password/", include((password_patterns, "password"), namespace="password")),
]
