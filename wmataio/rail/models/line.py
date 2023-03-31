"""Line models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from .standard_route import StandardRouteData

if TYPE_CHECKING:
    from ..client import MetroRail
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


class LineDataWithExtraInfo(LineData):
    """Station data with extra info for MetroRail WMATA API."""

    standard_routes: list[StandardRouteData]


@dataclass
class Line:
    """MetroRail Line."""

    client: "MetroRail"
    data: LineData
    standard_routes: list["StandardRoute"]
    display_name: str = field(init=False)
    start_station_code: str = field(init=False)
    end_station_code: str = field(init=False)
    internal_destination_code_1: str = field(init=False)
    internal_destination_code_2: str = field(init=False)
    line_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.line_id = self.data["LineCode"]
        self.display_name = self.data["DisplayName"]
        self.start_station_code = self.data["StartStationCode"]
        self.end_station_code = self.data["EndStationCode"]
        self.internal_destination_code_1 = self.data["InternalDestination1"]
        self.internal_destination_code_2 = self.data["InternalDestination2"]

    @property
    def start_station(self) -> "Station":
        """Return the start station."""
        return self.client.stations[self.start_station_code]

    @property
    def end_station(self) -> "Station":
        """Return the end station."""
        return self.client.stations[self.end_station_code]

    @property
    def internal_destination_1(self) -> "Station" | None:
        """Return the internal destination 1."""
        if not self.internal_destination_code_1:
            return None
        return self.client.stations[self.internal_destination_code_1]

    @property
    def internal_destination_2(self) -> "Station" | None:
        """Return the internal destination 2."""
        if not self.internal_destination_code_2:
            return None
        return self.client.stations[self.internal_destination_code_2]

    def to_dict(self) -> LineDataWithExtraInfo:
        """Return a dict representation of the Line."""
        return {
            **self.data,  # type: ignore
            "standard_routes": [route.to_dict() for route in self.standard_routes],
        }
