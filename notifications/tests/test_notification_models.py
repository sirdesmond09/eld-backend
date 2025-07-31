# """
# Tests for notifications models.
# """

# import pytest
# from django.utils import timezone
# from core.models import Notification, NotificationPreference
# from utils.helpers import TestCaseHelper


# @pytest.mark.django_db
# class TestNotification(TestCaseHelper):
#     """Test Notification model."""

#     def test_notification_creation(self, test_user):
#         """Test notification creation."""
#         notification = Notification.objects.create(
#             user=test_user,
#             title="Test Notification",
#             message="This is a test notification",
#             notification_type="info",
#         )

#         assert notification.user == test_user
#         assert notification.title == "Test Notification"
#         assert notification.message == "This is a test notification"
#         assert notification.notification_type == "info"
#         assert notification.is_read is False

#     def test_notification_str(self, test_user):
#         """Test notification string representation."""
#         notification = Notification.objects.create(
#             user=test_user,
#             title="Test Notification",
#             message="This is a test notification"
#         )

#         assert str(notification) == f"{test_user.email} - Test Notification"

#     def test_notification_mark_as_read(self, test_user):
#         """Test marking notification as read."""
#         notification = Notification.objects.create(
#             user=test_user,
#             title="Test Notification",
#             message="This is a test notification"
#         )

#         assert notification.is_read is False
#         assert notification.read_at is None

#         notification.mark_as_read()

#         assert notification.is_read is True
#         assert notification.read_at is not None

#     def test_notification_mark_as_read_already_read(self, test_user):
#         """Test marking already read notification as read."""
#         notification = Notification.objects.create(
#             user=test_user,
#             title="Test Notification",
#             message="This is a test notification",
#             is_read=True,
#             read_at=timezone.now(),
#         )

#         original_read_at = notification.read_at
#         notification.mark_as_read()

#         # Should not change read_at if already read
#         assert notification.read_at == original_read_at


# @pytest.mark.django_db
# class TestNotificationPreference(TestCaseHelper):
#     """Test NotificationPreference model."""

#     def test_notification_preference_creation(self, test_user):
#         """Test notification preference creation."""
#         preference = NotificationPreference.objects.create(
#             user=test_user,
#             email_notifications=True,
#             push_notifications=True,
#             sms_notifications=False,
#         )

#         assert preference.user == test_user
#         assert preference.email_notifications is True
#         assert preference.push_notifications is True
#         assert preference.sms_notifications is False

#     def test_notification_preference_str(self, test_user):
#         """Test notification preference string representation."""
#         preference = NotificationPreference.objects.create(user=test_user)

#         assert str(preference) == f"{test_user.email}'s Notification Preferences"

#     def test_notification_preference_defaults(self, test_user):
#         """Test notification preference default values."""
#         preference = NotificationPreference.objects.create(user=test_user)

#         assert preference.email_notifications is True
#         assert preference.push_notifications is True
#         assert preference.sms_notifications is False
