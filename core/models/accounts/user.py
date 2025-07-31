"""
Custom User model for the Django Project Template.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import secrets
from typing import Union
from django.utils.functional import cached_property
from accounts.emails import (
    AccountVerificationEmail,
    AccountWelcomeEmail,
    SharePasswordEmail,
    PasswordResetEmail,
)
from core.choices import Gender
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils import timezone
from pydantic import EmailStr, validate_call
from utils.generators import generate_random_password
from ..base import TimeStampUUIDModel, TimeStampModel
from utils.exceptions import PasswordErrorException, TokenInvalidException


class UserManager(DjangoUserManager):

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def create_user(
        self,
        email: EmailStr,
        password: Union[str, None] = None,
        **extra_fields,
    ):
        """
        Create and save a user with the given email and password.
        """
        user = User(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    @validate_call
    def admin_create_user(self, email: EmailStr, **extra_fields):
        password = generate_random_password()
        user = User(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user, password

    def active_users(self):
        return super().get_queryset().filter(is_active=True)


class User(TimeStampUUIDModel, AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    """

    username = None
    email = models.EmailField(
        _("User's email"),
        unique=True,
        error_messages={"unique": "The provided email is not available"},
    )

    is_email_verified = models.BooleanField(_("Is user email verified"), default=False)

    email_verification_token = models.CharField(
        _("Email verification token"), max_length=7, blank=True, null=True
    )
    email_verification_token_expires_at = models.DateTimeField(
        _("Email verification token expires at"), blank=True, null=True
    )

    email_last_updated_at = models.DateTimeField(null=True, blank=True)

    # forgot password
    forgot_password_token = models.CharField(max_length=6, unique=True, null=True)
    forgot_password_token_expires_at = models.DateTimeField(null=True, blank=True)

    # Profile fields
    first_name = models.CharField(
        _("First name"), max_length=255, blank=True, null=True
    )
    last_name = models.CharField(_("Last name"), max_length=255, blank=True, null=True)

    gender = models.CharField(
        _("Gender"),
        max_length=255,
        blank=True,
        null=True,
        choices=Gender.choices,
    )

    address = models.TextField(_("Address"), blank=True, null=True)
    country = models.CharField(_("Country"), max_length=255, blank=True, null=True)
    state = models.CharField(_("State"), max_length=255, blank=True, null=True)

    avatar = models.ImageField(upload_to="profiles/avatars", blank=True, null=True)

    phone_number = models.CharField(
        _("User's Phone number"), max_length=25, blank=True, null=True, unique=True
    )
    is_phone_verified = models.BooleanField(_("Is user phone verified"), default=False)

    phone_verification_token = models.CharField(
        _("Phone verification token"), max_length=7, blank=True, null=True
    )
    phone_verification_token_expires_at = models.DateTimeField(
        _("Phone verification token expires at"), blank=True, null=True
    )

    is_two_factor_enabled = models.BooleanField(_("Is 2FA enabled"), default=False)
    two_factor_auth_secret = models.CharField(
        _("2FA secret"), max_length=255, blank=True, null=True
    )

    date_of_birth = models.DateField(_("Date of birth"), blank=True, null=True)
    marital_status = models.CharField(
        _("Marital status"),
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ("single", _("Single")),
            ("married", _("Married")),
            ("divorced", _("Divorced")),
            ("widowed", _("Widowed")),
        ],
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=["email", "avatar"]),
            models.Index(fields=["email"]),
            models.Index(fields=["email_verification_token"]),
            models.Index(fields=["forgot_password_token"]),
        ]
        ordering = ["created_at"]

    # properties

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @cached_property
    def get_avatar_url(self) -> str:
        if self.avatar:
            return self.avatar.url
        return None



    def _get_email_token_expiration(self, duration: int = 30):
        """
        Get the expiration time for the email verification token.
        Args:
            duration (int): The duration in minutes for which the token is valid. Defaults to 30 minutes.
        Returns:
            datetime: The expiration time for the email verification token.
        """
        return timezone.now() + timedelta(minutes=duration)

    def _generate_and_save_verification_token(self):
        token = self.generate_unique_token(token_for="email_verification")
        self.email_verification_token = token
        self.email_verification_token_expires_at = self._get_email_token_expiration(30)
        self.save()

    def _generate_token(self) -> str:
        """Generate a random 6-digit token."""
        return str(secrets.randbelow(10**6)).zfill(6)

    def _perform_password_change(self, new_password: str) -> None:
        """Internal method to change the user's password."""
        self.set_password(new_password)
        self.save()

    # Emails
    def _send_verification_email(self):
        AccountVerificationEmail(self).send_email()

    def send_verification_email(self):
        """Send email verification email to user"""
        if self.is_email_verified:
            return
        self._generate_and_save_verification_token()
        self._send_verification_email()

    def send_welcome_email(self):
        """Send welcome email to user"""
        AccountWelcomeEmail(self).send_email()

    def is_email_token_valid(self, token: str):
        return (
            self.email_verification_token == token
            and self.email_verification_token_expires_at > timezone.now()
        )

    def perform_email_verification(self):
        """Verify user's email with given token"""

        self.is_email_verified = True
        self.email_verification_token = self.email_verification_token_expires_at = None
        self.save()

    def generate_forgot_password_reset_token(self) -> None:
        """Generate and set a forgot password reset token with an expiration time."""
        self.forgot_password_token = self.generate_unique_token(
            token_for="forgot_password"
        )
        self.forgot_password_token_expires_at = timezone.now() + timedelta(minutes=30)
        self.save()

    def generate_unique_token(self, token_for, max_attempts=5):
        if token_for == "email_verification":
            for i in range(max_attempts):
                token = self._generate_token()
                if (
                    not User.objects.active_users()
                    .filter(email_verification_token__iexact=token)
                    .exists()
                ):
                    return token
            raise Exception("Failed to generate a unique token after several attempts")

        if token_for == "forgot_password":
            for i in range(max_attempts):
                token = self._generate_token()
                if (
                    not User.objects.active_users()
                    .filter(forgot_password_token=token)
                    .exists()
                ):
                    return token
            raise Exception("Failed to generate a unique token after several attempts")

    def send_reset_password_email(self) -> None:
        """Send password reset email to user"""
        self.generate_forgot_password_reset_token()
        PasswordResetEmail(self).send_email()

    def send_password_to_user(self, password: str):
        """Send password to user via email"""
        SharePasswordEmail(self, password).send_email()

    def validate_forgot_password_reset_token(self) -> bool:
        """Validate the forgot password reset token."""
        if (
            self.forgot_password_token is not None
            and self.forgot_password_token_expires_at > timezone.now()
        ):
            return True
        raise TokenInvalidException()

    def validate_old_password(self, old_password: str) -> None:
        """Validate the old password."""
        if not self.check_password(old_password):
            raise PasswordErrorException("Old password is incorrect")
        self.password_validated = True

    def update_password(self, new_password: str) -> None:
        """Update the user's password."""
        self._perform_password_change(new_password)

    def reset_password(self, new_password: str) -> None:
        """Reset the user's password and clear the reset token."""
        self._perform_password_change(new_password)
        self.forgot_password_token = self.forgot_password_token_expires_at = None
        self.save()

    def get_random_password(self):
        """Get a random password for the user."""
        return generate_random_password()

    def get_short_name(self):
        """Return the short name of the user."""
        return self.first_name or self.username

    @property
    def has_complete_profile(self) -> bool:
        """Check if user has complete profile."""
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]
        return all(getattr(self, field) for field in required_fields)
