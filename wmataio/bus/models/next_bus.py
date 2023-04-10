"""NextBus models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .. import MetroBus
    from .route import Route


class NextBusData(TypedDict):
    """Next prediction data for MetroBus WMATA API."""

    DirectionNum: str
    DirectionText: str
    Minutes: int
    RouteID: str
    TripID: str
    VehicleID: str


@dataclass
class NextBus:
    """Next bus for a Stop."""

    bus: "MetroBus" = field(repr=False)
    data: NextBusData = field(repr=False)
    direction_number: int = field(init=False)
    direction_text: str = field(init=False)
    minutes: int = field(init=False)
    route_id: str = field(init=False)
    trip_id: str = field(init=False)
    vehicle_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.direction_number = int(self.data["DirectionNum"])
        self.direction_text = self.data["DirectionText"]
        self.minutes = self.data["Minutes"]
        self.route_id = self.data["RouteID"]
        self.trip_id = self.data["TripID"]
        self.vehicle_id = self.data["VehicleID"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.vehicle_id, self.trip_id, self.route, self.direction_number))

    @property
    def route(self) -> "Route":
        """Return the route."""
        return self.bus.routes[self.route_id]
