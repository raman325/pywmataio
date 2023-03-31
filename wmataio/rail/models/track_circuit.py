"""Standard route models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from ..client import MetroRail
    from .station import Station


class TrackCircuitNeighborData(TypedDict):
    """Track circuit neighbor data for MetroRail WMATA API."""

    CircuitIds: list[int]
    NeighborType: Literal["Left", "Right"]


@dataclass
class TrackCircuitNeighbor:
    """Track circuit neighbor."""

    all_track_circuits: list[TrackCircuit]
    data: TrackCircuitNeighborData
    circuit_ids: list[int] = field(init=False)
    neighbor_type: Literal["Left", "Right"] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.circuit_ids = self.data["CircuitIds"]
        self.neighbor_type = self.data["NeighborType"]

    @property
    def circuits(self) -> list[TrackCircuit]:
        """Circuits."""
        return [
            circuit
            for circuit in self.all_track_circuits
            if circuit.circuit_id in self.circuit_ids
        ]


class TrackCircuitData(TypedDict):
    """Track circuit data for MetroRail WMATA API."""

    CircuitId: int
    Neighbors: list[TrackCircuitNeighborData]
    StationCode: str | None


@dataclass
class TrackCircuit:
    """Track circuit."""

    client: "MetroRail"
    all_track_circuits: list[TrackCircuit]
    data: TrackCircuitData
    circuit_id: int = field(init=False)
    neighbors: list[TrackCircuitNeighbor] = field(init=False)
    station_code: str | None = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.circuit_id = self.data["CircuitId"]
        self.neighbors = [
            TrackCircuitNeighbor(self.all_track_circuits, neighbor)
            for neighbor in self.data["Neighbors"]
        ]
        self.station_code = self.data["StationCode"]

    @property
    def station(self) -> "Station" | None:
        """Station."""
        if self.station_code is None:
            return None
        return self.client.stations[self.station_code]
