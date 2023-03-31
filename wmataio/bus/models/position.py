"""Bus position models for MetroBus API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route


class PositionData(TypedDict):
    """Bus position data for MetroBus API."""

    DateTime: str
    Deviation: float
    DirectionNum: int  # deprecated
    DirectionText: str
    Lat: float
    Lon: float
    RouteID: str
    TripEndTime: str
    TripHeadsign: str
    TripID: str
    TripStartTime: str
    VehicleID: str


@dataclass
class Position:
    """A MetroBus Bus Position."""

    client: "MetroBus"
    data: PositionData
    last_update: datetime = field(init=False)
    deviation: float = field(init=False)
    direction_text: str = field(init=False)
    latitude: float = field(init=False)
    longitude: float = field(init=False)
    route_id: str = field(init=False)
    route: "Route" = field(init=False)
    trip_end_time: datetime = field(init=False)
    trip_id: str = field(init=False)
    trip_start_time: datetime = field(init=False)
    vehicle_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.last_update = datetime.fromisoformat(self.data["DateTime"]).replace(
            tzinfo=TZ
        )
        self.latitude = self.data["Lat"]
        self.longitude = self.data["Lon"]
        self.route_id = self.data["RouteID"]
        self.route = self.client.routes[self.route_id]
        self.trip_end_time = datetime.fromisoformat(self.data["TripEndTime"]).replace(
            tzinfo=TZ
        )
        self.trip_id = self.data["TripID"]
        self.trip_start_time = datetime.fromisoformat(
            self.data["TripStartTime"]
        ).replace(tzinfo=TZ)
        self.vehicle_id = self.data["VehicleID"]

    def to_dict(self) -> PositionData:
        """Return the data as PositionData."""
        return self.data
