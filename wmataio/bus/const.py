"""Constants for MetroBus API."""
from __future__ import annotations

from enum import Enum

from ..const import BASE_URL


class Endpoint(Enum):
    """Endpoints for all MetroBus APIs."""

    ROUTES = f"{BASE_URL}/Bus.svc/json/jRoutes"
    STOPS = f"{BASE_URL}/Bus.svc/json/jStops"
    INCIDENTS = f"{BASE_URL}/Incidents.svc/json/BusIncidents"
    POSITIONS = f"{BASE_URL}/Bus.svc/json/jBusPositions"
    PATH_DETAILS = f"{BASE_URL}/Bus.svc/json/jRouteDetails"
    ROUTE_SCHEDULE = f"{BASE_URL}/Bus.svc/json/jRouteSchedule"
    NEXT_BUSES = f"{BASE_URL}/NextBusService.svc/json/jPredictions"
    STOP_SCHEDULE = f"{BASE_URL}/Bus.svc/json/jStopSchedule"
