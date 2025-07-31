"""
Tests for ELD services business logic.
"""

from datetime import date
from decimal import Decimal
from core.models import Route, LogEntry
from eld.services import TripPlanningService
from utils.factories import TripFactory
from utils.helpers import TestCaseHelper


class TestTripPlanningService(TestCaseHelper):
    """Test trip planning service business logic"""

    def test_plan_trip_creates_trip_and_route(self, test_driver):
        """Test that planning a trip creates both trip and route"""
        trip_data = {
            "driver": test_driver,
            "current_location": "New York, NY",
            "pickup_location": "Boston, MA",
            "dropoff_location": "Philadelphia, PA",
            "current_cycle_used": Decimal("25.50"),
        }

        planning_service = TripPlanningService()
        trip = planning_service.plan_trip(trip_data)

        # Verify trip was created
        self.assertEqual(trip.driver, test_driver)
        self.assertEqual(trip.current_location, "New York, NY")
        self.assertEqual(trip.pickup_location, "Boston, MA")
        self.assertEqual(trip.dropoff_location, "Philadelphia, PA")
        self.assertEqual(trip.status, "planned")

        # Verify route was created
        self.assertTrue(hasattr(trip, "route"))
        self.assertTrue(isinstance(trip.route, Route))

    def test_generate_logs_creates_log_entries(self, test_driver):
        """Test that generating logs creates log entries"""
        trip = TripFactory.create(driver=test_driver, estimated_duration=Decimal("15.00"))
        start_date = date.today()

        planning_service = TripPlanningService()
        log_entries = planning_service.generate_logs(trip, start_date)

        # Verify logs were created
        self.assertTrue(len(log_entries) > 0)
        
        # Verify first log entry
        log_entry = log_entries[0]
        self.assertEqual(log_entry.trip, trip)
        self.assertEqual(log_entry.date, start_date)
        self.assertTrue(isinstance(log_entry, LogEntry))

    def test_long_trip_generates_multiple_logs(self, test_driver):
        """Test that long trips generate multiple daily log entries"""
        trip = TripFactory.create(driver=test_driver, estimated_duration=Decimal("30.00"))
        start_date = date.today()

        planning_service = TripPlanningService()
        log_entries = planning_service.generate_logs(trip, start_date)

        # Long trips should generate multiple log entries
        self.assertTrue(len(log_entries) > 1)
