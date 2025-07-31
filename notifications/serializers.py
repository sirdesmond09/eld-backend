"""
Notification serializers for the Django Project Template.
"""

from rest_framework import serializers
from core.models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    class Meta:
        model = Notification
        fields = [
            "uid",
            "title",
            "message",
            "notification_type",
            "is_read",
            "read_at",
            "data",
            "created_at",
        ]
        read_only_fields = ["uid", "created_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = [
            "email_notifications",
            "push_notifications",
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for notification list."""

    class Meta:
        model = Notification
        fields = [
            "uid",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["uid", "created_at"]
