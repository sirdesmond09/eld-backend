# """
# Tests for notifications views.
# """

# import pytest
# from rest_framework import status
# from utils.helpers import TestCaseHelper
# from core.models import Notification, NotificationPreference

# # API URLs
# notification_list_url = "/api/v1/notifications/"
# notification_detail_url = "/api/v1/notifications/{0}/"
# notification_mark_read_url = "/api/v1/notifications/{0}/mark_as_read/"
# notification_mark_all_read_url = "/api/v1/notifications/mark_all_as_read/"
# notification_preferences_url = "/api/v1/notifications/preferences/"


# @pytest.mark.django_db
# class TestNotificationList(TestCaseHelper):
#     """Test notification list views."""

#     def test_get_notifications(self, landlord_user):
#         """Test getting user notifications."""
#         client = self.get_authenticated_client(landlord_user)

#         # Create some notifications
#         Notification.objects.create(
#             user=landlord_user,
#             title="Test Notification 1",
#             message="First test notification",
#         )
#         Notification.objects.create(
#             user=landlord_user,
#             title="Test Notification 2",
#             message="Second test notification",
#         )

#         response = client.get(notification_list_url)

#         assert response.status_code == status.HTTP_200_OK
#         assert len(response.data["results"]) == 2
#         assert response.data["results"][0]["title"] == "Test Notification 1"
#         assert response.data["results"][1]["title"] == "Test Notification 2"

#     def test_get_notifications_empty(self, landlord_user):
#         """Test getting notifications when user has none."""
#         client = self.get_authenticated_client(landlord_user)

#         response = client.get(notification_list_url)

#         assert response.status_code == status.HTTP_200_OK
#         assert len(response.data["results"]) == 0

#     def test_get_notifications_unread_only(self, landlord_user):
#         """Test getting unread notifications only."""
#         client = self.get_authenticated_client(landlord_user)

#         # Create read and unread notifications
#         Notification.objects.create(
#             user=landlord_user,
#             title="Read Notification",
#             message="This is read",
#             is_read=True,
#         )
#         Notification.objects.create(
#             user=landlord_user,
#             title="Unread Notification",
#             message="This is unread",
#             is_read=False,
#         )

#         response = client.get(f"{notification_list_url}?unread_only=true")

#         assert response.status_code == status.HTTP_200_OK
#         assert len(response.data["results"]) == 1
#         assert response.data["results"][0]["title"] == "Unread Notification"


# @pytest.mark.django_db
# class TestNotificationDetail(TestCaseHelper):
#     """Test notification detail views."""

#     def test_get_notification_detail(self, landlord_user):
#         """Test getting notification detail."""
#         client = self.get_authenticated_client(landlord_user)

#         notification = Notification.objects.create(
#             user=landlord_user, title="Test Notification", message="Test message"
#         )

#         url = notification_detail_url.format(notification.uid)
#         response = client.get(url)

#         assert response.status_code == status.HTTP_200_OK
#         assert response.data["title"] == "Test Notification"
#         assert response.data["message"] == "Test message"

#     def test_mark_notification_as_read(self, landlord_user):
#         """Test marking notification as read."""
#         client = self.get_authenticated_client(landlord_user)

#         notification = Notification.objects.create(
#             user=landlord_user,
#             title="Test Notification",
#             message="Test message",
#             is_read=False,
#         )

#         url = notification_mark_read_url.format(notification.uid)
#         response = client.post(url)

#         assert response.status_code == status.HTTP_200_OK
#         notification.refresh_from_db()
#         assert notification.is_read is True
#         assert notification.read_at is not None

#     def test_mark_all_notifications_as_read(self, landlord_user):
#         """Test marking all notifications as read."""
#         client = self.get_authenticated_client(landlord_user)

#         # Create multiple unread notifications
#         Notification.objects.create(
#             user=landlord_user,
#             title="Notification 1",
#             message="First notification",
#             is_read=False,
#         )
#         Notification.objects.create(
#             user=landlord_user,
#             title="Notification 2",
#             message="Second notification",
#             is_read=False,
#         )

#         response = client.post(notification_mark_all_read_url)

#         assert response.status_code == status.HTTP_200_OK
#         unread_count = Notification.objects.filter(
#             user=landlord_user, is_read=True
#         ).count()
#         assert unread_count == 2


# @pytest.mark.django_db
# class TestNotificationPreference(TestCaseHelper):
#     """Test notification preference views."""

#     def test_get_notification_preferences(self, landlord_user):
#         """Test getting notification preferences."""
#         client = self.get_authenticated_client(landlord_user)

#         NotificationPreference.objects.create(
#             user=landlord_user,
#             email_notifications=True,
#             push_notifications=False,
#             sms_notifications=True,
#         )

#         response = client.get(notification_preferences_url)

#         assert response.status_code == status.HTTP_200_OK
#         assert response.data["email_notifications"] is True
#         assert response.data["push_notifications"] is False
#         assert response.data["sms_notifications"] is True

#     def test_update_notification_preferences(self, landlord_user):
#         """Test updating notification preferences."""
#         client = self.get_authenticated_client(landlord_user)

#         NotificationPreference.objects.create(user=landlord_user)

#         data = {
#             "email_notifications": False,
#             "push_notifications": True,
#             "sms_notifications": False,
#         }

#         response = client.put(notification_preferences_url, data)

#         assert response.status_code == status.HTTP_200_OK
#         assert response.data["email_notifications"] is False
#         assert response.data["push_notifications"] is True
#         assert response.data["sms_notifications"] is False
