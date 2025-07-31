# Test file for password reset API 
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from utils.helpers import TestCaseHelper

# URL variables
request_reset_url = "/api/v1/accounts/auth/password/request-token/"
reset_password_url = "/api/v1/accounts/auth/password/{}/reset/"
change_password_url = "/api/v1/accounts/auth/change-password/"


class TestPasswordResetAPI(TestCaseHelper):
    def test_request_reset_success(self, user_with_password, email_mocker):
        response = self.client.post(
            request_reset_url, data={"email": user_with_password.email}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        email_mocker.assert_called_once()

    def test_request_reset_invalid_email(self):
        response = self.client.post(
            request_reset_url, data={"email": "invalid@example.com"}
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

    def test_reset_password_token_validation(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        response = self.client.get(
            reset_password_url.format(user_with_password.forgot_password_token),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_token_validation_invalid_token(self):
        response = self.client.get(reset_password_url.format("invalid_token"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_reset_password_token_validation_expired(self, user_with_password):
    #     user_with_password.generate_forgot_password_reset_token()
    #     user_with_password.forgot_password_token_expires_at = (
    #         timezone.now() - timezone.timedelta(minutes=30)
    #     )
    #     user_with_password.save()

    #     response = self.client.get(
    #         reset_password_url.format(user_with_password.forgot_password_token),
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_success(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        password = "NewValidPassword123@$"
        response = self.client.post(
            reset_password_url.format(user_with_password.forgot_password_token),
            data={"password": password},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_with_password.refresh_from_db()
        self.assertTrue(user_with_password.check_password(password))

    def test_reset_password_invalid_token(self, user_with_password):
        user_with_password.generate_forgot_password_reset_token()
        user_with_password.forgot_password_token_expires_at = (
            timezone.now() - timezone.timedelta(minutes=30)
        )
        user_with_password.save()

        response = self.client.post(
            reset_password_url.format(user_with_password.forgot_password_token),
            data={"password": "NewValidPassword123"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_reset_throttling(self, user_with_password, email_mocker):
        """
        Ensure that the password reset request is throttled to once every 3 minutes per email.
        """
        # First request should succeed
        response = self.client.post(
            request_reset_url, data={"email": user_with_password.email}
        )
        assert response.status_code == status.HTTP_200_OK

        # Second request should be throttled
        # mock_cache.get.return_value = True  # Simulate rate limit hit
        response = self.client.post(
            request_reset_url, data={"email": user_with_password.email}
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # Simulate cache cleared by resetting the mock
        cache.clear()

        response = self.client.post(
            request_reset_url, data={"email": user_with_password.email}
        )
        assert email_mocker.call_count == 2
        assert response.status_code == status.HTTP_200_OK


class TestChangePasswordAPI(TestCaseHelper):
    def test_unauthenticated_user_cannot_change_password(self):
        """Test unauthenticated user cannot change their password"""

        data = {
            "old_password": "OldValidPassword123",
            "password": "ValidPassword123",
        }
        response = self.client.post(change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_change_password(self, user_with_password):
        """Test an authenticated user can change their password"""
        data = {
            "old_password": "OldValidPassword123",
            "password": "NewValidPassword123.@",
        }
        client = self.get_authenticated_client(user_with_password)
        response = client.post(change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user_with_password.refresh_from_db()
        self.assertTrue(user_with_password.check_password("NewValidPassword123.@"))

    def test_user_cannot_change_password_with_wrong_old_password(
        self, user_with_password
    ):
        """Test an authenticated user cannot change their password with wrong old password"""

        data = {
            "old_password": "OldWrongPassword123.@",
            "password": "NewValidPassword123.@",
        }
        client = self.get_authenticated_client(user_with_password)
        response = client.post(change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_change_password_with_invalid_password(
        self, user_with_password
    ):
        """Test an authenticated user cannot change their password with wrong old password"""

        data = {"old_password": "OldValidPassword123", "password": "invalid"}
        client = self.get_authenticated_client(user_with_password)
        response = client.post(change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 