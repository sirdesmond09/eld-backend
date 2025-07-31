"""
URL configuration for notifications app.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import NotificationViewSet, NotificationPreferenceView

app_name = "notifications"

router = SimpleRouter()
router.register(r"", NotificationViewSet, basename="notification")
router.register(r"preferences", NotificationPreferenceView, basename="notification-preference")


urlpatterns = [
    path("", include(router.urls))
]
