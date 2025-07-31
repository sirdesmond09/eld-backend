"""
Tests for ELD API endpoints.
"""

from datetime import date
from decimal import Decimal
from core.models import Trip, Route, LogEntry
from django.urls import reverse
from rest_framework import status
from utils.factories import TripFactory, UserFactory
from utils.helpers import TestCaseHelper

# URL patterns for ELD API
trip_list_url = "/api/v1/eld/trips/"
trip_detail_url = "/api/v1/eld/trips/{}/"
trip_plan_url = "/api/v1/eld/trips/plan_trip/"
trip_generate_logs_url = "/api/v1/eld/trips/{}/generate_logs/"
log_entry_list_url = "/api/v1/eld/log-entries/"
log_entry_detail_url = "/api/v1/eld/log-entries/{}/"
route_list_url = "/api/v1/eld/routes/"
route_detail_url = "/api/v1/eld/routes/{}/"


class TestTripAPI(TestCaseHelper):
    """Test Trip API endpoints"""

    def test_trip_list_authenticated_user(self, test_driver, test_trip):
        """Test authenticated user can list their trips"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(trip_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uid"], str(test_trip.uid))

    def test_trip_list_unauthenticated_user(self):
        """Test unauthenticated user cannot access trip list"""
        response = self.client.get(trip_list_url)
        self.assertEqual(response.status_code, 401)

    def test_trip_create_authenticated_user(self, test_driver):
        """Test authenticated user can create a trip"""
        trip_data = {
            "current_location": "New York, NY",
            "pickup_location": "Boston, MA",
            "dropoff_location": "Philadelphia, PA",
            "current_cycle_used": "25.50",
        }

        client = self.get_authenticated_client(test_driver)
        response = client.post(trip_list_url, data=trip_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["current_location"], "New York, NY")
        self.assertEqual(response.data["pickup_location"], "Boston, MA")

    def test_trip_create_invalid_data(self, test_driver):
        """Test trip creation with invalid data"""
        invalid_data = {
            "current_location": "",  # Empty location
            "pickup_location": "Boston, MA",
            "dropoff_location": "Philadelphia, PA",
            "current_cycle_used": "75.00",  # Exceeds max
        }

        client = self.get_authenticated_client(test_driver)
        response = client.post(trip_list_url, data=invalid_data)

        self.assertEqual(response.status_code, 400)

    def test_trip_detail_authenticated_user(self, test_driver, test_trip):
        """Test authenticated user can view trip details"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(trip_detail_url.format(test_trip.uid))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uid"], str(test_trip.uid))

    def test_trip_update_authenticated_user(self, test_driver, test_trip):
        """Test authenticated user can update their trip"""
        update_data = {"current_location": "Updated Location", "status": "in_progress"}

        client = self.get_authenticated_client(test_driver)
        response = client.patch(trip_detail_url.format(test_trip.uid), data=update_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["current_location"], "Updated Location")

    def test_trip_delete_authenticated_user(self, test_driver, test_trip):
        """Test authenticated user can delete their trip"""
        client = self.get_authenticated_client(test_driver)
        response = client.delete(trip_detail_url.format(test_trip.uid))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Trip.objects.filter(uid=test_trip.uid).exists())

    def test_user_can_only_access_own_trips(self, test_driver):
        """Test user can only access their own trips"""
        # Create another user and their trip
        other_user = UserFactory.create(verified=True)
        other_trip = TripFactory.create(driver=other_user)

        # Current user's trip
        my_trip = TripFactory.create(driver=test_driver)

        client = self.get_authenticated_client(test_driver)
        response = client.get(trip_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uid"], str(my_trip.uid))

        # Try to access other user's trip
        response = client.get(trip_detail_url.format(other_trip.uid))
        self.assertEqual(response.status_code, 404)


class TestTripPlanningAPI(TestCaseHelper):
    """Test trip planning functionality"""

    def test_plan_trip_success(self, test_driver):
        """Test successful trip planning"""
        plan_data = {
            "current_location": "New York, NY",
            "pickup_location": "Boston, MA",
            "dropoff_location": "Philadelphia, PA",
            "current_cycle_used": "25.50",
            "driver_name": "John Doe",
            "carrier_name": "ABC Trucking",
        }

        client = self.get_authenticated_client(test_driver)
        response = client.post(trip_plan_url, data=plan_data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("uid", response.data)
        self.assertEqual(response.data["current_location"], "New York, NY")

    def test_plan_trip_unauthenticated_user(self):
        """Test unauthenticated user cannot plan trip"""
        plan_data = {
            "current_location": "New York, NY",
            "pickup_location": "Boston, MA",
            "dropoff_location": "Philadelphia, PA",
            "current_cycle_used": "25.50",
        }

        response = self.client.post(trip_plan_url, data=plan_data)
        self.assertEqual(response.status_code, 401)


class TestLogGenerationAPI(TestCaseHelper):
    """Test log generation functionality"""

    def test_generate_logs_success(self, test_driver):
        """Test successful log generation"""
        # Create a trip with estimated_duration (required for log generation)
        trip = TripFactory.create(
            driver=test_driver,
            estimated_duration=Decimal("15.00"),
            estimated_distance=Decimal("750.00"),
        )

        generate_data = {
            "start_date": date.today().isoformat(),
            "driver_name": "John Doe",
            "carrier_name": "ABC Trucking",
        }

        client = self.get_authenticated_client(test_driver)
        response = client.post(
            trip_generate_logs_url.format(trip.uid), data=generate_data
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(isinstance(response.data, list))

    def test_generate_logs_invalid_trip(self, test_driver):
        """Test log generation for unauthorized trip"""
        other_user = UserFactory.create(verified=True)
        other_trip = TripFactory.create(driver=other_user)

        generate_data = {"start_date": date.today().isoformat()}

        client = self.get_authenticated_client(test_driver)
        response = client.post(
            trip_generate_logs_url.format(other_trip.uid), data=generate_data
        )

        self.assertEqual(response.status_code, 404)


class TestLogEntryAPI(TestCaseHelper):
    """Test LogEntry API endpoints"""

    def test_log_entry_list_authenticated_user(self, test_driver, test_log_entry):
        """Test authenticated user can list their log entries"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(log_entry_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uid"], str(test_log_entry.uid))

    def test_log_entry_detail_authenticated_user(self, test_driver, test_log_entry):
        """Test authenticated user can view log entry details"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(log_entry_detail_url.format(test_log_entry.uid))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uid"], str(test_log_entry.uid))


class TestRouteAPI(TestCaseHelper):
    """Test Route API endpoints"""

    def test_route_list_authenticated_user(self, test_driver, test_route):
        """Test authenticated user can list their routes"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(route_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uid"], str(test_route.uid))

    def test_route_detail_authenticated_user(self, test_driver, test_route):
        """Test authenticated user can view route details"""
        client = self.get_authenticated_client(test_driver)
        response = client.get(route_detail_url.format(test_route.uid))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uid"], str(test_route.uid))
