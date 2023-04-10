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

    station_to_station: StationToStation
    data: PathItemData = field(repr=False)
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

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_to_station)

    @property
    def line(self) -> "Line":
        """Return the line."""
        return self.station_to_station.rail.lines[self.line_code]

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.station_to_station.rail.stations[self.station_code]


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

    station_to_station_information: StationToStationInformation
    data: RailFareData = field(repr=False)
    off_peak_time: float = field(init=False)
    peak_time: float = field(init=False)
    senior_disabled: float = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.off_peak_time = float(self.data["OffPeakTime"])
        self.peak_time = float(self.data["PeakTime"])
        self.senior_disabled = float(self.data["SeniorDisabled"])

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_to_station_information)


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

    station_to_station: StationToStation
    data: StationToStationInfoData = field(repr=False)
    composite_miles: float = field(init=False)
    destination_station_code: str = field(init=False)
    rail_fare: RailFare = field(init=False)
    rail_time: str = field(init=False)
    source_station_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.composite_miles = float(self.data["CompositeMiles"])
        self.destination_station_code = self.data["DestinationStation"]
        self.rail_fare = RailFare(self, self.data["RailFare"])
        self.rail_time = self.data["RailTime"]
        self.source_station_code = self.data["SourceStation"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_to_station)

    @property
    def destination_station(self) -> "Station":
        """Return the destination station."""
        return self.station_to_station.rail.stations[self.destination_station_code]

    @property
    def source_station(self) -> "Station":
        """Return the source station."""
        return self.station_to_station.rail.stations[self.source_station_code]


class StationToStationData(TypedDict):
    """Station to station data for MetroRail WMATA API."""

    path: StationToStationPathData
    info: StationToStationInfoData


@dataclass
class StationToStation:
    """MetroRail Station to Station."""

    rail: "MetroRail" = field(repr=False)
    from_station: "Station"
    to_station: "Station"
    path_data: StationToStationPathData = field(repr=False)
    info_data: list[StationToStationInfoData] = field(repr=False)
    path: list[PathItem] = field(init=False)
    info: list[StationToStationInformation] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.path = sorted(
            [PathItem(self, item_data) for item_data in self.path_data["Path"]],
            key=lambda item: item.sequence_number,
        )
        self.info = [
            StationToStationInformation(self, station_info_data)
            for station_info_data in self.info_data
        ]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.from_station, self.to_station))
