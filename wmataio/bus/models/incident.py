"""Bus incident models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...const import TZ

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route


class IncidentData(TypedDict):
    """Incident data for MetroBus WMATA API."""

    DateUpdated: str
    Description: str
    IncidentID: str
    IncidentType: str
    RoutesAffected: list[str]


@dataclass
class Incident:
    """MetroBus Incident."""

    client: "MetroBus"
    data: IncidentData
    date_updated: datetime = field(init=False)
    description: str = field(init=False)
    incident_id: str = field(init=False)
    incident_type: str = field(init=False)
    route_ids_affected: list[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.date_updated = datetime.fromisoformat(self.data["DateUpdated"]).replace(
            tzinfo=TZ
        )
        self.incident_id = self.data["IncidentID"]
        self.route_ids_affected = self.data["RoutesAffected"]

    @property
    def routes_affected(self) -> list["Route"]:
        """Return routes affected by this incident."""
        return [self.client.routes[route_id] for route_id in self.route_ids_affected]

    def to_dict(self) -> IncidentData:
        """Return a dict representation of the Incident."""
        return self.data
