"""Standard route models for MetroRail WMATA API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict


class TrackCircuitNeighborData(TypedDict):
    """Track circuit neighbor data for MetroRail WMATA API."""

    CircuitIds: list[int]
    NeighborType: Literal["Left", "Right"]


@dataclass
class TrackCircuitNeighbor:
    """Track circuit neighbor."""

    all_track_circuits: dict[int, TrackCircuit]
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
        return [self.all_track_circuits[circuit_id] for circuit_id in self.circuit_ids]


class TrackCircuitData(TypedDict):
    """Track circuit data for MetroRail WMATA API."""

    CircuitId: int
    Neighbors: list[TrackCircuitNeighborData]
    Track: int


@dataclass
class TrackCircuit:
    """Track circuit."""

    all_track_circuits: dict[int, TrackCircuit]
    data: TrackCircuitData
    circuit_id: int = field(init=False)
    neighbors: list[TrackCircuitNeighbor] = field(init=False)
    track: int = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        self.circuit_id = self.data["CircuitId"]
        self.neighbors = [
            TrackCircuitNeighbor(self.all_track_circuits, neighbor)
            for neighbor in self.data["Neighbors"]
        ]
        self.track = self.data["Track"]
