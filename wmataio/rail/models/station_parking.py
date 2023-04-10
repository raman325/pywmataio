"""Station parking information models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .. import MetroRail
    from .station import Station


class ShortTermParkingData(TypedDict):
    """Short-term parking data for MetroRail WMATA API."""

    TotalCount: int
    Notes: str | None


@dataclass
class ShortTermParking:
    """Short-term parking information for MetroRail WMATA API."""

    station_parking: StationParking
    data: ShortTermParkingData = field(repr=False)
    total_count: int = field(init=False)
    notes: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.total_count = self.data["TotalCount"]
        self.notes = self.data["Notes"] if self.data["Notes"] else None

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_parking)


class AllDayParkingData(TypedDict):
    """All-day parking data for MetroRail WMATA API."""

    TotalCount: int
    RiderCost: float | int
    NonRiderCost: float | int
    SaturdayRiderCost: float | int
    SaturdayNonRiderCost: float | int


@dataclass
class AllDayParking:
    """All-day parking information for MetroRail WMATA API."""

    station_parking: StationParking
    data: AllDayParkingData = field(repr=False)
    total_count: int = field(init=False)
    rider_cost: float | None = field(init=False, default=None)
    non_rider_cost: float | None = field(init=False, default=None)
    saturday_rider_cost: float | None = field(init=False, default=None)
    saturday_non_rider_cost: float | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post init."""
        self.total_count = self.data["TotalCount"]

        if rider_cost := self.data["RiderCost"]:
            self.rider_cost = float(rider_cost)
        if non_rider_cost := self.data["NonRiderCost"]:
            self.non_rider_cost = float(non_rider_cost)
        if saturday_rider_cost := self.data["SaturdayRiderCost"]:
            self.saturday_rider_cost = float(saturday_rider_cost)
        if saturday_non_rider_cost := self.data["SaturdayNonRiderCost"]:
            self.saturday_non_rider_cost = float(saturday_non_rider_cost)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.station_parking)


class StationParkingData(TypedDict):
    """Station parking data for MetroRail WMATA API."""

    Code: str
    Notes: str | None
    ShortTermParking: ShortTermParkingData
    AllDayParking: AllDayParkingData


@dataclass
class StationParking:
    """Station parking information for MetroRail WMATA API."""

    rail: "MetroRail" = field(repr=False)
    data: StationParkingData = field(repr=False)
    code: str = field(init=False)
    notes: str | None = field(init=False)
    short_term_parking: ShortTermParking = field(init=False)
    all_day_parking: AllDayParking = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.code = self.data["Code"]
        self.notes = self.data["Notes"] if self.data["Notes"] else None
        self.short_term_parking = ShortTermParking(self, self.data["ShortTermParking"])
        self.all_day_parking = AllDayParking(self, self.data["AllDayParking"])

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.station, self.code))

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.rail.stations[self.code]
