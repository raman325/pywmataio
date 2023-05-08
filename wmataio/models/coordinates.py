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

    @property
    def as_tuple(self) -> tuple[float, float]:
        """Return the coordinates as a tuple."""
        return (self.latitude, self.longitude)
