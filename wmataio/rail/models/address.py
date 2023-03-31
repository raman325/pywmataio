"""Address models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class AddressData(TypedDict):
    """Station address data for MetroRail WMATA API."""

    City: str
    State: str
    Street: str
    Zip: str


@dataclass
class Address:
    """MetroRail Station Address."""

    data: AddressData
    street: str = field(init=False)
    city: str = field(init=False)
    state: str = field(init=False)
    zip_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.street = self.data["Street"]
        self.city = self.data["City"]
        self.state = self.data["State"]
        self.zip_code = self.data["Zip"]
