"""Utility functions for the WMATA Bus API."""
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Iterable

from .models.route import Route
from .models.route_path import RoutePath, RoutePathDirection
from .models.stop import Stop

if TYPE_CHECKING:
    from ..client import Client


async def find_direct_route_start_end_stop_pairs(
    client: "Client",
    start_stops: Iterable[Stop],
    end_stops: Iterable[Stop],
) -> defaultdict[tuple[Stop, Stop], set[RoutePathDirection]]:
    """Find direct routes between two stops."""
    start_end_stops_to_routes: defaultdict[
        tuple[Stop, Stop], set[RoutePathDirection]
    ] = defaultdict(set)
    route_paths: dict[Route, RoutePath] = {}

    for start_stop in start_stops:
        for end_stop in end_stops:
            if start_stop == end_stop:
                continue
            for route in start_stop.routes.intersection(end_stop.routes):
                if route not in route_paths:
                    route_paths[route] = await client.bus.get_route_path(route)
                for direction in route_paths[route].path_directions.values():
                    route_stops = direction.stops
                    if start_stop not in route_stops or end_stop not in route_stops:
                        continue
                    if route_stops.index(start_stop) < route_stops.index(end_stop):
                        stop_pair = (start_stop, end_stop)
                    else:
                        stop_pair = (end_stop, start_stop)
                    start_end_stops_to_routes[stop_pair].add(direction)

    return start_end_stops_to_routes
