from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView as SimpleTokenObtainPairView,
)

from timetracker.apps.users.serializers import (
    ChangePasswordSerializer,
    PasswordCheckSerializer,
    TokenBlackListSerializer,
    TokenObtainPairSerializer,
    UserSerializer,
)

User = get_user_model()


class TokenBlackListPairView(CreateAPIView):
    serializer_class = TokenBlackListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TokenObtainPairView(SimpleTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class PasswordCheck(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordCheckSerializer


class PasswordChangeAPIView(CreateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
