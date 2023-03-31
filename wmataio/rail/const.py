"""Constants for MetroRail API."""
from __future__ import annotations

from enum import Enum

from ..const import BASE_URL


class Endpoint(Enum):
    """Endpoints for all MetroRail endpoints."""

    NEXT_TRAINS = f"{BASE_URL}/StationPrediction.svc/json/GetPrediction"
    STATION_INFORMATION = f"{BASE_URL}/Rail.svc/json/jStationInfo"
    STATION_PARKING_INFORMATION = f"{BASE_URL}/Rail.svc/json/jStationParking"
    STATION_TO_STATION_PATH = f"{BASE_URL}/Rail.svc/json/jPath"
    STATION_TIMINGS = f"{BASE_URL}/Rail.svc/json/jStationTimes"
    STATION_TO_STATION_INFO = f"{BASE_URL}/Rail.svc/json/jSrcStationToDstStationInfo"
    LINES = f"{BASE_URL}/Rail.svc/json/jLines"
    STATION_ENTRANCES = f"{BASE_URL}/Rail.svc/json/jStationEntrances"
    TRAIN_POSITIONS = f"{BASE_URL}/TrainPositions/TrainPositions"
    STANDARD_ROUTES = f"{BASE_URL}/TrainPositions/StandardRoutes"
    TRACK_CIRCUITS = f"{BASE_URL}/TrainPositions/TrackCircuits"
    ELEVATOR_ESCALATOR_INCIDENTS = f"{BASE_URL}/Incidents.svc/json/ElevatorIncidents"
    INCIDENTS = f"{BASE_URL}/Incidents.svc/json/Incidents"
    STATIONS = f"{BASE_URL}/Rail.svc/json/jStations"
