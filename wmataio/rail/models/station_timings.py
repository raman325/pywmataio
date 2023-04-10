"""Station timings models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from .. import MetroRail
    from .station import Station


class TrainTimingData(TypedDict):
    """Train timing data for MetroRail WMATA API."""

    Time: str
    DestinationStation: str


@dataclass
class TrainTiming:
    """Train timing for MetroRail WMATA API."""

    day_time: DayTime
    data: TrainTimingData = field(repr=False)
    time: time = field(init=False)
    destination_station_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.time = time.fromisoformat(self.data["Time"]).replace(tzinfo=TZ)
        self.destination_station_code = self.data["DestinationStation"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.day_time, self.destination_station))

    @property
    def destination_station(self) -> "Station":
        """Return the destination station."""
        return self.day_time.station_time.rail.stations[self.destination_station_code]


class DayTimeData(TypedDict):
    """Day time data for MetroRail WMATA API."""

    OpeningTime: str
    FirstTrains: list[TrainTimingData]
    LastTrains: list[TrainTimingData]


@dataclass
class DayTime:
    """Day time for MetroRail WMATA API."""

    station_time: StationTime
    data: DayTimeData = field(repr=False)
    day: str
    day_of_week: int = field(repr=False)
    opening_time: time = field(init=False)
    first_trains: list[TrainTiming] = field(init=False)
    last_trains: list[TrainTiming] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.opening_time = time.fromisoformat(self.data["OpeningTime"]).replace(
            tzinfo=TZ
        )
        self.first_trains = [
            TrainTiming(self, train) for train in self.data["FirstTrains"]
        ]
        self.last_trains = [
            TrainTiming(self, train) for train in self.data["LastTrains"]
        ]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.station_time, self.day))


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

    rail: "MetroRail" = field(repr=False)
    data: StationTimeData = field(repr=False)
    station_code: str = field(init=False)
    name: str = field(init=False)
    days_of_week: dict[int, DayTime] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.station_code = self.data["Code"]
        self.name = self.data["StationName"]
        self.days_of_week = {
            1: DayTime(self, self.data["Monday"], "Monday", 1),
            2: DayTime(self, self.data["Tuesday"], "Tuesday", 2),
            3: DayTime(self, self.data["Wednesday"], "Wednesday", 3),
            4: DayTime(self, self.data["Thursday"], "Thursday", 4),
            5: DayTime(self, self.data["Friday"], "Friday", 5),
            6: DayTime(self, self.data["Saturday"], "Saturday", 6),
            7: DayTime(self, self.data["Sunday"], "Sunday", 7),
        }

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station)

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.rail.stations[self.station_code]

    def get_day_time(self, date_: datetime | date) -> DayTime:
        """Return the day time for the given date."""
        return self.days_of_week[date_.isoweekday()]
