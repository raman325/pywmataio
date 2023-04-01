"""Station to station path models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .. import MetroRail
    from .line import Line
    from .station import Station


class PathItemData(TypedDict):
    """Path item data for MetroRail WMATA API."""

    DistanceToPrev: int
    LineCode: str
    SeqNum: int
    StationCode: str
    StationName: str


@dataclass
class PathItem:
    """MetroRail Path Item."""

    bus: "MetroRail"
    data: PathItemData
    distance_to_previous: int = field(init=False)
    line_code: str = field(init=False)
    sequence_number: int = field(init=False)
    station_code: str = field(init=False)
    station_name: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.distance_to_previous = self.data["DistanceToPrev"]
        self.line_code = self.data["LineCode"]
        self.sequence_number = self.data["SeqNum"]
        self.station_code = self.data["StationCode"]
        self.station_name = self.data["StationName"]

    @property
    def line(self) -> "Line":
        """Return the line."""
        return self.bus.lines[self.line_code]

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.bus.stations[self.station_code]


class StationToStationPathData(TypedDict):
    """Station to station path data for MetroRail WMATA API."""

    Path: list[PathItemData]


class RailFareData(TypedDict):
    """Rail fare data for MetroRail WMATA API."""

    OffPeakTime: float | int
    PeakTime: float | int
    SeniorDisabled: float | int


@dataclass
class RailFare:
    """MetroRail Rail Fare."""

    data: RailFareData
    off_peak_time: float = field(init=False)
    peak_time: float = field(init=False)
    senior_disabled: float = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.off_peak_time = float(self.data["OffPeakTime"])
        self.peak_time = float(self.data["PeakTime"])
        self.senior_disabled = float(self.data["SeniorDisabled"])


class StationToStationInfoData(TypedDict):
    """Station to station info data for MetroRail WMATA API."""

    CompositeMiles: float | int
    DestinationStation: str
    RailFare: RailFareData
    RailTime: str
    SourceStation: str


@dataclass
class StationToStationInformation:
    """MetroRail Station to Station Info."""

    bus: "MetroRail"
    data: StationToStationInfoData
    composite_miles: float = field(init=False)
    destination_station_code: str = field(init=False)
    rail_fare: RailFare = field(init=False)
    rail_time: str = field(init=False)
    source_station_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.composite_miles = float(self.data["CompositeMiles"])
        self.destination_station_code = self.data["DestinationStation"]
        self.rail_fare = RailFare(self.data["RailFare"])
        self.rail_time = self.data["RailTime"]
        self.source_station_code = self.data["SourceStation"]

    @property
    def destination_station(self) -> "Station":
        """Return the destination station."""
        return self.bus.stations[self.destination_station_code]

    @property
    def source_station(self) -> "Station":
        """Return the source station."""
        return self.bus.stations[self.source_station_code]


class StationToStationData(TypedDict):
    """Station to station data for MetroRail WMATA API."""

    path: StationToStationPathData
    info: StationToStationInfoData


@dataclass
class StationToStation:
    """MetroRail Station to Station."""

    bus: "MetroRail"
    path_data: StationToStationPathData
    info_data: list[StationToStationInfoData]
    path: list[PathItem] = field(init=False)
    info: list[StationToStationInformation] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.path = sorted(
            [PathItem(self.bus, item_data) for item_data in self.path_data["Path"]],
            key=lambda item: item.sequence_number,
        )
        self.info = [
            StationToStationInformation(self.bus, station_info_data)
            for station_info_data in self.info_data
        ]
