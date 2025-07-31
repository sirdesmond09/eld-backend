import factory
import factory.fuzzy
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from core.models import Trip, Route, LogEntry, ActivityPeriod
from utils.factories.accounts import UserFactory


class TripFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trip
        skip_postgeneration_save = True

    class Params:
        completed = factory.Trait(
            status="completed",
            start_time=factory.LazyFunction(
                lambda: datetime.now() - timedelta(days=1)
            ),
            end_time=factory.LazyFunction(datetime.now),
        )
        in_progress = factory.Trait(
            status="in_progress",
            start_time=factory.LazyFunction(
                lambda: datetime.now() - timedelta(hours=2)
            ),
        )
        long_trip = factory.Trait(
            estimated_duration=Decimal("30.00"),
            estimated_distance=Decimal("1500.00"),
        )
        short_trip = factory.Trait(
            estimated_duration=Decimal("4.50"),
            estimated_distance=Decimal("250.00"),
        )

    driver = factory.SubFactory(UserFactory)
    current_location = factory.Faker("city")
    pickup_location = factory.Faker("city")
    dropoff_location = factory.Faker("city")
    current_cycle_used = factory.fuzzy.FuzzyDecimal(
        low=0, high=70, precision=2
    )
    status = factory.fuzzy.FuzzyChoice(
        choices=["planned", "in_progress", "completed", "cancelled"]
    )


class RouteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Route

    trip = factory.SubFactory(TripFactory)
    route_data = factory.LazyFunction(
        lambda: {
            "distance": 500.0,
            "duration": 8.5,
            "waypoints": [
                {"location": "New York, NY", "type": "origin"},
                {"location": "Boston, MA", "type": "destination"},
            ],
        }
    )
    total_distance = factory.fuzzy.FuzzyDecimal(
        low=100, high=2000, precision=2
    )
    total_duration = factory.fuzzy.FuzzyDecimal(
        low=2, high=24, precision=2
    )
    rest_stops = factory.LazyFunction(
        lambda: [
            {
                "location": "Rest Stop at 300 miles",
                "duration": 0.5,
                "type": "rest_break",
                "reason": "30-minute break required",
            }
        ]
    )
    fuel_stops = factory.LazyFunction(
        lambda: [
            {
                "location": "Fuel Stop at 1000 miles",
                "duration": 0.5,
                "type": "fuel",
                "reason": "Fuel stop every 1000 miles",
            }
        ]
    )


class LogEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LogEntry
        skip_postgeneration_save = True

    class Params:
        long_day = factory.Trait(
            total_hours=Decimal("14.00"),
            total_miles=Decimal("600.0"),
        )
        short_day = factory.Trait(
            total_hours=Decimal("8.00"),
            total_miles=Decimal("300.0"),
        )
        with_remarks = factory.Trait(
            remarks="Completed delivery on time. No issues encountered.",
        )

    trip = factory.SubFactory(TripFactory)
    date = factory.fuzzy.FuzzyDate(
        start_date=date.today() - timedelta(days=30),
        end_date=date.today(),
    )
    start_time = factory.fuzzy.FuzzyChoice(
        choices=[
            time(6, 0),
            time(7, 0),
            time(8, 0),
            time(9, 0),
        ]
    )
    end_time = factory.fuzzy.FuzzyChoice(
        choices=[
            time(18, 0),
            time(19, 0),
            time(20, 0),
            time(21, 0),
        ]
    )
    total_miles = factory.fuzzy.FuzzyDecimal(
        low=100, high=800, precision=1
    )
    total_hours = factory.fuzzy.FuzzyDecimal(
        low=4, high=14, precision=2
    )
    driver_name = factory.LazyAttribute(
        lambda obj: f"{obj.trip.driver.first_name} {obj.trip.driver.last_name}"
    )
    carrier_name = factory.Faker("company")
    vehicle_numbers = factory.Faker("license_plate")
    remarks = factory.Faker("text", max_nb_chars=200)
    log_data = factory.LazyFunction(
        lambda: {
            "hour_1": "driving",
            "hour_2": "driving",
            "hour_3": "driving",
            "hour_4": "driving",
            "hour_5": "driving",
            "hour_6": "driving",
            "hour_7": "driving",
            "hour_8": "driving",
            "hour_9": "off_duty",
            "hour_10": "off_duty",
            "hour_11": "off_duty",
            "hour_12": "off_duty",
            "hour_13": "off_duty",
            "hour_14": "off_duty",
        }
    )


class ActivityPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityPeriod

    class Params:
        driving_period = factory.Trait(
            activity="driving",
            start_time=time(6, 0),
            end_time=time(14, 0),
        )
        rest_period = factory.Trait(
            activity="off_duty",
            start_time=time(14, 0),
            end_time=time(22, 0),
        )
        sleeper_period = factory.Trait(
            activity="sleeper_berth",
            start_time=time(22, 0),
            end_time=time(6, 0),
        )

    log_entry = factory.SubFactory(LogEntryFactory)
    activity = factory.fuzzy.FuzzyChoice(
        choices=[
            "off_duty",
            "sleeper_berth",
            "driving",
            "on_duty_not_driving",
        ]
    )
    start_time = factory.fuzzy.FuzzyChoice(
        choices=[
            time(6, 0),
            time(8, 0),
            time(10, 0),
            time(12, 0),
            time(14, 0),
            time(16, 0),
            time(18, 0),
            time(20, 0),
            time(22, 0),
        ]
    )
    end_time = factory.fuzzy.FuzzyChoice(
        choices=[
            time(8, 0),
            time(10, 0),
            time(12, 0),
            time(14, 0),
            time(16, 0),
            time(18, 0),
            time(20, 0),
            time(22, 0),
            time(6, 0),
        ]
    )
    location = factory.Faker("city")
    remarks = factory.Faker("text", max_nb_chars=100) 