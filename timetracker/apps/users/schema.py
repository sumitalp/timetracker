from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView

from timetracker.apps.users.config import TOKEN_PAIR_RESPONSE_SCHEMA
from timetracker.apps.users.views import TokenBlackListPairView, TokenObtainPairView

blacklist_token_view = swagger_auto_schema(
    method="post", operation_description="", responses={status.HTTP_204_NO_CONTENT: ""}
)(TokenBlackListPairView.as_view())


token_obtain_pair_view = swagger_auto_schema(
    method="post",
    operation_description="Generate JWT token pair.",
    responses={status.HTTP_200_OK: TOKEN_PAIR_RESPONSE_SCHEMA},
)(TokenObtainPairView.as_view())


token_refresh_view = swagger_auto_schema(
    method="post",
    operation_description="Generate new/updated JWT token pair.",
    responses={status.HTTP_200_OK: TOKEN_PAIR_RESPONSE_SCHEMA},
)(TokenRefreshView.as_view())
