from utils.factories import UserFactory
from utils.helpers import TestCaseHelper
import pytest
from django.urls import reverse
from rest_framework import status

from accounts.serializers import AccountSignupSerializer

login_url = "/api/v1/accounts/auth/login/"
logout_url = "/api/v1/accounts/auth/logout/"
signup = "/api/v1/accounts/signup/"
profile_url = "/api/v1/accounts/profile/"



class TestUserAuth(TestCaseHelper):
    """
    This class contains test cases for user login functionality.
    """

    valid_password = "A.ValidPassword2"

    def test_user_can_login(self):
        """
        Test case to verify that a user can log in successfully.
        """
        user = UserFactory.create(verified=True)
        user.set_password(self.valid_password)
        user.save()
        response = self.client.post(
            login_url,
            data={"email": user.email, "password": self.valid_password},
        )
        assert "access" in response.data
        assert "refresh" in response.data
        assert "is_email_verified" in response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_cannot_login_with_wrong_password(self):
        """
        Test case to verify that a user cannot log in with incorrect password.
        """
        user = UserFactory.create(verified=True)
        user.set_password(self.valid_password)
        user.save()
        response = self.client.post(
            login_url, data={"email": user.email, "password": "XXXXX_password"}
        )
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_login_with_wrong_email(self):
        """
        Test case to verify that a user cannot log in with an incorrect email.
        """
        user = UserFactory.create(verified=True)
        user.set_password(self.valid_password)
        user.save()
        response = self.client.post(
            login_url,
            data={"email": "test@example.com", "password": self.valid_password},
        )
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_logout(self):
        """
        Test case to verify that an authenticated user can log out.
        """
        user = UserFactory.create(verified=True)
        user.set_password(self.valid_password)
        user.save()
        self.authenticate_user(user)
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.client.logout()


class TestSignupPasswordValidation(TestCaseHelper):
    def test_signup_with_invalidated_password_min_length(self, client):
        """Test a user can not signup with less than min password"""
        data = self.get_test_data(
            serializer=AccountSignupSerializer,
            factory_class=UserFactory,
            traits={
                "is_build": True,
                "is_email_verified": True,
            },
        )
        data["password"] = "pass"
        response = client.post(signup, data=data)
        self.assertEqual(response.status_code, 400)

    def test_signup_with_invalidated_password_no_uppercase(self, client):
        """Test a user can not signup with no uppercase password"""
        data = self.get_test_data(
            serializer=AccountSignupSerializer,
            factory_class=UserFactory,
            traits={"is_email_verified": True, "is_build": True},
        )
        data["password"] = "securepassword123@."
        response = client.post(signup, data=data)
        self.assertEqual(response.status_code, 400)

    def test_signup_with_invalidated_password_all_uppercase(self, client):
        """Test a user can not signup with all uppercase password"""
        data = self.get_test_data(
            serializer=AccountSignupSerializer,
            factory_class=UserFactory,
            traits={"is_email_verified": True, "is_build": True},
        )
        data["password"] = "SECUREPASSWORD123@."
        response = client.post(signup, data=data)
        self.assertEqual(response.status_code, 400)

    def test_signup_with_invalidated_password_no_number(self, client):
        """Test a user can not signup with no number password"""
        data = self.get_test_data(
            serializer=AccountSignupSerializer,
            factory_class=UserFactory,
            traits={"is_email_verified": True, "is_build": True},
        )
        data["password"] = "Securepassword@."
        response = client.post(signup, data=data)
        self.assertEqual(response.status_code, 400)

    def test_signup_with_invalidated_password_no_special_character(self, client):
        """Test a user can not signup with no special character password"""
        data = self.get_test_data(
            serializer=AccountSignupSerializer,
            factory_class=UserFactory,
            traits={"is_email_verified": True, "is_build": True},
        )
        data["password"] = "Securepassword1"
        response = client.post(signup, data=data)
        self.assertEqual(response.status_code, 400)


class TestProfile(TestCaseHelper):
    def test_profile_get(self, test_user):
        client = self.get_authenticated_client(test_user)
        response = client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], test_user.email)

    def test_profile_update(self, test_user):
        client = self.get_authenticated_client(test_user)
        response = client.patch(profile_url, {"first_name": "NewName"})
        self.assertEqual(response.status_code, 200)
        test_user.refresh_from_db()
        self.assertEqual(test_user.first_name, "NewName")
