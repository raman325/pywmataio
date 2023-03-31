"""Standard route models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
    from .line import Line
    from .station import Station


class TrackCircuitData(TypedDict):
    """Track circuit data for MetroRail WMATA API."""

    CircuitId: int
    SeqNum: int
    StationCode: str | None


@dataclass
class TrackCircuit:
    """Track circuit."""

    client: "MetroRail"
    data: TrackCircuitData
    circuit_id: int = field(init=False)
    seq_num: int = field(init=False)
    station_code: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.circuit_id = self.data["CircuitId"]
        self.seq_num = self.data["SeqNum"]
        self.station_code = self.data["StationCode"]

    @property
    def station(self) -> "Station" | None:
        """Station."""
        if self.station_code is None:
            return None
        return self.client.stations[self.station_code]


class StandardRouteData(TypedDict):
    """Standard route data for MetroRail WMATA API."""

    LineCode: str
    TrackCircuits: list[TrackCircuitData]
    TrackNum: Literal[1, 2]


@dataclass
class StandardRoute:
    """Standard route."""

    client: "MetroRail"
    data: StandardRouteData
    line_code: str = field(init=False)
    track_circuits: list[TrackCircuit] = field(init=False)
    track_num: Literal[1, 2] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.line_code = self.data["LineCode"]
        self.track_circuits = sorted(
            [
                TrackCircuit(self.client, track_circuit_data)
                for track_circuit_data in self.data["TrackCircuits"]
            ],
            key=lambda track_circuit: track_circuit.seq_num,
        )
        self.track_num = self.data["TrackNum"]

    @property
    def line(self) -> "Line":
        """Return line for route."""
        return self.client.lines[self.line_code]

    def to_dict(self) -> StandardRouteData:
        """Return dict representation of standard route."""
        return self.data