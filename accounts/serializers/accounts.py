import logging

from core.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from utils.exceptions import (
    AuthFailureException,
    TokenInvalidException,
)
from utils.serializers import BaseManyToManyNestedSerializer

logger = logging.getLogger(__name__)


class AuthSerializer(serializers.Serializer):

    refresh = serializers.RegexField(
        regex=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$",
        error_messages={"invalid": "Invalid JWT token format"},
    )
    access = serializers.RegexField(
        regex=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$",
        error_messages={"invalid": "Invalid JWT token format"},
    )

    def get_avatar_url(self, instance):
        return instance.get_avatar_url

    class Meta:
        token_class = RefreshToken

    def to_representation(self, instance):
        if not isinstance(instance, User):
            raise AuthFailureException
        token = self.Meta.token_class.for_user(instance)
        return {
            "refresh": str(token),
            "access": str(token.access_token),
            "avatar_url": self.get_avatar_url(instance),
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "is_email_verified": instance.is_email_verified,
        }


class BaseSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def to_internal_value(self, data):
        data = data.copy()
        validated_data = {}

        for field in self.fields:
            if field not in data:
                continue

            value = data[field].strip()

            if field == "password":
                validated_data[field] = value
            elif field in ("first_name", "last_name"):
                validated_data[field] = value.title()
            else:
                validated_data[field] = value.lower()

        return super().to_internal_value(validated_data)

    @transaction.atomic
    def create(self, validated_data):
        """Creates the User, NB: Password validation happens on the model level"""
        user = User.objects.create_user(**validated_data)
        transaction.on_commit(lambda: self.complete_account_signup(user))
        return user

    def complete_account_signup(self, user: User):
        # Automatically verify email and make user active
        user.is_email_verified = True
        user.is_active = True
        user.save()
        user.send_welcome_email()


class AccountSignupSerializer(BaseSignupSerializer):
    class Meta(BaseSignupSerializer.Meta):
        model = User
        fields = BaseSignupSerializer.Meta.fields

    def to_representation(self, instance):
        return AuthSerializer(instance).data


class AccountLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=True)

    email_validator = EmailValidator()

    def use_django_email_validator(self, value):
        try:
            self.email_validator(value)
            return True
        except ValidationError:
            return False

    def to_internal_value(self, data):
        try:
            data = data.copy()
            if email := data.get("email", "").strip():
                try:
                    self.email_validator(email)
                except ValidationError:
                    pass
        except Exception as e:
            logger.exception(f"Invalid email: {data} - {type(e).__name__}: {e}")
        return super().to_internal_value(data)

    def perform_authentication(self, request):
        user = authenticate(**self.validated_data, request=request)
        if user is None:
            raise serializers.ValidationError(
                "Invalid credentials. Please check your email and password."
            )
        self.instance = user
        return user

    def to_representation(self, instance):
        # Get the user from self.instance if instance is not a User object
        if not hasattr(instance, 'is_email_verified'):
            user = self.instance
        else:
            user = instance
            
        # Auto-verify user on login if not already verified
        if hasattr(user, 'is_email_verified') and not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
            
        return AuthSerializer(user).data


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(
        write_only=True, source="email_verification_token", required=True
    )

    class Meta:
        model = User
        fields = ["token", "is_email_verified"]
        extra_kwargs = {
            "is_email_verified": {"read_only": True},
        }

    def validate_token(self, value):
        is_valid = self.instance.is_email_token_valid(value)
        if not is_valid:
            raise TokenInvalidException()
        self.instance.token_is_validated = True
        return value

    @transaction.atomic
    def update(self, instance: User, validated_data) -> User:
        instance.perform_email_verification()
        return instance


class ResendEmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_email_verified"]

    def resend_email_verification(self):
        self.instance.send_verification_email()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def request_password_token(self):
        """Trigger password reset email."""
        try:
            user = User.objects.get(email=self.validated_data["email"])
            user.send_reset_password_email()
        except User.DoesNotExist:
            pass


class PasswordTokenValidationSerializer(serializers.Serializer):
    forgot_password_token = serializers.CharField(write_only=True, required=False)

    def validate_forgot_password_token(self, value: str):
        if not self.instance.validate_forgot_password_reset_token():
            raise TokenInvalidException()
        return value

    def update(self, instance: User, validated_data):
        return instance


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    forgot_password_token = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["forgot_password_token", "password"]

    def validate(self, data):
        validate_password(data["password"])
        return data

    def update(self, instance: User, validated_data):
        instance.reset_password(validated_data["password"])
        return instance


class AccountProfileSerializer(BaseManyToManyNestedSerializer):
    """
    A serializer for a user's account profile
    """

    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "address",
            "country",
            "state",
            "avatar",
            "is_email_verified",
        ]
        extra_kwargs = {
            "is_email_verified": {"read_only": True},
        }


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["password", "old_password"]

    def validate_old_password(self, value):
        self.instance.validate_old_password(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def update(self, instance: User, validated_data):
        instance.update_password(validated_data["password"])
        return instance



