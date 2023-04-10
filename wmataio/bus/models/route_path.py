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

    data: ShapePointData = field(repr=False)
    coordinates: Coordinates = field(init=False)
    sequence_number: int = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.coordinates = Coordinates(float(self.data["Lat"]), float(self.data["Lon"]))
        self.sequence_number = int(self.data["SeqNum"])

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.coordinates, self.sequence_number))


class PathDirectionData(TypedDict):
    """Direction data for MetroBus WMATA API."""

    DirectionNum: int  # deprecated
    DirectionText: str
    Shape: list[ShapePointData]
    Stops: list["StopData"]
    TripHeadsign: str


@dataclass
class RoutePathDirection:
    """Direction for a Path."""

    route_path: RoutePath
    data: PathDirectionData = field(repr=False)
    direction_num: int
    direction: str = field(init=False)
    shapes: list[ShapePoint] = field(init=False, repr=False)
    stops_data: list["StopData"] = field(init=False, repr=False)
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

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.route_path, self.direction_num))

    @property
    def stops(self) -> list["Stop"]:
        """Return the stops."""
        return [
            self.route_path.bus.get_stop_from_stop_data(stop_data)
            for stop_data in self.stops_data
        ]


class RoutePathData(TypedDict):
    """Path data for MetroBus WMATA API."""

    RouteID: str
    Name: str
    Direction0: PathDirectionData | None
    Direction1: PathDirectionData | None


@dataclass
class RoutePath:
    """Path for a MetroBus."""

    bus: "MetroBus" = field(repr=False)
    data: RoutePathData = field(repr=False)
    route_id: str = field(init=False)
    name: str = field(init=False)
    path_directions: dict[int, RoutePathDirection] = field(
        init=False, default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        """Post init."""
        self.route_id = self.data["RouteID"]
        self.name = self.data["Name"]
        if (direction_data := self.data["Direction0"]) is not None:
            self.path_directions[0] = RoutePathDirection(self, direction_data, 0)
        if (direction_data := self.data["Direction1"]) is not None:
            self.path_directions[1] = RoutePathDirection(self, direction_data, 1)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.route)

    @property
    def route(self) -> "Route":
        """Return the route."""
        return self.bus.routes[self.route_id]
