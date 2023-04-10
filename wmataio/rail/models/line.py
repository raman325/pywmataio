"""Line models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .. import MetroRail
    from .standard_route import StandardRoute
    from .station import Station


class LineData(TypedDict):
    """Line data for MetroRail WMATA API."""

    DisplayName: str
    StartStationCode: str
    EndStationCode: str
    InternalDestination1: str
    InternalDestination2: str
    LineCode: str


@dataclass
class Line:
    """MetroRail Line."""

    rail: "MetroRail" = field(repr=False)
    data: LineData = field(repr=False)
    standard_routes: list["StandardRoute"] = field(repr=False)
    display_name: str = field(init=False)
    start_station_code: str = field(init=False)
    end_station_code: str = field(init=False)
    internal_destination_code_1: str | None = field(init=False, default=None)
    internal_destination_code_2: str | None = field(init=False, default=None)
    line_code: str = field(init=False)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.line_code)

    def __post_init__(self) -> None:
        """Post init."""
        self.line_code = self.data["LineCode"]
        self.display_name = self.data["DisplayName"]
        self.start_station_code = self.data["StartStationCode"]
        self.end_station_code = self.data["EndStationCode"]
        if internal_destination_1 := self.data["InternalDestination1"]:
            self.internal_destination_code_1 = internal_destination_1
        if internal_destination_2 := self.data["InternalDestination2"]:
            self.internal_destination_code_2 = internal_destination_2

    @property
    def start_station(self) -> "Station":
        """Return the start station."""
        return self.rail.stations[self.start_station_code]

    @property
    def end_station(self) -> "Station":
        """Return the end station."""
        return self.rail.stations[self.end_station_code]

    @property
    def internal_destination_1(self) -> "Station" | None:
        """Return the internal destination 1."""
        if not self.internal_destination_code_1:
            return None
        return self.rail.stations[self.internal_destination_code_1]

    @property
    def internal_destination_2(self) -> "Station" | None:
        """Return the internal destination 2."""
        if not self.internal_destination_code_2:
            return None
        return self.rail.stations[self.internal_destination_code_2]
