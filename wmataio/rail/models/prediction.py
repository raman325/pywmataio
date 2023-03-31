"""Prediction models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
    from .line import Line
    from .station import Station


class PredictionData(TypedDict):
    """Prediction data for MetroRail WMATA API."""

    Car: int | str | None
    Destination: str
    DestinationCode: str | None
    DestinationName: str | None
    Group: str
    Line: str
    LocationCode: str
    LocationName: str
    Min: int | str | None


@dataclass
class Prediction:
    """Prediction."""

    client: "MetroRail"
    data: PredictionData
    car: int | None = field(init=False)
    destination: str = field(init=False)
    destination_code: str | None = field(init=False)
    destination_name: str | None = field(init=False)
    group: int = field(init=False)
    line_id: str | None = field(init=False)
    location_code: str = field(init=False)
    location_name: str = field(init=False)
    minutes: int | str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        if isinstance((car := self.data["Car"]), int) and car != 0:
            self.car = int(car)
        else:
            self.car = None
        self.destination = self.data["Destination"]
        self.destination_code = self.data["DestinationCode"]
        self.destination_name = self.data["DestinationName"]
        self.group = int(self.data["Group"])
        if (line_id := self.data["Line"]) in (None, "No"):
            self.line_id = None
        else:
            self.line_id = line_id
        self.location_code = self.data["LocationCode"]
        self.location_name = self.data["LocationName"]
        if (minutes := self.data["Min"]) in (None, "-", "---"):
            self.minutes = None
        else:
            self.minutes = minutes

    @property
    def destination_station(self) -> "Station" | None:
        """Return the destination Station."""
        if not self.destination_code:
            return None
        return self.client.stations[self.destination_code]

    @property
    def line(self) -> "Line" | None:
        """Return the Line."""
        if not self.line_id:
            return None
        return self.client.lines[self.line_id]

    @property
    def location(self) -> "Station":
        """Return the location Station."""
        return self.client.stations[self.location_code]
