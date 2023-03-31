"""Stop schedule models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route
    from .stop import Stop


class StopArrivalScheduleData(TypedDict):
    """ArrivalSchedule data for MetroBus WMATA API."""

    DirectionNum: str
    EndTime: str
    RouteID: str
    ScheduleTime: str
    StartTime: str
    TripDirectionText: str
    TripHeadsign: str
    TripID: str


@dataclass
class StopArrivalSchedule:
    """Stop Time for a Route Schedule."""

    client: "MetroBus"
    stop: "Stop"
    data: StopArrivalScheduleData
    direction_number: int = field(init=False)
    end_time: datetime = field(init=False)
    route_id: str = field(init=False)
    route: "Route" = field(init=False)
    schedule_time: datetime = field(init=False)
    start_time: datetime = field(init=False)
    trip_direction_text: str = field(init=False)
    trip_headsign: str = field(init=False)
    trip_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.direction_number = int(self.data["DirectionNum"])
        self.end_time = datetime.fromisoformat(self.data["EndTime"]).replace(tzinfo=TZ)
        self.route_id = self.data["RouteID"]
        self.route = self.client.routes[self.route_id]
        self.schedule_time = datetime.fromisoformat(self.data["ScheduleTime"]).replace(
            tzinfo=TZ
        )
        self.start_time = datetime.fromisoformat(self.data["StartTime"]).replace(
            tzinfo=TZ
        )
        self.trip_direction_text = self.data["TripDirectionText"]
        self.trip_headsign = self.data["TripHeadsign"]
        self.trip_id = self.data["TripID"]

    def to_dict(self) -> StopArrivalScheduleData:
        """Return a dict representation of the StopArrivalScheduleData."""
        return self.data
