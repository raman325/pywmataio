"""Station timings models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroRail
    from .station import Station


class TrainTimingData(TypedDict):
    """Train timing data for MetroRail WMATA API."""

    Time: str
    DestinationStation: str


@dataclass
class TrainTiming:
    """Train timing for MetroRail WMATA API."""

    client: "MetroRail"
    data: TrainTimingData
    time: time = field(init=False)
    destination_station_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.time = time.fromisoformat(self.data["Time"]).replace(tzinfo=TZ)
        self.destination_station_code = self.data["DestinationStation"]

    @property
    def destination_station(self) -> "Station":
        """Return the destination station."""
        return self.client.stations[self.destination_station_code]

    def to_dict(self) -> TrainTimingData:
        """Return dict representation."""
        return self.data


class DayTimeData(TypedDict):
    """Day time data for MetroRail WMATA API."""

    OpeningTime: str
    FirstTrains: list[TrainTimingData]
    LastTrains: list[TrainTimingData]


@dataclass
class DayTime:
    """Day time for MetroRail WMATA API."""

    client: "MetroRail"
    data: DayTimeData
    opening_time: time = field(init=False)
    first_trains: list[TrainTiming] = field(init=False)
    last_trains: list[TrainTiming] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.opening_time = time.fromisoformat(self.data["OpeningTime"]).replace(
            tzinfo=TZ
        )
        self.first_trains = [
            TrainTiming(self.client, train) for train in self.data["FirstTrains"]
        ]
        self.last_trains = [
            TrainTiming(self.client, train) for train in self.data["LastTrains"]
        ]

    def to_dict(self) -> DayTimeData:
        """Return dict representation."""
        return self.data


class StationTimeData(TypedDict):
    """Station time data for MetroRail WMATA API."""

    Code: str
    StationName: str
    Monday: DayTimeData
    Tuesday: DayTimeData
    Wednesday: DayTimeData
    Thursday: DayTimeData
    Friday: DayTimeData
    Saturday: DayTimeData
    Sunday: DayTimeData


@dataclass
class StationTime:
    """Station time for MetroRail WMATA API."""

    client: "MetroRail"
    data: StationTimeData
    code: str = field(init=False)
    name: str = field(init=False)
    days_of_week: dict[int, DayTime] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.code = self.data["Code"]
        self.name = self.data["StationName"]
        self.days_of_week = {
            1: DayTime(self.client, self.data["Monday"]),
            2: DayTime(self.client, self.data["Tuesday"]),
            3: DayTime(self.client, self.data["Wednesday"]),
            4: DayTime(self.client, self.data["Thursday"]),
            5: DayTime(self.client, self.data["Friday"]),
            6: DayTime(self.client, self.data["Saturday"]),
            7: DayTime(self.client, self.data["Sunday"]),
        }

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.client.stations[self.code]

    def get_day_time(self, date_: datetime | date) -> DayTime:
        """Return the day time for the given date."""
        return self.days_of_week[date_.isoweekday()]

    def to_dict(self) -> StationTimeData:
        """Return dict representation."""
        return self.data
