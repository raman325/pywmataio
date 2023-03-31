"""Station models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from .station_entrance import StationEntranceData
from .station_parking import StationParkingData
from .station_timings import StationTimeData

if TYPE_CHECKING:
    from ..client import MetroRail
    from .address import Address, AddressData
    from .line import Line
    from .station_entrance import StationEntrance
    from .station_parking import StationParking
    from .station_timings import StationTime


class StationData(TypedDict):
    """Station data for MetroRail WMATA API."""

    Address: "AddressData"
    Code: str
    Lat: float
    Lon: float
    LineCode1: str
    LineCode2: str | None
    LineCode3: str | None
    LineCode4: str | None
    Name: str
    StationTogether1: str
    StationTogether2: str


class StationDataWithExtraInfo(StationData):
    """Station data with extra info for MetroRail WMATA API."""

    parking: StationParkingData
    entrances: list[StationEntranceData]
    station_times: list[StationTimeData]


@dataclass
class Station:
    """MetroRail Station."""

    client: "MetroRail"
    data: StationData
    parking: "StationParking"
    entrances: list["StationEntrance"]
    station_times: list["StationTime"]
    address: Address = field(init=False)
    code: str = field(init=False)
    latitude: float = field(init=False)
    longitude: float = field(init=False)
    line_codes: list[str] = field(init=False)
    name: str = field(init=False)
    station_together_code_1: str | None = field(init=False)
    station_together_code_2: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.address = Address(self.data["Address"])
        self.code = self.data["Code"]
        self.latitude = self.data["Lat"]
        self.longitude = self.data["Lon"]
        self.line_codes = [
            self.data[f"LineCode{x}"]  # type: ignore
            for x in range(1, 5)
            if self.data[f"LineCode{x}"]  # type: ignore
        ]
        self.name = self.data["Name"]
        self.station_together_code_1 = (
            self.data["StationTogether1"] if self.data["StationTogether1"] else None
        )
        self.station_together_code_2 = (
            self.data["StationTogether2"] if self.data["StationTogether2"] else None
        )

    @property
    def lines(self) -> list["Line"]:
        """Return the lines."""
        return [self.client.lines[line_code] for line_code in self.line_codes]

    @property
    def station_together_1(self) -> "Station" | None:
        """Return the station together 1."""
        if not self.station_together_code_1:
            return None
        return self.client.stations[self.station_together_code_1]

    @property
    def station_together_2(self) -> "Station" | None:
        """Return the station together 2."""
        if not self.station_together_code_2:
            return None
        return self.client.stations[self.station_together_code_2]

    def to_dict(self) -> StationDataWithExtraInfo:
        """Return a dict representation of the Station."""
        return {
            **self.data,  # type: ignore
            "parking": self.parking.data,
            "entrances": [entrance.data for entrance in self.entrances],
            "station_times": [station_time.data for station_time in self.station_times],
        }
