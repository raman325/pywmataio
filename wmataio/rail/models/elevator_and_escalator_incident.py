"""Elevator/escalator incident models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from .. import MetroRail
    from .station import Station


class ElevatorAndEscalatorIncidentData(TypedDict):
    """Elevator/escalator incident data for MetroRail WMATA API."""

    DateOutOfServ: str
    DateUpdated: str
    DisplayOrder: int | None  # deprecated
    EstimatedReturnToService: str
    LocationDescription: str
    StationCode: str
    StationName: str
    SymptomCode: str | None  # deprecated
    SymptomDescription: str
    TimeOutOfService: str | None  # deprecated
    UnitName: str
    UnitStatus: str | None  # deprecated
    UnitType: Literal["ELEVATOR", "ESCALATOR"]


@dataclass
class ElevatorAndEscalatorIncident:
    """MetroRail Elevator/Escalator Incident."""

    rail: "MetroRail" = field(repr=False)
    data: ElevatorAndEscalatorIncidentData = field(repr=False)
    date_out_of_service: datetime = field(init=False)
    date_updated: datetime = field(init=False)
    estimated_return_to_service: datetime | None = field(init=False, default=None)
    location_description: str = field(init=False)
    station_code: str = field(init=False)
    station_name: str = field(init=False)
    symptom_description: str = field(init=False)
    unit_name: str = field(init=False)
    unit_type: Literal["ELEVATOR", "ESCALATOR"] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.date_out_of_service = datetime.fromisoformat(
            self.data["DateOutOfServ"]
        ).replace(tzinfo=TZ)
        self.date_updated = datetime.fromisoformat(self.data["DateUpdated"]).replace(
            tzinfo=TZ
        )
        if estimated_return_to_service := self.data["EstimatedReturnToService"]:
            self.estimated_return_to_service = datetime.fromisoformat(
                estimated_return_to_service
            ).replace(tzinfo=TZ)
        self.location_description = self.data["LocationDescription"]
        self.station_code = self.data["StationCode"]
        self.station_name = self.data["StationName"]
        self.symptom_description = self.data["SymptomDescription"]
        self.unit_name = self.data["UnitName"]
        self.unit_type = self.data["UnitType"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(
            (
                self.station,
                self.date_out_of_service,
                self.symptom_description,
                self.unit_name,
                self.unit_type,
            )
        )

    @property
    def station(self) -> "Station":
        """Return the station."""
        return self.rail.stations[self.station_code]
