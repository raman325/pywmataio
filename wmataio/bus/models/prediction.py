"""Prediction models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route


class NextPredictionData(TypedDict):
    """Next prediction data for MetroBus WMATA API."""

    DirectionNum: str
    DirectionText: str
    Minutes: int
    RouteID: str
    TripID: str
    VehicleID: str


@dataclass
class NextPrediction:
    """Next prediction for a Stop."""

    client: "MetroBus"
    data: NextPredictionData
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
        self.route = self.client.routes[self.route_id]
        self.trip_id = self.data["TripID"]
        self.vehicle_id = self.data["VehicleID"]

    def to_dict(self) -> NextPredictionData:
        """Return a dict representation of the NextPrediction."""
        return self.data
