"""Stop models for MetroBus API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import MetroBus
    from .route import Route


class StopData(TypedDict, total=False):
    """Stop data for MetroBus API."""

    StopID: str | int | None
    Lat: str
    Lon: str
    Name: str
    Routes: list[str]


@dataclass
class Stop:
    """A MetroBus Stop"""

    client: "MetroBus"
    data: StopData
    stop_id: str = field(init=False)
    latitude: str = field(init=False)
    longitude: str = field(init=False)
    name: str = field(init=False)
    route_ids: list[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        if isinstance(self.data["StopID"], str):
            self.stop_id = self.data["StopID"]
        else:
            self.stop_id = self.data["Name"]
        self.latitude = self.data["Lat"]
        self.longitude = self.data["Lon"]
        self.longitude = self.data["Name"]
        self.route_ids = self.data["Routes"]

    @property
    def routes(self) -> list["Route"]:
        """Return routes for this stop."""
        return [self.client.routes[route_id] for route_id in self.route_ids]

    def to_dict(self) -> StopData:
        """Return a dict representation of the Stop."""
        return self.data
