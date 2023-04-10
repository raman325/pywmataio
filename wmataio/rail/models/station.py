"""Station models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from ...models.coordinates import Coordinates
from .address import Address, AddressData

if TYPE_CHECKING:
    from .. import MetroRail
    from .line import Line
    from .station_entrance import StationEntrance
    from .station_parking import StationParking
    from .station_timings import StationTime


class StationData(TypedDict):
    """Station data for MetroRail WMATA API."""

    Address: "AddressData"
    Code: str
    Lat: float
    Lon: float
    LineCode1: str
    LineCode2: str | None
    LineCode3: str | None
    LineCode4: str | None
    Name: str
    StationTogether1: str
    StationTogether2: str


@dataclass
class Station:
    """MetroRail Station."""

    rail: "MetroRail" = field(repr=False)
    data: StationData = field(repr=False)
    parking: "StationParking" | None = field(repr=False)
    entrances: list["StationEntrance"] = field(repr=False)
    station_times: list["StationTime"] = field(repr=False)
    address: Address = field(init=False)
    station_code: str = field(init=False)
    coordinates: Coordinates = field(init=False)
    line_codes: list[str] = field(init=False)
    name: str = field(init=False)
    station_together_code_1: str | None = field(init=False)
    station_together_code_2: str | None = field(init=False)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_code)

    def __post_init__(self) -> None:
        """Post init."""
        self.address = Address(self.data["Address"])
        self.station_code = self.data["Code"]
        self.coordinates = Coordinates(self.data["Lat"], self.data["Lon"])
        self.line_codes = [
            self.data[f"LineCode{x}"]  # type: ignore
            for x in range(1, 5)
            if self.data[f"LineCode{x}"]  # type: ignore
        ]
        self.name = self.data["Name"]
        self.station_together_code_1 = (
            self.data["StationTogether1"] if self.data["StationTogether1"] else None
        )
        self.station_together_code_2 = (
            self.data["StationTogether2"] if self.data["StationTogether2"] else None
        )

    @property
    def lines(self) -> list["Line"]:
        """Return the lines."""
        return [self.rail.lines[line_code] for line_code in self.line_codes]

    @property
    def station_together_1(self) -> "Station" | None:
        """Return the station together 1."""
        if not self.station_together_code_1:
            return None
        return self.rail.stations[self.station_together_code_1]

    @property
    def station_together_2(self) -> "Station" | None:
        """Return the station together 2."""
        if not self.station_together_code_2:
            return None
        return self.rail.stations[self.station_together_code_2]
