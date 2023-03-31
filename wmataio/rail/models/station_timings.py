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

    bus: "MetroRail"
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
        return self.bus.stations[self.destination_station_code]


class DayTimeData(TypedDict):
    """Day time data for MetroRail WMATA API."""

    OpeningTime: str
    FirstTrains: list[TrainTimingData]
    LastTrains: list[TrainTimingData]


@dataclass
class DayTime:
    """Day time for MetroRail WMATA API."""

    bus: "MetroRail"
    data: DayTimeData
    day: str
    day_of_week: int
    opening_time: time = field(init=False)
    first_trains: list[TrainTiming] = field(init=False)
    last_trains: list[TrainTiming] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.opening_time = time.fromisoformat(self.data["OpeningTime"]).replace(
            tzinfo=TZ
        )
        self.first_trains = [
            TrainTiming(self.bus, train) for train in self.data["FirstTrains"]
        ]
        self.last_trains = [
            TrainTiming(self.bus, train) for train in self.data["LastTrains"]
        ]


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

    bus: "MetroRail"
    data: StationTimeData
    station_code: str = field(init=False)
    name: str = field(init=False)
    days_of_week: dict[int, DayTime] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.station_code = self.data["Code"]
        self.name = self.data["StationName"]
        self.days_of_week = {
            1: DayTime(self.bus, self.data["Monday"], "Monday", 1),
            2: DayTime(self.bus, self.data["Tuesday"], "Tuesday", 2),
            3: DayTime(self.bus, self.data["Wednesday"], "Wednesday", 3),
            4: DayTime(self.bus, self.data["Thursday"], "Thursday", 4),
            5: DayTime(self.bus, self.data["Friday"], "Friday", 5),
            6: DayTime(self.bus, self.data["Saturday"], "Saturday", 6),
            7: DayTime(self.bus, self.data["Sunday"], "Sunday", 7),
        }

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.bus.stations[self.station_code]

    def get_day_time(self, date_: datetime | date) -> DayTime:
        """Return the day time for the given date."""
        return self.days_of_week[date_.isoweekday()]
