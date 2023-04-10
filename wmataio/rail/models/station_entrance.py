"""Station entrance models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from ...models.coordinates import Coordinates

if TYPE_CHECKING:
    from .. import MetroRail
    from .station import Station


class StationEntranceData(TypedDict):
    """Station entrance data for MetroRail WMATA API."""

    Description: str
    ID: str
    Lat: float
    Lon: float
    Name: str
    StationCode1: str
    StationCode2: str


@dataclass
class StationEntrance:
    """Station entrance information for MetroRail WMATA API."""

    rail: "MetroRail" = field(repr=False)
    data: StationEntranceData = field(repr=False)
    description: str = field(init=False)
    entrance_id: str = field(init=False)
    coordinates: Coordinates = field(init=False)
    name: str = field(init=False)
    station_code_1: str = field(init=False)
    station_code_2: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.description = self.data["Description"]
        self.entrance_id = self.data["ID"]
        self.coordinates = Coordinates(self.data["Lat"], self.data["Lon"])
        self.name = self.data["Name"]
        self.station_code_1 = self.data["StationCode1"]
        self.station_code_2 = self.data["StationCode2"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.entrance_id)

    @property
    def station_1(self) -> "Station":
        """Return the station 1."""
        return self.rail.stations[self.station_code_1]

    @property
    def station_2(self) -> "Station":
        """Return the station 2."""
        return self.rail.stations[self.station_code_2]
