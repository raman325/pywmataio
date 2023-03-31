"""Station to station path models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
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

    client: "MetroRail"
    data: PathItemData
    distance_to_prev: int = field(init=False)
    line_code: str = field(init=False)
    seq_num: int = field(init=False)
    station_code: str = field(init=False)
    station_name: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.distance_to_prev = self.data["DistanceToPrev"]
        self.line_code = self.data["LineCode"]
        self.seq_num = self.data["SeqNum"]
        self.station_code = self.data["StationCode"]
        self.station_name = self.data["StationName"]

    @property
    def line(self) -> "Line":
        """Return the line."""
        return self.client.lines[self.line_code]

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.client.stations[self.station_code]

    def to_dict(self) -> PathItemData:
        """Return the data as a dict."""
        return self.data


@dataclass
class SimplifiedStationToStationPath:
    """Station to station simplified path data for MetroRail WMATA API."""

    from_station: "Station"
    to_station: "Station"
    line: "Line"


class StationToStationPathData(TypedDict):
    """Station to station path data for MetroRail WMATA API."""

    Path: list[PathItemData]


@dataclass
class StationToStationPath:
    """MetroRail Station to Station Path."""

    client: "MetroRail"
    data: StationToStationPathData
    path: list[PathItem] = field(init=False)
    simplified_path: list[SimplifiedStationToStationPath] = field(
        init=False, default_factory=list
    )

    def __post_init__(self) -> None:
        """Post init."""
        self.path = sorted(
            [PathItem(self.client, item_data) for item_data in self.data["Path"]],
            key=lambda item: item.seq_num,
        )

        from_station = self.path[0].station
        line = self.path[0].line
        to_station = self.path[0].station
        for i in range(1, len(self.path)):
            if i + 1 == len(self.path):
                self.simplified_path.append(
                    SimplifiedStationToStationPath(
                        from_station=from_station,
                        to_station=to_station,
                        line=line,
                    )
                )
            elif self.path[i + 1].line == line:
                to_station = self.path[i].station
            else:
                self.simplified_path.append(
                    SimplifiedStationToStationPath(
                        from_station=from_station,
                        to_station=to_station,
                        line=line,
                    )
                )
                from_station = self.path[i].station
                line = self.path[i].line
                to_station = self.path[i + 1].station

    def to_dict(self) -> StationToStationPathData:
        """Return the data as a dict."""
        return {
            "Path": [item.to_dict() for item in self.path],
        }


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

    def to_dict(self) -> RailFareData:
        """Return the data as a dict."""
        return self.data


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

    client: "MetroRail"
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
        return self.client.stations[self.destination_station_code]

    @property
    def source_station(self) -> "Station":
        """Return the source station."""
        return self.client.stations[self.source_station_code]

    def to_dict(self) -> StationToStationInfoData:
        """Return the data as a dict."""
        return self.data


class StationToStationData(TypedDict):
    """Station to station data for MetroRail WMATA API."""

    path: StationToStationPathData
    info: StationToStationInfoData


@dataclass
class StationToStation:
    """MetroRail Station to Station."""

    client: "MetroRail"
    path_data: StationToStationPathData
    info_data: StationToStationInfoData
    path: StationToStationPath = field(init=False)
    info: StationToStationInformation = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.path = StationToStationPath(self.client, self.path_data)
        self.info = StationToStationInformation(self.client, self.info_data)

    def to_dict(self) -> StationToStationData:
        """Return the data as a dict."""
        return {"path": self.path_data, "info": self.info_data}
