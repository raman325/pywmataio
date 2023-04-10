"""Stop models for MetroBus API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from ...models.coordinates import Coordinates

if TYPE_CHECKING:
    from .. import MetroBus
    from .route import Route


class StopData(TypedDict, total=False):
    """Stop data for MetroBus API."""

    StopID: str | int | None
    Lat: float
    Lon: float
    Name: str
    Routes: list[str]


@dataclass
class Stop:
    """A MetroBus Stop."""

    bus: "MetroBus" = field(repr=False)
    data: StopData = field(repr=False)
    stop_id: str = field(init=False)
    coordinates: Coordinates = field(init=False, repr=False)
    name: str = field(init=False)
    route_ids: list[str] = field(init=False)

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.stop_id)

    def __post_init__(self) -> None:
        """Post init."""
        if isinstance(self.data["StopID"], str):
            self.stop_id = self.data["StopID"]
        else:
            self.stop_id = self.data["Name"]
        self.coordinates = Coordinates(self.data["Lat"], self.data["Lon"])
        self.name = self.data["Name"]
        self.route_ids = self.data["Routes"]

    @property
    def routes(self) -> set["Route"]:
        """Return routes for this stop."""
        return {self.bus.routes[route_id] for route_id in self.route_ids}
