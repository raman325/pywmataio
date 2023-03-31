"""Path models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from ...models.coordinates import Coordinates

if TYPE_CHECKING:
    from .. import MetroBus
    from .route import Route
    from .stop import Stop, StopData


class ShapePointData(TypedDict):
    """ShapePoint data for MetroBus WMATA API."""

    Lat: float | int
    Lon: float | int
    SeqNum: str


@dataclass
class ShapePoint:
    """ShapePoint for a Path."""

    data: ShapePointData
    coordinates: Coordinates = field(init=False)
    sequence_number: int = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.coordinates = Coordinates(float(self.data["Lat"]), float(self.data["Lon"]))
        self.sequence_number = int(self.data["SeqNum"])


class PathDirectionData(TypedDict):
    """Direction data for MetroBus WMATA API."""

    DirectionNum: int  # deprecated
    DirectionText: str
    Shape: list[ShapePointData]
    Stops: list["StopData"]
    TripHeadsign: str


@dataclass
class PathDirection:
    """Direction for a Path."""

    bus: "MetroBus"
    data: PathDirectionData
    direction_num: int
    direction: str = field(init=False)
    shapes: list[ShapePoint] = field(init=False)
    stops: list["Stop"] = field(init=False)
    trip_headsign: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.direction = self.data["DirectionText"]
        self.shapes = sorted(
            [ShapePoint(shape_data) for shape_data in self.data["Shape"]],
            key=lambda shape: shape.sequence_number,
        )
        self.stops = [
            self.bus.get_stop_from_stop_data(stop_data)
            for stop_data in self.data["Stops"]
        ]
        self.trip_headsign = self.data["TripHeadsign"]


class RoutePathData(TypedDict):
    """Path data for MetroBus WMATA API."""

    RouteID: str
    Name: str
    Direction0: PathDirectionData | None
    Direction1: PathDirectionData | None


@dataclass
class RoutePath:
    """Path for a MetroBus."""

    bus: "MetroBus"
    data: RoutePathData
    route_id: str = field(init=False)
    route: "Route" = field(init=False)
    name: str = field(init=False)
    directions: dict[int, PathDirection] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Post init."""
        self.route_id = self.data["RouteID"]
        self.route = self.bus.routes[self.route_id]
        self.name = self.data["Name"]
        if (direction_data := self.data["Direction0"]) is not None:
            self.directions[0] = PathDirection(self.bus, direction_data, 0)
        if (direction_data := self.data["Direction1"]) is not None:
            self.directions[1] = PathDirection(self.bus, direction_data, 1)
