"""
Notification views for the Django Project Template.
"""

from django.utils import timezone
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
)
from utils.paginators import CustomLimitOffsetPagination
from utils.views import BaseAuthenticatedViewSet


class NotificationViewSet(BaseAuthenticatedViewSet):
    """ViewSet for notifications."""

    serializer_class = NotificationSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        return NotificationSerializer

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response({"message": "All notifications marked as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})


class NotificationPreferenceView(
    BaseAuthenticatedViewSet, RetrieveModelMixin, UpdateModelMixin
):
    """View for notification preferences."""

    serializer_class = NotificationPreferenceSerializer
    queryset = NotificationPreference.objects.all()

    def get_object(self):
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj
