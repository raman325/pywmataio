"""Model for area search data."""
from dataclasses import dataclass


@dataclass
class Coordinates:
    """Represent location coordinates."""

    latitude: float
    longitude: float

    def __hash__(self) -> int:
        """Return the hash."""
        return hash((self.latitude, self.longitude))
