from django.contrib import admin
from core.models import Trip, Route, LogEntry, ActivityPeriod


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        "uid",
        "driver",
        "pickup_location",
        "dropoff_location",
        "current_cycle_used",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["pickup_location", "dropoff_location", "driver__email"]
    readonly_fields = ["uid", "created_at", "updated_at", "total_duration"]

    fieldsets = (
        (
            "Trip Information",
            {
                "fields": (
                    "uid",
                    "driver",
                    "current_location",
                    "pickup_location",
                    "dropoff_location",
                    "current_cycle_used",
                )
            },
        ),
        (
            "Calculated Fields",
            {"fields": ("estimated_distance", "estimated_duration", "total_duration")},
        ),
        (
            "Status & Timestamps",
            {
                "fields": (
                    "status",
                    "start_time",
                    "end_time",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["uid", "trip", "total_distance", "total_duration", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["uid", "created_at", "updated_at"]

    fieldsets = (
        ("Route Information", {"fields": ("uid", "trip", "total_distance", "total_duration")}),
        ("Route Data", {"fields": ("route_data", "rest_stops", "fuel_stops")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "uid",
        "trip",
        "date",
        "driver_name",
        "total_miles",
        "total_hours",
        "created_at",
    ]
    list_filter = ["date", "created_at"]
    search_fields = ["driver_name", "carrier_name", "trip__pickup_location"]
    readonly_fields = ["uid", "created_at", "updated_at"]

    fieldsets = (
        ("Log Information", {"fields": ("uid", "trip", "date", "start_time", "end_time")}),
        ("Totals", {"fields": ("total_miles", "total_hours")}),
        (
            "Driver Information",
            {"fields": ("driver_name", "carrier_name", "vehicle_numbers")},
        ),
        ("Log Data", {"fields": ("remarks", "log_data")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ActivityPeriod)
class ActivityPeriodAdmin(admin.ModelAdmin):
    list_display = [
        "uid",
        "log_entry",
        "activity",
        "start_time",
        "end_time",
        "location",
        "duration_hours",
    ]
    list_filter = ["activity", "start_time"]
    search_fields = ["location", "remarks", "log_entry__driver_name"]
    readonly_fields = ["uid", "duration_hours"]

    fieldsets = (
        (
            "Activity Information",
            {"fields": ("uid", "log_entry", "activity", "start_time", "end_time")},
        ),
        ("Location & Remarks", {"fields": ("location", "remarks")}),
        ("Calculated Fields", {"fields": ("duration_hours",)}),
    )
