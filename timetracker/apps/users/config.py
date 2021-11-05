# configuration values go here:
# e.g: key value pairs to be used inside model field choices
from drf_yasg import openapi

TOKEN_PAIR_RESPONSE_SCHEMA = openapi.Response(
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(title="Refresh Token", type=openapi.TYPE_STRING),
            "access": openapi.Schema(title="Access Token", type=openapi.TYPE_STRING),
        },
    ),
    description="JWT Token Pair.",
)
