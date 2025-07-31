import requests
from datetime import datetime, timedelta, time
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from core.models import Trip, Route, LogEntry, ActivityPeriod


class MapService:
    """Service for handling map API interactions"""

    def __init__(self):
        # Using OpenRouteService API (free tier available)
        self.base_url = "https://api.openrouteservice.org/v2/directions"
        self.api_key = None  # Will be set from environment

    def get_route(
        self, origin: str, destination: str, waypoints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get route information from map API
        Returns route data with distance, duration, and waypoints
        """
        try:
            # For now, return mock data - in production, integrate with actual API
            # This would be replaced with actual API call to OpenRouteService or similar

            # Mock route calculation (simplified)
            route_data = {
                "distance": 500.0,  # miles
                "duration": 8.5,  # hours
                "waypoints": [
                    {"location": origin, "type": "origin"},
                    {"location": destination, "type": "destination"},
                ],
                "rest_stops": self._calculate_rest_stops(500.0),
                "fuel_stops": self._calculate_fuel_stops(500.0),
            }

            return route_data

        except Exception as e:
            raise Exception(f"Failed to get route: {str(e)}")

    def _calculate_rest_stops(self, distance: float) -> List[Dict[str, Any]]:
        """Calculate rest stops based on HOS requirements"""
        stops = []

        # Every 8 hours of driving requires a 30-minute break
        # Every 11 hours of driving requires a 10-hour rest
        driving_hours = distance / 60  # Assuming 60 mph average

        if driving_hours > 8:
            # Add 30-minute break after 8 hours
            break_location = f"Rest Stop at {distance * 0.6:.0f} miles"
            stops.append(
                {
                    "location": break_location,
                    "duration": 0.5,
                    "type": "rest_break",
                    "reason": "30-minute break required after 8 hours driving",
                }
            )

        if driving_hours > 11:
            # Add 10-hour rest after 11 hours
            rest_location = f"Rest Area at {distance * 0.8:.0f} miles"
            stops.append(
                {
                    "location": rest_location,
                    "duration": 10,
                    "type": "sleeper_berth",
                    "reason": "10-hour rest required after 11 hours driving",
                }
            )

        return stops

    def _calculate_fuel_stops(self, distance: float) -> List[Dict[str, Any]]:
        """Calculate fuel stops (every 1000 miles)"""
        stops = []

        if distance > 1000:
            fuel_miles = 1000
            while fuel_miles < distance:
                stops.append(
                    {
                        "location": f"Fuel Stop at {fuel_miles:.0f} miles",
                        "duration": 0.5,
                        "type": "fuel",
                        "reason": "Fuel stop every 1000 miles",
                    }
                )
                fuel_miles += 1000

        return stops


class HOSService:
    """Service for Hours of Service calculations and compliance"""

    def __init__(self):
        self.max_driving_hours = 11
        self.max_on_duty_hours = 14
        self.min_off_duty_hours = 10
        self.max_cycle_hours = 70
        self.break_required_after = 8  # hours

    def calculate_trip_logs(
        self, trip: Trip, start_date: datetime.date
    ) -> List[LogEntry]:
        """
        Calculate all required log entries for a trip
        Returns list of LogEntry objects
        """
        logs = []

        if not trip.estimated_duration:
            raise ValueError("Trip must have estimated duration")

        # Calculate number of days needed
        total_hours = float(trip.estimated_duration)
        days_needed = int((total_hours + 23) // 24)  # Ceiling division

        current_date = start_date
        remaining_hours = total_hours

        for day in range(days_needed):
            # Calculate hours for this day
            day_hours = min(24, remaining_hours)

            # Create log entry for this day
            log_entry = self._create_daily_log(trip, current_date, day_hours, day == 0)
            logs.append(log_entry)

            current_date += timedelta(days=1)
            remaining_hours -= day_hours

        return logs

    def _create_daily_log(
        self, trip: Trip, date: datetime.date, day_hours: float, is_first_day: bool
    ) -> LogEntry:
        """Create a single daily log entry"""

        # Calculate activity periods for this day
        activity_periods = self._calculate_activity_periods(
            trip, date, day_hours, is_first_day
        )

        # Calculate totals
        total_miles = self._calculate_day_miles(trip, day_hours)
        total_hours = day_hours

        # Create log entry
        log_entry = LogEntry.objects.create(
            trip=trip,
            date=date,
            start_time=time(6, 0),  # Start at 6 AM
            end_time=time(6, 0),  # End at 6 AM next day
            total_miles=total_miles,
            total_hours=total_hours,
            driver_name=getattr(trip.driver, "first_name", "Driver")
            + " "
            + getattr(trip.driver, "last_name", ""),
            carrier_name="",
            vehicle_numbers="",
            remarks=self._generate_remarks(activity_periods),
            log_data=self._create_log_grid(activity_periods),
        )

        # Create activity periods
        for period_data in activity_periods:
            ActivityPeriod.objects.create(log_entry=log_entry, **period_data)

        return log_entry

    def _calculate_activity_periods(
        self, trip: Trip, date: datetime.date, day_hours: float, is_first_day: bool
    ) -> List[Dict[str, Any]]:
        """Calculate activity periods for a day"""
        periods = []

        if is_first_day:
            # First day: start with pickup and driving
            periods.extend(
                [
                    {
                        "activity": "on_duty_not_driving",
                        "start_time": time(6, 0),
                        "end_time": time(7, 0),
                        "location": trip.pickup_location,
                        "remarks": "Pickup and pre-trip inspection",
                    },
                    {
                        "activity": "driving",
                        "start_time": time(7, 0),
                        "end_time": time(18, 0),  # 11 hours driving
                        "location": f"{trip.pickup_location} to {trip.dropoff_location}",
                        "remarks": "Driving to destination",
                    },
                    {
                        "activity": "on_duty_not_driving",
                        "start_time": time(18, 0),
                        "end_time": time(19, 0),
                        "location": trip.dropoff_location,
                        "remarks": "Dropoff and post-trip inspection",
                    },
                    {
                        "activity": "off_duty",
                        "start_time": time(19, 0),
                        "end_time": time(6, 0),  # Next day
                        "location": trip.dropoff_location,
                        "remarks": "Off duty rest",
                    },
                ]
            )
        else:
            # Subsequent days: continue driving
            periods.extend(
                [
                    {
                        "activity": "driving",
                        "start_time": time(6, 0),
                        "end_time": time(17, 0),  # 11 hours driving
                        "location": f"Continuing to {trip.dropoff_location}",
                        "remarks": "Driving to destination",
                    },
                    {
                        "activity": "off_duty",
                        "start_time": time(17, 0),
                        "end_time": time(6, 0),  # Next day
                        "location": "Rest area",
                        "remarks": "Off duty rest",
                    },
                ]
            )

        return periods

    def _calculate_day_miles(self, trip: Trip, day_hours: float) -> Decimal:
        """Calculate miles driven in a day"""
        if trip.estimated_distance:
            # Proportional to hours
            total_hours = float(trip.estimated_duration)
            return Decimal(
                str((day_hours / total_hours) * float(trip.estimated_distance))
            )
        return Decimal("0")

    def _generate_remarks(self, activity_periods: List[Dict[str, Any]]) -> str:
        """Generate remarks for the log entry"""
        remarks = []
        for period in activity_periods:
            if period.get("location"):
                remarks.append(f"{period['location']}")
        return "; ".join(remarks)

    def _create_log_grid(
        self, activity_periods: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create the 24-hour grid data for the log"""
        grid = {}

        # Initialize 24-hour grid
        for hour in range(24):
            grid[f"{hour:02d}:00"] = "off_duty"

        # Fill in activity periods
        for period in activity_periods:
            start_hour = period["start_time"].hour
            end_hour = period["end_time"].hour

            if end_hour < start_hour:  # Crosses midnight
                # Fill from start to 23
                for hour in range(start_hour, 24):
                    grid[f"{hour:02d}:00"] = period["activity"]
                # Fill from 0 to end
                for hour in range(0, end_hour):
                    grid[f"{hour:02d}:00"] = period["activity"]
            else:
                # Fill from start to end
                for hour in range(start_hour, end_hour):
                    grid[f"{hour:02d}:00"] = period["activity"]

        return grid


class TripPlanningService:
    """Service for planning trips and generating routes"""

    def __init__(self):
        self.map_service = MapService()
        self.hos_service = HOSService()

    def plan_trip(self, trip_data: Dict[str, Any]) -> Trip:
        """Plan a complete trip with route and logs"""

        # Create trip
        trip = Trip.objects.create(
            driver=trip_data["driver"],
            current_location=trip_data["current_location"],
            pickup_location=trip_data["pickup_location"],
            dropoff_location=trip_data["dropoff_location"],
            current_cycle_used=trip_data["current_cycle_used"],
        )

        # Get route information
        route_data = self.map_service.get_route(
            trip.pickup_location, trip.dropoff_location
        )

        # Update trip with route data
        trip.estimated_distance = route_data["distance"]
        trip.estimated_duration = route_data["duration"]
        trip.save()

        # Create route
        Route.objects.create(
            trip=trip,
            route_data=route_data,
            total_distance=route_data["distance"],
            total_duration=route_data["duration"],
            rest_stops=route_data["rest_stops"],
            fuel_stops=route_data["fuel_stops"],
        )

        return trip

    def generate_logs(self, trip: Trip, start_date: datetime.date) -> List[LogEntry]:
        """Generate all required log entries for a trip"""
        return self.hos_service.calculate_trip_logs(trip, start_date)
