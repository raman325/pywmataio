"""Route schedule models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route
    from .stop import Stop


class StopTimeData(TypedDict):
    """StopTime data for MetroBus WMATA API."""

    StopID: str
    StopName: str
    StopSeq: int
    Time: str


@dataclass
class StopTime:
    """Stop Time for a Route Schedule."""

    client: "MetroBus"
    data: StopTimeData
    stop_id: str = field(init=False)
    stop_name: str = field(init=False)
    stop: Stop = field(init=False)
    stop_sequence: int = field(init=False)
    time: datetime = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.stop_id = self.data["StopID"]
        self.stop_name = self.data["StopName"]
        self.stop = self.client.get_stop_from_stop_data(
            {"StopID": self.stop_id, "Name": self.stop_name}
        )
        self.stop_sequence = self.data["StopSeq"]
        self.time = datetime.fromisoformat(self.data["Time"]).replace(tzinfo=TZ)

    def to_dict(self) -> StopTimeData:
        """Return a dict representation of the StopTime."""
        return self.data


class DirectionScheduleData(TypedDict):
    """DirectionSchedule data for MetroBus WMATA API."""

    DirectionNum: int  # deprecated
    EndTime: str
    RouteID: str
    StartTime: str
    StopTimes: list[StopTimeData]
    TripDirectionText: str
    TripHeadsign: str
    TripID: str


@dataclass
class DirectionSchedule:
    """Direction Schedule for a Path."""

    client: "MetroBus"
    data: DirectionScheduleData
    direction_num: int
    end_time: datetime = field(init=False)
    route_id: str = field(init=False)
    route: Route = field(init=False)
    start_time: datetime = field(init=False)
    stop_times: list[StopTime] = field(init=False)
    trip_direction: str = field(init=False)
    trip_headsign: str = field(init=False)
    trip_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.end_time = datetime.fromisoformat(self.data["EndTime"]).replace(tzinfo=TZ)
        self.route_id = self.data["RouteID"]
        self.route = self.client.routes[self.route_id]
        self.start_time = datetime.fromisoformat(self.data["StartTime"]).replace(
            tzinfo=TZ
        )
        self.stop_times = sorted(
            [
                StopTime(self.client, stop_time_data)
                for stop_time_data in self.data["StopTimes"]
            ],
            key=lambda stop_time: stop_time.stop_sequence,
        )
        self.trip_direction = self.data["TripDirectionText"]
        self.trip_headsign = self.data["TripHeadsign"]
        self.trip_id = self.data["TripID"]

    def to_dict(self) -> DirectionScheduleData:
        """Return a dict representation of the DirectionSchedule."""
        return self.data


class RouteScheduleData(TypedDict):
    """Route schedule data for MetroBus WMATA API."""

    Direction0: DirectionScheduleData | None
    Direction1: DirectionScheduleData | None


@dataclass
class RouteSchedule:
    """Schedule for a Route."""

    client: "MetroBus"
    route: "Route"
    data: RouteScheduleData
    direction_schedules: dict[int, DirectionSchedule] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        """Post init."""
        if (direction_data := self.data["Direction0"]) is not None:
            self.direction_schedules[0] = DirectionSchedule(
                self.client, direction_data, 0
            )
        if (direction_data := self.data["Direction1"]) is not None:
            self.direction_schedules[1] = DirectionSchedule(
                self.client, direction_data, 1
            )

    def to_dict(self) -> RouteScheduleData:
        """Return a dict representation of the RouteSchedule."""
        return self.data
