import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from core.models import User
from django.core.management import call_command
from utils.factories import UserFactory, TripFactory, RouteFactory, LogEntryFactory, ActivityPeriodFactory
from moto import mock_aws
import boto3


@pytest.fixture(autouse=True)
def model_fixtures(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Ensure database is ready
        from django.db import connection

        connection.ensure_connection()


@pytest.fixture(scope="function")
def test_user() -> User:
    return UserFactory.create(verified=True)


@pytest.fixture(scope="function")
def staff_user() -> User:
    return UserFactory.create(verified=True, staff_user=True)


@pytest.fixture(scope="function")
def email_mocker(mocker):
    mock = mocker.patch("utils.emails.BaseEmail.send_email")
    yield mock


@pytest.fixture(scope="function")
def user_with_password() -> User:
    user = UserFactory.create(verified=True)
    user.set_password("OldValidPassword123")
    user.save()
    return user


# ELD App Fixtures
@pytest.fixture(scope="function")
def test_driver() -> User:
    """Create a test driver user"""
    return UserFactory.create(verified=True)


@pytest.fixture(scope="function")
def test_trip(test_driver):
    """Create a test trip"""
    return TripFactory.create(driver=test_driver)


@pytest.fixture(scope="function")
def test_trip_with_route(test_trip):
    """Create a test trip with route"""
    route = RouteFactory.create(trip=test_trip)
    return test_trip


@pytest.fixture(scope="function")
def test_trip_with_logs(test_trip):
    """Create a test trip with log entries"""
    log_entry = LogEntryFactory.create(trip=test_trip)
    return test_trip


@pytest.fixture(scope="function")
def test_log_entry(test_trip):
    """Create a test log entry"""
    return LogEntryFactory.create(trip=test_trip)


@pytest.fixture(scope="function")
def test_log_entry_with_activities(test_log_entry):
    """Create a test log entry with activity periods"""
    activity_period = ActivityPeriodFactory.create(log_entry=test_log_entry)
    return test_log_entry


@pytest.fixture(scope="function")
def test_activity_period(test_log_entry):
    """Create a test activity period"""
    return ActivityPeriodFactory.create(log_entry=test_log_entry)


@pytest.fixture(scope="function")
def test_route(test_trip):
    """Create a test route"""
    return RouteFactory.create(trip=test_trip)


@pytest.fixture(scope="function")
def short_trip(test_driver):
    """Create a short trip (single day)"""
    return TripFactory.create(
        driver=test_driver,
        estimated_duration=Decimal("8.00"),
        estimated_distance=Decimal("400.00")
    )


@pytest.fixture(scope="function")
def long_trip(test_driver):
    """Create a long trip (multiple days)"""
    return TripFactory.create(
        driver=test_driver,
        estimated_duration=Decimal("30.00"),
        estimated_distance=Decimal("1500.00")
    )


@pytest.fixture(scope="function")
def completed_trip(test_driver):
    """Create a completed trip"""
    return TripFactory.create(
        driver=test_driver,
        status="completed"
    )


@pytest.fixture(scope="function")
def in_progress_trip(test_driver):
    """Create an in-progress trip"""
    return TripFactory.create(
        driver=test_driver,
        status="in_progress"
    )


@pytest.fixture(scope="function")
def driving_activity_period(test_log_entry):
    """Create a driving activity period"""
    return ActivityPeriodFactory.create(
        log_entry=test_log_entry,
        activity="driving",
        start_time=time(6, 0),
        end_time=time(14, 0)
    )


@pytest.fixture(scope="function")
def rest_activity_period(test_log_entry):
    """Create a rest activity period"""
    return ActivityPeriodFactory.create(
        log_entry=test_log_entry,
        activity="off_duty",
        start_time=time(14, 0),
        end_time=time(22, 0)
    )


@pytest.fixture(scope="function")
def sleeper_activity_period(test_log_entry):
    """Create a sleeper berth activity period"""
    return ActivityPeriodFactory.create(
        log_entry=test_log_entry,
        activity="sleeper_berth",
        start_time=time(22, 0),
        end_time=time(6, 0)
    )


@pytest.fixture(scope="function")
def valid_trip_data():
    """Valid trip creation data"""
    return {
        "current_location": "New York, NY",
        "pickup_location": "Boston, MA",
        "dropoff_location": "Philadelphia, PA",
        "current_cycle_used": "25.50"
    }


@pytest.fixture(scope="function")
def valid_trip_plan_data():
    """Valid trip planning data"""
    return {
        "current_location": "New York, NY",
        "pickup_location": "Boston, MA",
        "dropoff_location": "Philadelphia, PA",
        "current_cycle_used": "25.50",
        "driver_name": "John Doe",
        "carrier_name": "ABC Trucking",
        "vehicle_numbers": "TRK-001"
    }


@pytest.fixture(scope="function")
def valid_log_generation_data(test_trip):
    """Valid log generation data"""
    return {
        "trip_id": str(test_trip.id),
        "start_date": date.today().isoformat(),
        "driver_name": "John Doe",
        "carrier_name": "ABC Trucking",
        "vehicle_numbers": "TRK-001"
    }


@pytest.fixture(scope="function")
def invalid_trip_data():
    """Invalid trip creation data"""
    return {
        "current_location": "",
        "pickup_location": "",
        "dropoff_location": "",
        "current_cycle_used": "75.00"  # Exceeds max
    }


@pytest.fixture(scope="function")
def multiple_trips(test_driver):
    """Create multiple trips for testing"""
    trips = []
    for i in range(3):
        trip = TripFactory.create(
            driver=test_driver,
            current_location=f"Location {i}",
            pickup_location=f"Pickup {i}",
            dropoff_location=f"Dropoff {i}"
        )
        trips.append(trip)
    return trips


@pytest.fixture(scope="function")
def multiple_log_entries(test_trip):
    """Create multiple log entries for testing"""
    log_entries = []
    for i in range(3):
        log_entry = LogEntryFactory.create(
            trip=test_trip,
            date=date.today() + timedelta(days=i)
        )
        log_entries.append(log_entry)
    return log_entries


@pytest.fixture(scope="function")
def multiple_activity_periods(test_log_entry):
    """Create multiple activity periods for testing"""
    periods = []
    activities = ["driving", "off_duty", "sleeper_berth", "on_duty_not_driving"]
    
    for i, activity in enumerate(activities):
        period = ActivityPeriodFactory.create(
            log_entry=test_log_entry,
            activity=activity,
            start_time=time(6 + i * 4, 0),
            end_time=time(10 + i * 4, 0)
        )
        periods.append(period)
    return periods
