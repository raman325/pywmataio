"""Train position models for MetroRail API."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .. import MetroRail
    from .line import Line
    from .station import Station


class TrainDirection(IntEnum):
    """Enum for all known train directions."""

    NORTHBOUND_OR_EASTBOUND = 1
    SOUTHBOUND_OR_WESTBOUND = 2


class LiveTrainPositionData(TypedDict):
    """Train position data for MetroRail API."""

    CarCount: int
    CircuitId: int
    DestinationStationCode: str | None
    DirectionNum: int
    LineCode: str
    SecondsAtLocation: int
    ServiceType: Literal["NoPassengers", "Normal", "Special", "Unknown"]
    TrainId: str
    TrainNumber: str


@dataclass
class LiveTrainPosition:
    """A MetroRail Bus LiveTrainPosition."""

    rail: "MetroRail" = field(repr=False)
    data: LiveTrainPositionData = field(repr=False)
    car_count: int = field(init=False)
    circuit_id: int = field(init=False)
    destination_station_code: str | None = field(init=False)
    direction: TrainDirection = field(init=False)
    line_code: str = field(init=False)
    seconds_at_location: int = field(init=False)
    service_type: Literal["NoPassengers", "Normal", "Special", "Unknown"] = field(
        init=False
    )
    train_id: str = field(init=False)
    train_number: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.car_count = self.data["CarCount"]
        self.circuit_id = self.data["CircuitId"]
        self.destination_station_code = self.data["DestinationStationCode"]
        self.direction = TrainDirection(self.data["DirectionNum"])
        self.line_code = self.data["LineCode"]
        self.seconds_at_location = self.data["SecondsAtLocation"]
        self.service_type = self.data["ServiceType"]
        self.train_id = self.data["TrainId"]
        self.train_number = self.data["TrainNumber"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(
            (self.train_id, self.circuit_id, self.line, self.destination_station)
        )

    @property
    def destination_station(self) -> "Station" | None:
        """Return the destination station."""
        if not self.destination_station_code:
            return None
        return self.rail.stations[self.destination_station_code]

    @property
    def line(self) -> "Line" | None:
        """Return the line."""
        if not self.line_code:
            return None
        return self.rail.lines[self.line_code]
