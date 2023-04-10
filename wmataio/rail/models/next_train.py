"""NextTrain models for MetroRail WMATA API."""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .. import MetroRail
    from .line import Line
    from .station import Station


class NextTrainData(TypedDict):
    """NextTrain data for MetroRail WMATA API."""

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
class NextTrain:
    """NextTrain."""

    rail: "MetroRail" = field(repr=False)
    data: NextTrainData = field(repr=False)
    num_cars: int | None = field(init=False)
    destination: str = field(init=False)
    destination_station_code: str | None = field(init=False)
    destination_station_name: str | None = field(init=False)
    group: int = field(init=False)
    line_code: str | None = field(init=False)
    location_code: str = field(init=False)
    location_name: str = field(init=False)
    minutes: int | str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        if isinstance((car := self.data["Car"]), int) and car != 0:
            self.num_cars = int(car)
        else:
            self.num_cars = None
        self.destination = self.data["Destination"]
        self.destination_station_code = self.data["DestinationCode"]
        self.destination_station_name = self.data["DestinationName"]
        self.group = int(self.data["Group"])
        if (line_code := self.data["Line"]) in (None, "No"):
            self.line_code = None
        else:
            self.line_code = line_code
        self.location_code = self.data["LocationCode"]
        self.location_name = self.data["LocationName"]
        if (minutes := self.data["Min"]) in ("-", "---") or minutes is None:
            self.minutes = None
        else:
            self.minutes = minutes
            with suppress(ValueError):
                self.minutes = int(minutes)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.location, self.destination_station, self.line))

    @property
    def destination_station(self) -> "Station" | None:
        """Return the destination Station."""
        if not self.destination_station_code:
            return None
        return self.rail.stations[self.destination_station_code]

    @property
    def line(self) -> "Line" | None:
        """Return the Line."""
        if not self.line_code:
            return None
        return self.rail.lines[self.line_code]

    @property
    def location(self) -> "Station":
        """Return the location Station."""
        return self.rail.stations[self.location_code]
