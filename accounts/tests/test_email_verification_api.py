# Test file for email verification API
from django.contrib.auth import get_user_model
from utils.factories import UserFactory
from utils.helpers import TestCaseHelper

User = get_user_model()
base_email_url = "/api/v1/accounts/verifications/"
verify_email_url = base_email_url + "email/"
resend_verification_url = base_email_url + "resend-email-token/"


class TestEmailVerificationAPI(TestCaseHelper):
    def get_user(self):
        user = UserFactory.create()
        user.set_password("valid_password")
        user._generate_and_save_verification_token()
        user.save()
        return user

    def test_verify_email_success(self, email_mocker):
        """Test a user can verify their email successfully"""
        user = self.get_user()
        self.authenticate_user(user)
        data = {"token": user.email_verification_token}
        response = self.client.post(verify_email_url, data=data)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.client.logout()

    def test_verify_email_invalid_token(self):
        """Test a user cannot verify their email with an invalid token"""
        user = self.get_user()
        self.authenticate_user(user)
        data = {
            "token": "invalid_token",
        }
        response = self.client.post(verify_email_url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user.is_email_verified)
        self.client.logout()

    def test_email_verification_with_expired_token_returns_bad_request(self):
        """Test a user cannot verify their email with an expired token"""
        user = self.get_user()
        self.authenticate_user(user)
        user._generate_and_save_verification_token()
        user.email_verification_token_expires_at = user._get_email_token_expiration(-30)
        user.save()
        data = {
            "token": user.email_verification_token,
        }
        response = self.client.post(verify_email_url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user.is_email_verified)
        self.client.logout()

    def test_resend_verification_email_success(self, email_mocker):
        """Test a user can request to resend the verification email"""
        user = self.get_user()
        self.authenticate_user(user)
        response = self.client.post(resend_verification_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_resend_verification_unauth_user(self):
        """Test a user cannot request to resend verification email for an invalid email"""
        response = self.client.post(resend_verification_url)
        self.assertEqual(response.status_code, 401)
