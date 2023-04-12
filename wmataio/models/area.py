"""Model for area search data."""
from dataclasses import dataclass, field
from typing import TypedDict

from .coordinates import Coordinates


class AreaData(TypedDict):
    """Search area parameters for WMATA API."""

    Radius: int
    Lat: float
    Lon: float


@dataclass
class Area:
    """Represent search area parameters."""

    radius: int
    latitude: float = field(repr=False)
    longitude: float = field(repr=False)
    coordinates: Coordinates = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.coordinates = Coordinates(self.latitude, self.longitude)
        del self.latitude
        del self.longitude

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.radius, self.coordinates))

    def to_dict(self) -> dict[str, int | float]:
        """Return a dict representation of the search area parameters."""
        return {
            "Radius": self.radius,
            "Lat": self.coordinates.latitude,
            "Lon": self.coordinates.longitude,
        }
