"""Utility functions for the WMATA Bus API."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Iterable

from .models.route import Route
from .models.route_path import RoutePath, RoutePathDirection
from .models.stop import Stop
from .models.stop_schedule import StopArrival

if TYPE_CHECKING:
    from ..client import Client

ArrivalPair = list[tuple[StopArrival, StopArrival]]


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


async def get_route_directions_from_stop_pair(
    client: "Client", start_stop: Stop, end_stop: Stop
) -> list[tuple[RoutePath, RoutePathDirection | None, RoutePathDirection | None]]:
    """
    Get route directions between a pair of stops.

    Returns tuple that contains route, forward path direction, and reverse path
    direction.
    """
    directions: list[tuple[RoutePath, int | None, int | None]] = []
    for route in start_stop.routes.intersection(end_stop.routes):
        forward_direction: RoutePathDirection | None = None
        reverse_direction: RoutePathDirection | None = None
        route_path = await client.bus.get_route_path(route)

        for path_direction in route_path.path_directions.values():
            route_stops = path_direction.stops
            if start_stop not in route_stops or end_stop not in route_stops:
                continue
            if route_stops.index(start_stop) < route_stops.index(end_stop):
                forward_direction = path_direction
            else:
                reverse_direction = path_direction

        if (forward_direction or reverse_direction) is not None:
            directions.append((route_path, forward_direction, reverse_direction))
    return directions


async def get_next_buses_from_stop_pair(
    client: "Client", start_stop: Stop, end_stop: Stop
) -> tuple[ArrivalPair, ArrivalPair]:
    """
    Get next bus arrivals for a pair of stops.

    Returns tuple that contains start stop bus arrivals that go to the end stop and
    end stop bus arrivals that go to the start stop sorted by arrival time.
    """
    alL_start_stop_arrivals, all_end_stop_arrivals = await asyncio.gather(
        client.bus.get_stop_schedule(start_stop),
        client.bus.get_stop_schedule(end_stop),
    )
    start_stop_arrivals: ArrivalPair = []
    end_stop_arrivals: ArrivalPair = []

    for start_stop_arrival in alL_start_stop_arrivals:
        for end_stop_arrival in all_end_stop_arrivals:
            if end_stop_arrival.trip_id != start_stop_arrival.trip_id:
                continue
            if end_stop_arrival.schedule_time > start_stop_arrival.schedule_time:
                start_stop_arrivals.append((start_stop_arrival, end_stop_arrival))
            else:
                end_stop_arrivals.append((end_stop_arrival, start_stop_arrival))

    return (
        sorted(start_stop_arrivals, key=lambda x: x[0].schedule_time),
        sorted(end_stop_arrivals, key=lambda x: x[0].schedule_time),
    )
