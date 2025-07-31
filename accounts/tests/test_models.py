"""
Tests for accounts models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import User
from django.db import IntegrityError
from pydantic import ValidationError
from utils.exceptions import (
    TokenInvalidException,
    PasswordErrorException,
    PreconditionException,
)
from utils.factories import (
    UserFactory,
)
from utils.helpers import TestCaseHelper


@pytest.mark.django_db
class TestUserDBModel(TestCaseHelper):
    def test_user_model_creation(self):
        """Test User model works"""
        user = User.objects.create_user(
            email="johndoe@example.com",
            password="A.ValidPassword25",
            first_name="John",
            last_name="Doe",
            gender="male",
        )
        self.assertEqual(user.email, "johndoe@example.com")
        self.assertTrue(user.check_password("A.ValidPassword25"))

    def test_invalid_email_exception_raises_pydantic_validation_error(self):
        """Test invalid email raises pydantic validation error"""
        with pytest.raises(ValidationError):
            User.objects.create_user(
                email="johndoeexample.com",
                password="XXXXXXXXXXXXXXXXX",
                first_name="John",
                last_name="Doe",
                gender="male",
            )

    def test_normalized_email_is_saved(self):
        """Test normalized email is saved"""
        user = User.objects.create_user(
            email="johndoe@examPle.com",
            password="XXXXXXXXXXXXXXXXX",
            first_name="John",
            last_name="Doe",
            gender="male",
        )

        self.assertEqual(user.email, "johndoe@example.com")

    def test_email_is_required_field(self):
        """Test email is a required field"""
        with pytest.raises(ValidationError):
            User.objects.create_user(
                email="",
                password="XXXXXXXXXXXXXXXXX",
                first_name="John",
                last_name="Doe",
                gender="male",
            )

    def test_emails_are_unique(self):
        """Test emails are unique"""
        User.objects.create_user(
            email="johndoe@example.com",
            password="XXXXXXXXXXXXXXXXX",
            first_name="John",
            last_name="Doe",
            gender="male",
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="johndoe@example.com",
                password="XXXXXXXXXXXXXXXXX",
                first_name="John",
                last_name="Doe",
                gender="male",
            )

    def test_generate_verification_token(self):
        """Test sending verification email"""
        user = User.objects.create_user(
            email="johndoe@example.com",
            password="XXXXXXXXXXXXXXXXX",
            first_name="John",
            last_name="Doe",
            gender="male",
        )
        user._generate_and_save_verification_token()
        self.assertTrue(user.email_verification_token is not None)
        self.assertTrue(user.email_verification_token_expires_at is not None)

    def test_verify_email(self, email_mocker):
        """Test verifying email with valid token"""
        user = User.objects.create_user(
            email="johndoe@example.com",
            password="XXXXXXXXXXXXXXXXX",
            first_name="John",
            last_name="Doe",
            gender="male",
        )
        user.send_verification_email()
        user.refresh_from_db()

        token = user.email_verification_token
        user.is_email_token_valid(token)
        user.token_is_validated = True
        user.perform_email_verification()

        self.assertTrue(user.is_email_verified)
        self.assertEqual(user.email_verification_token, None)
        self.assertEqual(user.email_verification_token_expires_at, None)

        assert email_mocker.call_count == 1


class TestPasswordResetTokenModel(TestCaseHelper):
    def test_generate_unique_token(self, user_with_password):
        token = user_with_password.generate_unique_token(token_for="forgot_password")
        self.assertEqual(len(token), 6)
        self.assertFalse(User.objects.filter(forgot_password_token=token).exists())

    def test_generate_forgot_password_reset_token_creates_token(
        self, user_with_password
    ):
        user_with_password.generate_forgot_password_reset_token()
        self.assertTrue(user_with_password.forgot_password_token is not None)

    def test_validate_reset_token_success(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        self.assertTrue(user_with_password.validate_forgot_password_reset_token())

    def test_validate_reset_token_failure(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        user_with_password.forgot_password_token_expires_at = (
            timezone.now() - timezone.timedelta(minutes=30)
        )
        user_with_password.save()
        print(user_with_password.forgot_password_token_expires_at)
        print(timezone.now())
        print(user_with_password.forgot_password_token_expires_at > timezone.now())
        print(user_with_password.forgot_password_token)
        with pytest.raises(TokenInvalidException):
            user_with_password.validate_forgot_password_reset_token()

    def test_reset_password_success(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        new_password = "NewValidPassword123!@"
        user_with_password.validate_forgot_password_reset_token()
        user_with_password.forgot_password_token_is_validated = True
        user_with_password.reset_password(new_password)

        user_with_password.refresh_from_db()
        self.assertTrue(user_with_password.check_password(new_password))

    def test_validate_old_password_success(self, user_with_password):
        """Test validate_old_password method works correctly"""
        user_with_password.validate_old_password("OldValidPassword123")
        self.assertTrue(hasattr(user_with_password, "password_validated"))

    def test_validate_old_password_failure(self, user_with_password):
        """Test validate_old_password raises exception for incorrect password"""
        with pytest.raises(PasswordErrorException):
            user_with_password.validate_old_password("WrongPassword123")

    def test_update_password_success(self, user_with_password):
        """Test update_password method works correctly after validation"""
        user_with_password.validate_old_password("OldValidPassword123")
        user_with_password.update_password("NewValidPassword123")
        user_with_password.refresh_from_db()
        self.assertTrue(user_with_password.check_password("NewValidPassword123"))
