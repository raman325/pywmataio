"""Train incident models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from .. import MetroRail
    from .line import Line


class RailIncidentData(TypedDict):
    """Incident data for MetroRail WMATA API."""

    DateUpdated: str
    DelaySeverity: str | None  # deprecated
    Description: str
    EmergencyText: str | None  # deprecated
    EndLocationFullName: str | None  # deprecated
    IncidentID: str
    IncidentType: str
    LinesAffected: str
    PassengerDelay: int | None  # deprecated
    StartLocationFullName: str | None  # deprecated


@dataclass
class RailIncident:
    """MetroRail Incident."""

    rail: "MetroRail" = field(repr=False)
    data: RailIncidentData = field(repr=False)
    date_updated: datetime = field(init=False)
    description: str = field(init=False)
    incident_id: str = field(init=False)
    incident_type: str = field(init=False)
    line_codes_affected: list[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.date_updated = datetime.fromisoformat(self.data["DateUpdated"]).replace(
            tzinfo=TZ
        )
        self.description = self.data["Description"]
        self.incident_id = self.data["IncidentID"]
        self.incident_type = self.data["IncidentType"]
        self.line_codes_affected = [
            line_code.strip()
            for line_code in self.data["LinesAffected"].split(";")
            if line_code.strip()
        ]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.incident_id)

    @property
    def lines_affected(self) -> list["Line"]:
        """Lines affected."""
        return [self.rail.lines[line_code] for line_code in self.line_codes_affected]
