from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)

from core.models import Trip, Route, LogEntry
from utils.views import BaseAuthenticatedViewSet
from .serializers import (
    TripSerializer,
    TripCreateSerializer,
    TripPlanRequestSerializer,
    LogGenerationRequestSerializer,
    LogEntrySerializer,
    RouteSerializer,
)
from .services import TripPlanningService


class TripViewSet(
    BaseAuthenticatedViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """ViewSet for managing trips"""

    serializer_class = TripSerializer
    queryset = Trip.objects.all()

    def get_queryset(self):
        return self.queryset.filter(driver=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return TripCreateSerializer
        return TripSerializer

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)

    @action(detail=False, methods=["post"])
    def plan_trip(self, request):
        """Plan a complete trip with route and HOS calculations"""
        serializer = TripPlanRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                planning_service = TripPlanningService()

                # Create trip data
                trip_data = {
                    "driver": request.user,
                    "current_location": serializer.validated_data[
                        "current_location"
                    ],
                    "pickup_location": serializer.validated_data[
                        "pickup_location"
                    ],
                    "dropoff_location": serializer.validated_data[
                        "dropoff_location"
                    ],
                    "current_cycle_used": serializer.validated_data[
                        "current_cycle_used"
                    ],
                }

                # Plan the trip
                trip = planning_service.plan_trip(trip_data)

                # Return trip data
                trip_serializer = TripSerializer(
                    trip, context={"request": request}
                )
                return Response(
                    trip_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def generate_logs(self, request, pk=None):
        """Generate log entries for a trip"""
        trip = self.get_object()

        serializer = LogGenerationRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                planning_service = TripPlanningService()
                start_date = serializer.validated_data["start_date"]

                # Generate logs
                log_entries = planning_service.generate_logs(trip, start_date)

                # Return log entries
                log_serializer = LogEntrySerializer(
                    log_entries, many=True, context={"request": request}
                )
                return Response(
                    log_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def route(self, request, pk=None):
        """Get route for a trip"""
        trip = self.get_object()
        try:
            route = trip.route
            serializer = RouteSerializer(route, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Route.DoesNotExist:
            return Response(
                {"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        """Get log entries for a trip"""
        trip = self.get_object()
        log_entries = trip.log_entries.all()
        serializer = LogEntrySerializer(
            log_entries, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogEntryViewSet(
    BaseAuthenticatedViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """ViewSet for managing log entries"""

    serializer_class = LogEntrySerializer
    queryset = LogEntry.objects.all()

    def get_queryset(self):
        return self.queryset.filter(trip__driver=self.request.user)

    @action(detail=True, methods=["get"])
    def download_pdf(self, request, pk=None):
        """Download log entry as PDF"""
        log_entry = self.get_object()
        # Mock PDF download response
        return Response(
            {"id": log_entry.uid, "message": "PDF download would be here"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def download_image(self, request, pk=None):
        """Download log entry as image"""
        log_entry = self.get_object()
        # Mock image download response
        return Response(
            {"id": log_entry.uid, "message": "Image download would be here"},
            status=status.HTTP_200_OK,
        )


class RouteViewSet(
    BaseAuthenticatedViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """ViewSet for managing routes"""

    serializer_class = RouteSerializer
    queryset = Route.objects.all()

    def get_queryset(self):
        return self.queryset.filter(trip__driver=self.request.user)

    @action(detail=True, methods=["get"])
    def map_data(self, request, pk=None):
        """Get map data for a route"""
        route = self.get_object()
        map_data = {
            "route_data": route.route_data,
            "rest_stops": route.rest_stops,
            "fuel_stops": route.fuel_stops,
            "total_distance": route.total_distance,
            "total_duration": route.total_duration,
        }
        return Response(map_data, status=status.HTTP_200_OK)
