"""Constants for MetroBus API."""
from __future__ import annotations

from enum import Enum

from ..const import BASE_WMATA_URL


class BusEndpoint(Enum):
    """Endpoints for all MetroBus APIs."""

    BUS_INCIDENTS = f"{BASE_WMATA_URL}/Incidents.svc/json/BusIncidents"
    NEXT_BUSES = f"{BASE_WMATA_URL}/NextBusService.svc/json/jNextBuss"
    ROUTE_PATH = f"{BASE_WMATA_URL}/Bus.svc/json/jRouteDetails"
    POSITIONS = f"{BASE_WMATA_URL}/Bus.svc/json/jBusLiveBusPositions"
    ROUTE_SCHEDULE = f"{BASE_WMATA_URL}/Bus.svc/json/jRouteSchedule"
    ROUTES = f"{BASE_WMATA_URL}/Bus.svc/json/jRoutes"
    STOP_SCHEDULE = f"{BASE_WMATA_URL}/Bus.svc/json/jStopSchedule"
    STOPS = f"{BASE_WMATA_URL}/Bus.svc/json/jStops"
