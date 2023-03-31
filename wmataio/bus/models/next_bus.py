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

    bus: "MetroBus"
    data: NextBusData
    direction_number: int = field(init=False)
    direction_text: str = field(init=False)
    minutes: int = field(init=False)
    route_id: str = field(init=False)
    route: "Route" = field(init=False)
    trip_id: str = field(init=False)
    vehicle_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.direction_number = int(self.data["DirectionNum"])
        self.direction_text = self.data["DirectionText"]
        self.minutes = self.data["Minutes"]
        self.route_id = self.data["RouteID"]
        self.route = self.bus.routes[self.route_id]
        self.trip_id = self.data["TripID"]
        self.vehicle_id = self.data["VehicleID"]
