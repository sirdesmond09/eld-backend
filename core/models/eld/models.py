from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from core.models.accounts import User

from core.models.base import TimeStampUUIDModel


class Trip(TimeStampUUIDModel):
    """Model for storing trip information"""

    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trips"
    )

    # Trip details
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(70)],
        help_text="Current cycle used in hours (0-70)",
    )

    # Calculated fields
    estimated_distance = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    estimated_duration = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    # Status
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="planned"
    )

    # Timestamps
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Trip {self.uid} - {self.pickup_location} to "
            f"{self.dropoff_location}"
        )

    @property
    def total_duration(self):
        """Calculate total trip duration in hours"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return 0

    @property
    def requires_multiple_logs(self):
        """Check if trip requires multiple daily logs"""
        if self.estimated_duration:
            return self.estimated_duration > 24
        return False


class Route(TimeStampUUIDModel):
    """Model for storing route information and waypoints"""

    trip = models.OneToOneField(
        Trip, on_delete=models.CASCADE, related_name="route"
    )

    # Route details
    route_data = models.JSONField(
        default=dict, help_text="Stored route data from map API"
    )
    total_distance = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    total_duration = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    # Rest stops and fueling
    rest_stops = models.JSONField(
        default=list, help_text="List of rest stops along the route"
    )
    fuel_stops = models.JSONField(
        default=list, help_text="List of fuel stops along the route"
    )

    def __str__(self):
        return f"Route for Trip {self.trip.uid}"


class LogEntry(TimeStampUUIDModel):
    """Model for individual log entries (24-hour periods)"""

    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="log_entries"
    )

    # Log period
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Totals
    total_miles = models.DecimalField(
        max_digits=6, decimal_places=1, default=0
    )
    total_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=0
    )

    # Driver info
    driver_name = models.CharField(max_length=255)
    carrier_name = models.CharField(max_length=255, default="")
    vehicle_numbers = models.CharField(max_length=255, default="")

    # Remarks
    remarks = models.TextField(blank=True)

    # Log data
    log_data = models.JSONField(
        default=dict, help_text="Hourly breakdown of activities"
    )

    class Meta:
        unique_together = ["trip", "date"]
        ordering = ["date"]

    def __str__(self):
        return f"Log Entry {self.date} - Trip {self.trip.uid}"


class ActivityPeriod(TimeStampUUIDModel):
    """Model for individual activity periods within a log entry"""

    log_entry = models.ForeignKey(
        LogEntry, on_delete=models.CASCADE, related_name="activity_periods"
    )

    ACTIVITY_CHOICES = [
        ("off_duty", "Off Duty"),
        ("sleeper_berth", "Sleeper Berth"),
        ("driving", "Driving"),
        ("on_duty_not_driving", "On Duty (Not Driving)"),
    ]

    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return (
            f"{self.get_activity_display()} - {self.start_time} to "
            f"{self.end_time}"
        )

    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600
