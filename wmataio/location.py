"""Model for location search data."""
from typing import TypedDict


class Coordinates:
    """Represent location coordinates."""

    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude


class AreaData(TypedDict):
    """Search area parameters for WMATA API."""

    Radius: int
    Lat: float
    Lon: float


class Area:
    """Represent search area parameters."""

    radius: int
    coordinates: Coordinates

    def __init__(self, radius: int, latitude: float, longitude: float) -> None:
        """Initialize the search area parameters."""
        self.radius = radius
        self.coordinates = Coordinates(latitude, longitude)

    def to_dict(self) -> dict[str, int | float]:
        """Return a dict representation of the search area parameters."""
        return {
            "Radius": self.radius,
            "Lat": self.coordinates.latitude,
            "Lon": self.coordinates.longitude,
        }
