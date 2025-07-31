"""
Notification models for the Django Project Template.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import TimeStampUUIDModel
from django.utils import timezone
from core.models import User


class Notification(TimeStampUUIDModel):
    """Notification model for user notifications."""

    NOTIFICATION_TYPES = (
        ("info", _("Information")),
        ("success", _("Success")),
        ("warning", _("Warning")),
        ("error", _("Error")),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(_("Title"), max_length=255)
    message = models.TextField(_("Message"))
    notification_type = models.CharField(
        _("Type"), max_length=20, choices=NOTIFICATION_TYPES, default="info"
    )
    is_read = models.BooleanField(_("Is Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), blank=True, null=True)
    data = models.JSONField(_("Additional Data"), blank=True, null=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NotificationPreference(TimeStampUUIDModel):
    """User notification preferences."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)
    push_notifications = models.BooleanField(_("Push Notifications"), default=True)
    sms_notifications = models.BooleanField(_("SMS Notifications"), default=False)

    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
