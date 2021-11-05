from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as SimpleTokenObtainPairSerializer,
)
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import TOKEN_OBTAIN_PAIR_ERROR_MESSAGE
from .validators import FirstNameRegexValidator, SurnameRegexValidator

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True, max_length=25, validators=[FirstNameRegexValidator()]
    )
    last_name = serializers.CharField(
        required=True, max_length=25, validators=[SurnameRegexValidator()]
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
        ]


class UserSerializer(UserPublicSerializer):
    class Meta(UserPublicSerializer.Meta):
        fields = UserPublicSerializer.Meta.fields + [
            "is_staff",
            "is_active",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "is_staff",
            "is_active",
            "is_superuser",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class TokenBlackListSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, refresh):
        access_token_payload = token_backend.decode(refresh, True)
        if (
            not access_token_payload.get("user_id")
            == self.context.get("request").user.id
        ):
            raise serializers.ValidationError(
                "Submitted token for blacklist does not match the authenticated user."
            )
        return refresh

    def validate(self, attrs):
        super().validate(attrs)
        refresh = attrs.get("refresh", "")
        try:
            refresh_token = RefreshToken(refresh)
        except TokenError as token_error:
            raise serializers.ValidationError({"refresh": token_error})

        refresh_token.blacklist()
        attrs["refresh"] = ""
        return attrs


class TokenObtainPairSerializer(SimpleTokenObtainPairSerializer):
    default_error_messages = {"no_active_account": _(TOKEN_OBTAIN_PAIR_ERROR_MESSAGE)}


class PasswordCheckSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    is_verified = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        request = self.context.get("request", None)
        password = validated_data.pop("password", "")
        validated_data["is_verified"] = request.user.check_password(password)
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    password_change_form = PasswordChangeForm
    form = None

    def validate(self, attrs):
        super().validate(attrs)
        self.form = self.password_change_form(
            user=self.context.get("request").user, data=attrs
        )
        if not self.form.is_valid():
            raise serializers.ValidationError(self.form.errors)
        return attrs

    def save(self, **kwargs):
        user = self.form.save()
        user.blacklist_outstanding_tokens()

        return user
