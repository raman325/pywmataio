"""Exceptions for pywmataio."""


class WMATAError(BaseException):
    """Represent an error from the WMATA API."""

    message: str

    def __init__(self, message: str):
        """Initialize."""
        self.message = message
