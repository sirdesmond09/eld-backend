"""
Admin configuration for notifications app.
"""

from django.contrib import admin
from core.models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification."""

    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    ordering = ("-created_at",)
    readonly_fields = ("uid", "created_at")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin for NotificationPreference."""

    list_display = (
        "user",
        "email_notifications",
        "push_notifications",
        "sms_notifications",
    )
    list_filter = ("email_notifications", "push_notifications", "sms_notifications")
    search_fields = ("user__username", "user__email")
