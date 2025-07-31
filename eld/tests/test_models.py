"""
Tests for ELD models.
"""

import pytest
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Trip, Route, LogEntry, ActivityPeriod
from utils.factories import (
    TripFactory,
    RouteFactory,
    LogEntryFactory,
    ActivityPeriodFactory,
    UserFactory,
)
from utils.helpers import TestCaseHelper


@pytest.mark.django_db
class TestTripModel(TestCaseHelper):
    def test_trip_model_creation(self):
        """Test Trip model creation works"""
        trip = TripFactory.create()
        self.assertNotNone(trip.uid)
        self.assertNotNone(trip.driver)
        self.assertNotNone(trip.current_location)
        self.assertNotNone(trip.pickup_location)
        self.assertNotNone(trip.dropoff_location)
        self.assertNotNone(trip.current_cycle_used)
        self.assertIn(trip.status, ["planned", "in_progress", "completed", "cancelled"])

    def test_trip_total_duration_calculation(self):
        """Test total_duration property calculation"""
        start_time = datetime.now() - timedelta(hours=8)
        end_time = datetime.now()
        
        trip = TripFactory.create(
            start_time=start_time,
            end_time=end_time,
            status="completed"
        )
        
        expected_duration = (end_time - start_time).total_seconds() / 3600
        # Using assertEqual with tolerance for floating point comparison
        self.assertEqual(round(trip.total_duration, 2), 
                        round(expected_duration, 2))

    def test_trip_total_duration_no_times(self):
        """Test total_duration property when no start/end times"""
        trip = TripFactory.create(
            start_time=None,
            end_time=None
        )
        self.assertEqual(trip.total_duration, 0)

    def test_trip_requires_multiple_logs_true(self):
        """Test requires_multiple_logs property for long trips"""
        trip = TripFactory.create(
            estimated_duration=Decimal("30.00")
        )
        self.assertTrue(trip.requires_multiple_logs)

    def test_trip_requires_multiple_logs_false(self):
        """Test requires_multiple_logs property for short trips"""
        trip = TripFactory.create(
            estimated_duration=Decimal("8.00")
        )
        self.assertFalse(trip.requires_multiple_logs)

    def test_trip_requires_multiple_logs_no_estimate(self):
        """Test requires_multiple_logs property when no estimate"""
        trip = TripFactory.create(
            estimated_duration=None
        )
        self.assertFalse(trip.requires_multiple_logs)

    def test_trip_string_representation(self):
        """Test trip string representation"""
        trip = TripFactory.create(
            pickup_location="New York",
            dropoff_location="Boston"
        )
        expected = f"Trip {trip.uid} - New York to Boston"
        self.assertEqual(str(trip), expected)

    def test_trip_current_cycle_used_validation(self):
        """Test current_cycle_used field validation"""
        # Test valid values
        trip = TripFactory.create(current_cycle_used=Decimal("35.50"))
        self.assertEqual(trip.current_cycle_used, Decimal("35.50"))

        # Test maximum value
        trip = TripFactory.create(current_cycle_used=Decimal("70.00"))
        self.assertEqual(trip.current_cycle_used, Decimal("70.00"))

        # Test minimum value
        trip = TripFactory.create(current_cycle_used=Decimal("0.00"))
        self.assertEqual(trip.current_cycle_used, Decimal("0.00"))


@pytest.mark.django_db
class TestRouteModel(TestCaseHelper):
    def test_route_model_creation(self):
        """Test Route model creation works"""
        route = RouteFactory.create()
        self.assertNotNone(route.uid)
        self.assertNotNone(route.trip)
        self.assertNotNone(route.route_data)
        self.assertNotNone(route.rest_stops)
        self.assertNotNone(route.fuel_stops)

    def test_route_string_representation(self):
        """Test route string representation"""
        route = RouteFactory.create()
        expected = f"Route for Trip {route.trip.uid}"
        self.assertEqual(str(route), expected)

    def test_route_one_to_one_with_trip(self):
        """Test route has one-to-one relationship with trip"""
        trip = TripFactory.create()
        RouteFactory.create(trip=trip)
        
        # Second route creation should fail due to one-to-one constraint
        with pytest.raises(IntegrityError):
            RouteFactory.create(trip=trip)


@pytest.mark.django_db
class TestLogEntryModel(TestCaseHelper):
    def test_log_entry_model_creation(self):
        """Test LogEntry model creation works"""
        log_entry = LogEntryFactory.create()
        self.assertNotNone(log_entry.uid)
        self.assertNotNone(log_entry.trip)
        self.assertNotNone(log_entry.date)
        self.assertNotNone(log_entry.start_time)
        self.assertNotNone(log_entry.end_time)
        self.assertNotNone(log_entry.driver_name)
        self.assertNotNone(log_entry.carrier_name)

    def test_log_entry_string_representation(self):
        """Test log entry string representation"""
        log_entry = LogEntryFactory.create()
        expected = f"Log Entry {log_entry.date} - Trip {log_entry.trip.uid}"
        self.assertEqual(str(log_entry), expected)

    def test_log_entry_unique_trip_date_constraint(self):
        """Test unique constraint on trip and date"""
        trip = TripFactory.create()
        date_obj = date.today()
        
        # Create first log entry
        LogEntryFactory.create(trip=trip, date=date_obj)
        
        # Try to create second log entry with same trip and date
        with pytest.raises(IntegrityError):
            LogEntryFactory.create(trip=trip, date=date_obj)

    def test_log_entry_driver_name_auto_population(self):
        """Test driver_name is auto-populated from trip driver"""
        user = UserFactory.create(
            first_name="John",
            last_name="Doe"
        )
        trip = TripFactory.create(driver=user)
        log_entry = LogEntryFactory.create(trip=trip)
        
        self.assertEqual(log_entry.driver_name, "John Doe")

    def test_log_entry_total_miles_validation(self):
        """Test total_miles field validation"""
        log_entry = LogEntryFactory.create(
            total_miles=Decimal("500.5")
        )
        self.assertEqual(log_entry.total_miles, Decimal("500.5"))

    def test_log_entry_total_hours_validation(self):
        """Test total_hours field validation"""
        log_entry = LogEntryFactory.create(
            total_hours=Decimal("12.75")
        )
        self.assertEqual(log_entry.total_hours, Decimal("12.75"))


@pytest.mark.django_db
class TestActivityPeriodModel(TestCaseHelper):
    def test_activity_period_model_creation(self):
        """Test ActivityPeriod model creation works"""
        activity_period = ActivityPeriodFactory.create()
        self.assertNotNone(activity_period.uid)
        self.assertNotNone(activity_period.log_entry)
        self.assertNotNone(activity_period.activity)
        self.assertNotNone(activity_period.start_time)
        self.assertNotNone(activity_period.end_time)

    def test_activity_period_string_representation(self):
        """Test activity period string representation"""
        activity_period = ActivityPeriodFactory.create(
            activity="driving",
            start_time=time(6, 0),
            end_time=time(14, 0)
        )
        expected = "Driving - 06:00:00 to 14:00:00"
        self.assertEqual(str(activity_period), expected)

    def test_activity_period_duration_hours_calculation(self):
        """Test duration_hours property calculation"""
        activity_period = ActivityPeriodFactory.create(
            start_time=time(6, 0),
            end_time=time(14, 0)
        )
        
        expected_duration = 8.0  # 8 hours
        self.assertEqual(activity_period.duration_hours, expected_duration)

    def test_activity_period_duration_hours_overnight(self):
        """Test duration_hours property for overnight periods"""
        activity_period = ActivityPeriodFactory.create(
            start_time=time(22, 0),
            end_time=time(6, 0)
        )
        
        expected_duration = 8.0  # 8 hours (overnight)
        self.assertEqual(activity_period.duration_hours, expected_duration)

    def test_activity_period_activity_choices(self):
        """Test activity field choices"""
        valid_activities = [
            "off_duty",
            "sleeper_berth", 
            "driving",
            "on_duty_not_driving"
        ]
        
        for activity in valid_activities:
            activity_period = ActivityPeriodFactory.create(activity=activity)
            self.assertEqual(activity_period.activity, activity)

    def test_activity_period_invalid_activity(self):
        """Test activity field with invalid choice"""
        with pytest.raises(ValidationError):
            activity_period = ActivityPeriodFactory.build(activity="invalid")
            activity_period.full_clean()

    def test_activity_period_location_optional(self):
        """Test location field is optional"""
        activity_period = ActivityPeriodFactory.create(location="")
        self.assertEqual(activity_period.location, "")

    def test_activity_period_remarks_optional(self):
        """Test remarks field is optional"""
        activity_period = ActivityPeriodFactory.create(remarks="")
        self.assertEqual(activity_period.remarks, "")


@pytest.mark.django_db
class TestModelRelationships(TestCaseHelper):
    def test_trip_driver_relationship(self):
        """Test trip-driver relationship"""
        user = UserFactory.create()
        trip = TripFactory.create(driver=user)
        
        self.assertEqual(trip.driver, user)
        self.assertIn(trip, user.trips.all())

    def test_route_trip_relationship(self):
        """Test route-trip relationship"""
        trip = TripFactory.create()
        route = RouteFactory.create(trip=trip)
        
        self.assertEqual(route.trip, trip)
        self.assertEqual(trip.route, route)

    def test_log_entry_trip_relationship(self):
        """Test log entry-trip relationship"""
        trip = TripFactory.create()
        log_entry = LogEntryFactory.create(trip=trip)
        
        self.assertEqual(log_entry.trip, trip)
        self.assertIn(log_entry, trip.log_entries.all())

    def test_activity_period_log_entry_relationship(self):
        """Test activity period-log entry relationship"""
        log_entry = LogEntryFactory.create()
        activity_period = ActivityPeriodFactory.create(log_entry=log_entry)
        
        self.assertEqual(activity_period.log_entry, log_entry)
        self.assertIn(activity_period, log_entry.activity_periods.all())

    def test_trip_cascade_delete(self):
        """Test cascade delete from trip to related models"""
        trip = TripFactory.create()
        route = RouteFactory.create(trip=trip)
        log_entry = LogEntryFactory.create(trip=trip)
        activity_period = ActivityPeriodFactory.create(log_entry=log_entry)
        
        # Delete trip
        trip.delete()
        
        # Check that related objects are deleted
        self.assertFalse(Route.objects.filter(uid=route.uid).exists())
        self.assertFalse(LogEntry.objects.filter(uid=log_entry.uid).exists())
        self.assertFalse(
            ActivityPeriod.objects.filter(uid=activity_period.uid).exists()
        )

    def test_log_entry_cascade_delete(self):
        """Test cascade delete from log entry to activity periods"""
        log_entry = LogEntryFactory.create()
        activity_period = ActivityPeriodFactory.create(log_entry=log_entry)
        
        # Delete log entry
        log_entry.delete()
        
        # Check that activity period is deleted
        self.assertFalse(
            ActivityPeriod.objects.filter(uid=activity_period.uid).exists()
        ) 