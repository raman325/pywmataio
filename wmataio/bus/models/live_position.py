"""Bus position models for MetroBus API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ
from ...models.coordinates import Coordinates

if TYPE_CHECKING:
    from .. import MetroBus
    from .route import Route


class LiveBusPositionData(TypedDict):
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
    BlockNumber: str


@dataclass
class LiveBusPosition:
    """A MetroBus Bus LiveBusPosition."""

    bus: "MetroBus" = field(repr=False)
    data: LiveBusPositionData = field(repr=False)
    last_update: datetime = field(init=False)
    deviation: float = field(init=False)
    direction_text: str = field(init=False)
    coordinates: Coordinates = field(init=False)
    route_id: str = field(init=False)
    trip_end_time: datetime = field(init=False)
    trip_headsign: str = field(init=False)
    trip_id: str = field(init=False)
    trip_start_time: datetime = field(init=False)
    vehicle_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.last_update = datetime.fromisoformat(self.data["DateTime"]).replace(
            tzinfo=TZ
        )
        self.deviation = self.data["Deviation"]
        self.direction_text = self.data["DirectionText"]
        self.coordinates = Coordinates(self.data["Lat"], self.data["Lon"])
        self.route_id = self.data["RouteID"]
        self.trip_end_time = datetime.fromisoformat(self.data["TripEndTime"]).replace(
            tzinfo=TZ
        )
        self.trip_headsign = self.data["TripHeadsign"]
        self.trip_id = self.data["TripID"]
        self.trip_start_time = datetime.fromisoformat(
            self.data["TripStartTime"]
        ).replace(tzinfo=TZ)
        self.vehicle_id = self.data["VehicleID"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.vehicle_id, self.trip_id))

    @property
    def route(self) -> "Route":
        """Get route."""
        return self.bus.routes[self.route_id]
