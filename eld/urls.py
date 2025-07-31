from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, LogEntryViewSet, RouteViewSet

router = DefaultRouter()
router.register(r"trips", TripViewSet, basename="trip")
router.register(r"log-entries", LogEntryViewSet, basename="log-entry")
router.register(r"routes", RouteViewSet, basename="route")

app_name = "eld"

urlpatterns = router.urls