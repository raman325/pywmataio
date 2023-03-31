"""Train incident models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroRail
    from .line import Line


class IncidentData(TypedDict):
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
class Incident:
    """MetroRail Incident."""

    client: "MetroRail"
    data: IncidentData
    date_updated: datetime = field(init=False)
    description: str = field(init=False)
    incident_id: str = field(init=False)
    incident_type: str = field(init=False)
    line_codes_affected: list[str] = field(init=False)
    lines_affected: list["Line"] = field(init=False)

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
        self.lines_affected = [
            self.client.lines[line_code] for line_code in self.line_codes_affected
        ]
