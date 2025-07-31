from typing import List

from django.db.models import Model
from utils.emails import BaseEmail
from utils.formatters import get_formatted_durations


class AccountVerificationEmail(BaseEmail):
    """Generates email context for account verification"""

    @property
    def subject(self):
        return "Verify Your Email Address"

    @property
    def template_name(self):
        return "emails/accounts/emailVerification.html"

    @property
    def to_email(self):
        return [self.instance.email]

    @property
    def context(self):
        user = self.instance
        return {
            "token": user.email_verification_token,
            "duration": get_formatted_durations(
                user.email_verification_token_expires_at
            ),
        }


class AccountWelcomeEmail(BaseEmail):
    """Generates email context for account welcome"""

    @property
    def subject(self):
        return "Welcome to Our Platform"

    @property
    def template_name(self):
        return "emails/accounts/welcomeEmail.html"

    @property
    def to_email(self):
        return [self.instance.email]

    def _get_login_url(self):
        return "/api/v1/accounts/auth/login/"

    @property
    def context(self):
        return {
            "first_name": self.instance.first_name,
            "user_login_url": self._get_login_url(),
        }


class PasswordResetEmail(BaseEmail):
    """Generates email context for password reset"""

    @property
    def subject(self):
        return "Reset Your Password"

    @property
    def template_name(self):
        return "emails/accounts/password_reset.html"

    @property
    def to_email(self):
        return [self.instance.email]

    @property
    def context(self):
        return {
            "first_name": self.instance.first_name,
            "reset_token": self.instance.forgot_password_token,
        }


class SharePasswordEmail(BaseEmail):
    """Generates email context for sharing password"""

    def __init__(self, instance: Model, password: str):
        super().__init__(instance)
        self.new_password = password

    @property
    def subject(self):
        return "An Account Was Set Up for You"

    @property
    def template_name(self):
        return "emails/accounts/share_password.html"

    @property
    def to_email(self):
        return [self.instance.email]

    @property
    def context(self):
        return {
            "first_name": self.instance.first_name or "There",
            "password": self.new_password,
        }
