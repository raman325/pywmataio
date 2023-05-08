"""Bus incident models for MetroBus WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ...util import get_datetime_from_str

if TYPE_CHECKING:
    from .. import MetroBus
    from .route import Route


class BusIncidentData(TypedDict):
    """Incident data for MetroBus WMATA API."""

    DateUpdated: str
    Description: str
    IncidentID: str
    IncidentType: str
    RoutesAffected: list[str]


@dataclass
class BusIncident:
    """MetroBus Incident."""

    bus: "MetroBus" = field(repr=False)
    data: BusIncidentData = field(repr=False)
    date_updated: datetime = field(init=False)
    description: str = field(init=False)
    incident_id: str = field(init=False)
    id: str = field(init=False)
    incident_type: str = field(init=False)
    route_ids_affected: list[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.date_updated = get_datetime_from_str(self.data["DateUpdated"])
        self.description = self.data["Description"]
        self.incident_type = self.data["IncidentType"]
        self.id = self.incident_id = self.data["IncidentID"]
        self.route_ids_affected = self.data["RoutesAffected"]

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.incident_id)

    @property
    def routes_affected(self) -> set["Route"]:
        """Return routes affected by this incident."""
        return {self.bus.routes[route_id] for route_id in self.route_ids_affected}
