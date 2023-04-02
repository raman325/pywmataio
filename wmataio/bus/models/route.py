"""Route models for MetroBus API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class RouteData(TypedDict):
    """Route data for MetroBus API."""

    RouteID: str
    Name: str
    LineDescription: list[str]


@dataclass
class Route:
    """A MetroBus Route."""

    data: RouteData
    route_id: str = field(init=False)
    name: str = field(init=False)
    line_description: list[str] = field(init=False)

    def __repr__(self) -> str:
        """Return the representation."""
        cls_name = type(self).__name__
        return f"{cls_name}(id={self.route_id}, name={self.name})"

    def __hash__(self) -> int:
        """Return the hash."""
        return hash(self.route_id)

    def __post_init__(self) -> None:
        """Post init."""
        self.route_id = self.data["RouteID"]
        self.name = self.data["Name"]
        self.line_description = self.data["LineDescription"]
