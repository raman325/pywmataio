"""Constants for MetroRail API."""
from __future__ import annotations

from enum import Enum

from ..const import BASE_URL


class RailEndpoint(Enum):
    """Endpoints for all MetroRail endpoints."""

    ELEVATOR_ESCALATOR_INCIDENTS = f"{BASE_URL}/Incidents.svc/json/ElevatorIncidents"
    RAIL_INCIDENTS = f"{BASE_URL}/Incidents.svc/json/Incidents"
    LINES = f"{BASE_URL}/Rail.svc/json/jLines"
    NEXT_TRAINS = f"{BASE_URL}/StationNextTrain.svc/json/GetNextTrain"
    STANDARD_ROUTES = f"{BASE_URL}/TrainPositions/StandardRoutes"
    STATION_ENTRANCES = f"{BASE_URL}/Rail.svc/json/jStationEntrances"
    STATION_INFORMATION = f"{BASE_URL}/Rail.svc/json/jStationInfo"
    STATION_PARKING_INFORMATION = f"{BASE_URL}/Rail.svc/json/jStationParking"
    STATION_TIMINGS = f"{BASE_URL}/Rail.svc/json/jStationTimes"
    STATION_TO_STATION_INFO = f"{BASE_URL}/Rail.svc/json/jSrcStationToDstStationInfo"
    STATION_TO_STATION_PATH = f"{BASE_URL}/Rail.svc/json/jPath"
    STATIONS = f"{BASE_URL}/Rail.svc/json/jStations"
    TRACK_CIRCUITS = f"{BASE_URL}/TrainPositions/TrackCircuits"
    TRAIN_POSITIONS = f"{BASE_URL}/TrainPositions/TrainPositions"
