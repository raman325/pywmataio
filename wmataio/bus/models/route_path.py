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
    stops_data: list["StopData"] = field(init=False)
    trip_headsign: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.direction = self.data["DirectionText"]
        self.shapes = sorted(
            [ShapePoint(shape_data) for shape_data in self.data["Shape"]],
            key=lambda shape: shape.sequence_number,
        )
        self.stops_data = self.data["Stops"]
        self.trip_headsign = self.data["TripHeadsign"]

    @property
    def stops(self) -> list["Stop"]:
        """Return the stops."""
        return [self.bus.stops[stop_data["StopID"]] for stop_data in self.stops_data]


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
    name: str = field(init=False)
    directions: dict[int, PathDirection] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Post init."""
        self.route_id = self.data["RouteID"]
        self.name = self.data["Name"]
        if (direction_data := self.data["Direction0"]) is not None:
            self.directions[0] = PathDirection(self.bus, direction_data, 0)
        if (direction_data := self.data["Direction1"]) is not None:
            self.directions[1] = PathDirection(self.bus, direction_data, 1)

    @property
    def route(self) -> list["Route"]:
        """Return the route."""
        return self.bus.routes[self.route_id]
