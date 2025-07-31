"""
Helper utilities for the Django Project Template.
"""

import logging
import secrets
from collections import defaultdict
from typing import Dict

import factory
import pendulum
import pytest
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from storages.backends.s3 import S3Storage

logger = logging.getLogger(__name__)


@pytest.mark.django_db(transaction=True)
class TestCaseHelper:
    """Helper class for test cases."""

    client = APIClient()
    api_version = settings.REST_FRAMEWORK["DEFAULT_VERSION"]
    password = "A.ValidPassword25"

    def authenticate_user(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def assert_response_status(self, response, status_code):
        """Assert response status code."""
        assert response.status_code == status_code, response.content

    def assert_response_data(self, response, expected_data):
        """Assert response data matches expected data."""
        assert response.data == expected_data, response.data

    def assert_response_errors(self, response, expected_errors):
        """Assert response errors match expected errors."""
        assert response.data["errors"] == expected_errors, response.data["errors"]

    def assert_response_error_message(self, response, expected_error_message):
        """Assert response error message matches expected message."""
        assert (
            response.data["errors"][0]["message"] == expected_error_message
        ), response.data["errors"][0]["message"]

    def assertEqual(self, actual, expected):
        """Assert two values are equal."""
        assert actual == expected, f"{actual} != {expected}"

    def assertNotEqual(self, actual, expected):
        """Assert two values are not equal."""
        assert actual != expected, f"{actual} == {expected}"

    def assertCreated(self, response):
        """Assert response status is 201 Created."""
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"{response.status_code} != {status.HTTP_201_CREATED} -> {response.data}"

    def assertOk(self, response):
        """Assert response status is 200 OK."""
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"{response.status_code} != {status.HTTP_200_OK} -> {response.data}"

    def assertBadRequest(self, response):
        """Assert response status is 400 Bad Request."""
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f"{response.status_code} != {status.HTTP_400_BAD_REQUEST} -> {response.data}"

    def assertPermissionDenied(self, response):
        """Assert response status is 403 Forbidden."""
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), f"{response.status_code} != {status.HTTP_403_FORBIDDEN} -> {response.data}"

    def assertNoContent(self, response):
        """Assert response status is 204 No Content."""
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), f"{response.status_code} != {status.HTTP_204_NO_CONTENT} -> {response.data}"

    def assertTrue(self, actual):
        """Assert value is True."""
        assert actual, f"{actual} is not True"

    def assertFalse(self, actual):
        """Assert value is False."""
        assert not actual, f"{actual} is not False"

    def assertIn(self, key, container):
        """Assert key is in container."""
        assert key in container, f"{key} not in {container}"

    def assertNone(self, actual):
        """Assert value is None."""
        assert actual is None, f"{actual} is not None"

    def assertNotNone(self, actual):
        """Assert value is not None."""
        assert actual is not None, f"{actual} is None"

    @staticmethod
    def get_test_data(
        serializer,
        factory_class,
        set_specific_field={},
        traits={},
        raise_exception=True,
    ):
        """Get test data from the factory."""
        try:
            data = factory.build(dict, FACTORY_CLASS=factory_class, **traits)
            data.update(set_specific_field)
            serializer = serializer(data=data)
            serializer.is_valid(raise_exception=raise_exception)
        except Exception as e:
            logger.exception(f"An exception occurred while generating test data: {e}")
            raise e
        remove_null_values = lambda data: {
            key: value for key, value in data.items() if value is not None
        }
        return remove_null_values(serializer.validated_data)

    @staticmethod
    def remove_unwanted_fields(data, fields_to_remove):
        return {
            key: value for key, value in data.items() if key not in fields_to_remove
        }

    @staticmethod
    def remove_unwanted_field_batch(data_arr, fields_to_remove):
        return [
            {key: value for key, value in data.items() if key not in fields_to_remove}
            for data in data_arr
        ]

    @staticmethod
    def get_test_data_batch(serializer, factory_class, traits={}, size=1):
        """Get test data batch from the factory."""
        try:
            data = factory.build_batch(
                dict, size, FACTORY_CLASS=factory_class, **traits
            )
            serializer = serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.exception(f"An exception occurred while generating test data: {e}")
            raise e
        remove_null_values = lambda data: {
            key: value for key, value in data.items() if value is not None
        }
        return [remove_null_values(d) for d in serializer.validated_data]

    def get_authenticated_client(self, user) -> APIClient:
        """Get authenticated API client."""
        refresh = RefreshToken.for_user(user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
        return client


def parse_querydict(querydict: dict) -> dict:
    """Parse a querydict with lists into a dictionary."""
    parsed_data = defaultdict(list)
    for key, value in querydict.items():
        if "[" in key and "]" in key:
            main_key, remainder = key.split("[", 1)
            index, sub_key = remainder.split("]", 1)
            sub_key = sub_key.strip("[").strip("]")
            try:
                index = int(index)
            except ValueError:
                index = None

            try:
                if main_key not in parsed_data:
                    parsed_data[main_key] = []
                if index is not None:
                    parsed_data[main_key][index] |= {sub_key: value}
            except IndexError:
                parsed_data[main_key].append({sub_key: value} if sub_key else value)
        else:
            parsed_data[key] = value
    return parsed_data


def normalize_email(email: str):
    """Normalize the email address by lowercasing the domain part."""
    email = email or ""
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
    except ValueError:
        pass
    else:
        email = email_name + "@" + domain_part.lower()
    return email


def default_daily_availability():
    """Get default daily availability."""
    return {
        day: True
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
    }


def get_date_quarter(date: pendulum.DateTime) -> Dict[str, pendulum.DateTime]:
    """Returns the quarter of the year for the given date."""
    current_quarter = (date.month - 1) // 3 + 1
    first_month_of_quarter = (current_quarter - 1) * 3 + 1
    return {
        "start": date.set(month=first_month_of_quarter).start_of("month"),
        "end": date.set(month=first_month_of_quarter + 2).end_of("month"),
    }


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class S3BucketConfig(S3Storage):
    """Custom S3 storage configuration."""

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
