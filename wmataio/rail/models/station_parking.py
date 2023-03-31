"""Station parking information models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
    from .station import Station


class ShortTermParkingData(TypedDict):
    """Short-term parking data for MetroRail WMATA API."""

    TotalCount: int
    Notes: str | None


@dataclass
class ShortTermParking:
    """Short-term parking information for MetroRail WMATA API."""

    data: ShortTermParkingData
    total_count: int = field(init=False)
    notes: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.total_count = self.data["TotalCount"]
        self.notes = self.data["Notes"] if self.data["Notes"] else None

    def to_dict(self) -> ShortTermParkingData:
        """Return the data as a dictionary."""
        return self.data


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

    data: AllDayParkingData
    total_count: int = field(init=False)
    rider_cost: float = field(init=False)
    non_rider_cost: float = field(init=False)
    saturday_rider_cost: float = field(init=False)
    saturday_non_rider_cost: float = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.total_count = self.data["TotalCount"]
        self.rider_cost = float(self.data["RiderCost"])
        self.non_rider_cost = float(self.data["NonRiderCost"])
        self.saturday_rider_cost = float(self.data["SaturdayRiderCost"])
        self.saturday_non_rider_cost = float(self.data["SaturdayNonRiderCost"])

    def to_dict(self) -> AllDayParkingData:
        """Return the data as a dictionary."""
        return self.data


class StationParkingData(TypedDict):
    """Station parking data for MetroRail WMATA API."""

    Code: str
    Notes: str | None
    ShortTermParking: ShortTermParkingData
    AllDayParking: AllDayParkingData


@dataclass
class StationParking:
    """Station parking information for MetroRail WMATA API."""

    client: "MetroRail"
    data: StationParkingData
    code: str = field(init=False)
    notes: str | None = field(init=False)
    short_term_parking: ShortTermParking = field(init=False)
    all_day_parking: AllDayParking = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.code = self.data["Code"]
        self.notes = self.data["Notes"] if self.data["Notes"] else None
        self.short_term_parking = ShortTermParking(self.data["ShortTermParking"])
        self.all_day_parking = AllDayParking(self.data["AllDayParking"])

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.client.stations[self.code]

    def to_dict(self) -> StationParkingData:
        """Return the data as a dictionary."""
        return self.data
