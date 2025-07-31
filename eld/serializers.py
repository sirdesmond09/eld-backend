from rest_framework import serializers
from core.models import Trip, Route, LogEntry, ActivityPeriod


class ActivityPeriodSerializer(serializers.ModelSerializer):
    """Serializer for ActivityPeriod model"""
    activity_display = serializers.CharField(
        source='get_activity_display', read_only=True
    )
    duration_hours = serializers.DecimalField(
        max_digits=4, decimal_places=2, read_only=True
    )

    class Meta:
        model = ActivityPeriod
        fields = [
            'uid', 'activity', 'activity_display', 'start_time', 'end_time',
            'location', 'remarks', 'duration_hours'
        ]


class LogEntrySerializer(serializers.ModelSerializer):
    """Serializer for LogEntry model"""
    activity_periods = ActivityPeriodSerializer(many=True, read_only=True)
    date_display = serializers.DateField(source='date', read_only=True)

    class Meta:
        model = LogEntry
        fields = [
            'uid', 'date', 'date_display', 'start_time', 'end_time',
            'total_miles', 'total_hours', 'driver_name', 'carrier_name',
            'vehicle_numbers', 'remarks', 'log_data', 'activity_periods'
        ]


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for Route model"""
    class Meta:
        model = Route
        fields = [
            'uid', 'route_data', 'total_distance', 'total_duration',
            'rest_stops', 'fuel_stops', 'created_at', 'updated_at'
        ]


class TripSerializer(serializers.ModelSerializer):
    """Serializer for Trip model"""
    route = RouteSerializer(read_only=True)
    log_entries = LogEntrySerializer(many=True, read_only=True)
    total_duration = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )
    requires_multiple_logs = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            'uid', 'current_location', 'pickup_location', 'dropoff_location',
            'current_cycle_used', 'estimated_distance', 'estimated_duration',
            'status', 'status_display', 'created_at', 'updated_at',
            'start_time', 'end_time', 'total_duration', 'requires_multiple_logs',
            'route', 'log_entries'
        ]
        read_only_fields = [
            'uid', 'estimated_distance', 'estimated_duration', 'created_at',
            'updated_at', 'start_time', 'end_time', 'total_duration',
            'requires_multiple_logs'
        ]


class TripCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new trips"""
    class Meta:
        model = Trip
        fields = [
            'current_location', 'pickup_location', 'dropoff_location',
            'current_cycle_used'
        ]

    def create(self, validated_data):
        validated_data['driver'] = self.context['request'].user
        return super().create(validated_data)


class TripPlanRequestSerializer(serializers.Serializer):
    """Serializer for trip planning requests"""
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_used = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        min_value=0, max_value=70
    )
    driver_name = serializers.CharField(max_length=255, required=False)
    carrier_name = serializers.CharField(max_length=255, required=False)
    vehicle_numbers = serializers.CharField(max_length=255, required=False)


class LogGenerationRequestSerializer(serializers.Serializer):
    """Serializer for log generation requests"""
    start_date = serializers.DateField()
    driver_name = serializers.CharField(max_length=255, required=False)
    carrier_name = serializers.CharField(max_length=255, required=False)
    vehicle_numbers = serializers.CharField(max_length=255, required=False) 