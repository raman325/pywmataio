"""Model for area search data."""


class Coordinates:
    """Represent location coordinates."""

    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float) -> None:
        """Initialize."""
        self.latitude = latitude
        self.longitude = longitude
