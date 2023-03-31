"""Station entrance models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
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

    client: "MetroRail"
    data: StationEntranceData
    description: str = field(init=False)
    latitude: float = field(init=False)
    longitude: float = field(init=False)
    name: str = field(init=False)
    station_code_1: str = field(init=False)
    station_code_2: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.description = self.data["Description"]
        self.latitude = self.data["Lat"]
        self.longitude = self.data["Lon"]
        self.name = self.data["Name"]
        self.station_code_1 = self.data["StationCode1"]
        self.station_code_2 = self.data["StationCode2"]

    @property
    def station_1(self) -> "Station":
        """Return the station 1."""
        return self.client.stations[self.station_code_1]

    @property
    def station_2(self) -> "Station":
        """Return the station 2."""
        return self.client.stations[self.station_code_2]

    def to_dict(self) -> StationEntranceData:
        """Return the data as a dictionary."""
        return self.data
