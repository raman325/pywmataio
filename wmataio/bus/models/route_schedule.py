"""Route schedule models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from .. import MetroBus
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

    direction_schedule: DirectionSchedule
    data: StopTimeData = field(repr=False)
    stop_id: str = field(init=False)
    stop_name: str = field(init=False)
    stop_sequence: int = field(init=False)
    time: datetime = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.stop_id = self.data["StopID"]
        self.stop_name = self.data["StopName"]
        self.stop_sequence = self.data["StopSeq"]
        self.time = datetime.fromisoformat(self.data["Time"]).replace(tzinfo=TZ)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.stop, self.direction_schedule))

    @property
    def stop(self) -> Stop:
        """Get stop."""
        return self.direction_schedule.route_schedule.bus.stops[self.stop_id]


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

    route_schedule: RouteSchedule
    data: DirectionScheduleData = field(repr=False)
    direction_num: int
    end_time: datetime = field(init=False)
    route_id: str = field(init=False, repr=False)
    route: Route = field(init=False)
    start_time: datetime = field(init=False)
    stop_times_data: list[StopTimeData] = field(init=False, repr=False)
    stop_times: list[StopTime] = field(init=False)
    trip_direction: str = field(init=False)
    trip_headsign: str = field(init=False)
    trip_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.end_time = datetime.fromisoformat(self.data["EndTime"]).replace(tzinfo=TZ)
        self.route_id = self.data["RouteID"]
        self.route = self.route_schedule.bus.routes[self.route_id]
        self.start_time = datetime.fromisoformat(self.data["StartTime"]).replace(
            tzinfo=TZ
        )
        self.stop_times_data = self.data["StopTimes"]
        self.stop_times = sorted(
            [StopTime(self, stop_time_data) for stop_time_data in self.stop_times_data],
            key=lambda stop_time: stop_time.stop_sequence,
        )
        self.trip_direction = self.data["TripDirectionText"]
        self.trip_headsign = self.data["TripHeadsign"]
        self.trip_id = self.data["TripID"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.direction_num, self.route, self.trip_id))


class RouteScheduleData(TypedDict):
    """Route schedule data for MetroBus WMATA API."""

    Direction0: list[DirectionScheduleData] | None
    Direction1: list[DirectionScheduleData] | None


@dataclass
class RouteSchedule:
    """Schedule for a Route."""

    bus: "MetroBus" = field(repr=False)
    route: "Route"
    data: RouteScheduleData = field(repr=False)
    directions_schedules: dict[int, list[DirectionSchedule]] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        """Post init."""
        if (direction_schedules_data := self.data["Direction0"]) is not None:
            self.directions_schedules[0] = sorted(
                [
                    DirectionSchedule(self, direction_schedule_data, 0)
                    for direction_schedule_data in direction_schedules_data
                ],
                key=lambda direction_schedule: direction_schedule.start_time,
            )
        if (direction_schedules_data := self.data["Direction1"]) is not None:
            self.directions_schedules[1] = sorted(
                [
                    DirectionSchedule(self, direction_schedule_data, 1)
                    for direction_schedule_data in direction_schedules_data
                ],
                key=lambda direction_schedule: direction_schedule.start_time,
            )

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.directions_schedules.values())
