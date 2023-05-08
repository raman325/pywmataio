"""
Helper functions for pywmataio modules.

Generally should only be used internally.
"""
from __future__ import annotations

from dataclasses import astuple
from typing import TYPE_CHECKING, Callable, TypeVar, cast

from haversine import Unit, haversine

from .models.coordinates import Coordinates

if TYPE_CHECKING:
    from .bus.models.route import Route
    from .bus.models.stop import Stop
    from .rail.models.line import Line
    from .rail.models.station import Station

T = TypeVar("T", "Station", "Stop")
U = TypeVar("U", "Line", "Route")
StopDistanceType = tuple[T, float]


def __dist_between(start: Coordinates, end: T) -> float:
    """Get the distance between a Coordinates and a Stop/Station."""
    return cast(
        float, haversine(astuple(start), astuple(end.coordinates), unit=Unit.MILES)
    )


def __sorted_locations_and_dist(
    locations_dict: dict[str, T], coordinate: Coordinates
) -> list[StopDistanceType]:
    """Sort the locations by distance from the given coordinate."""
    return sorted(
        (
            (location, __dist_between(coordinate, location))
            for location in locations_dict.values()
        ),
        key=lambda location_and_dist: location_and_dist[1],
    )


async def get_stop_or_station_pairs_closest_to_coordinates(
    locations_dict: dict[str, T],
    routes_func: Callable[[T], set[U]],
    start_coordinate: Coordinates,
    end_coordinate: Coordinates,
    max_total_distance: float | None,
    dist_precision: int,
) -> list[tuple[StopDistanceType, StopDistanceType]]:
    """Get the closest stop/station pairs to the start and end coordinates."""

    # Sort the locations by distance from the start and end locations
    start_locations_and_dist: list[StopDistanceType] = __sorted_locations_and_dist(
        locations_dict, start_coordinate
    )
    end_locations_and_dist: list[StopDistanceType] = __sorted_locations_and_dist(
        locations_dict, end_coordinate
    )

    # For each start_location, find the closest end_location that shares a route if
    # possible and add it to a list
    start_end_pairs: list[tuple[StopDistanceType, StopDistanceType]] = []
    routes_covered: set[U] = set()
    for start_location, start_dist in start_locations_and_dist:
        # If we've already found the best location pair for a route at this location,
        # skip it
        if routes_func(start_location).intersection(routes_covered):
            continue
        try:
            end_location, end_dist = next(
                (location, dist)
                for location, dist in end_locations_and_dist
                if routes_func(location).intersection(routes_func(start_location))
            )
        except StopIteration:
            continue

        if end_location == start_location:
            continue

        routes_covered.update(
            routes_func(end_location).intersection(routes_func(start_location))
        )
        start_end_pairs.append(
            (
                (start_location, round(start_dist, dist_precision)),
                (end_location, round(end_dist, dist_precision)),
            )
        )

    if max_total_distance:
        start_end_pairs = [
            start_end_pair
            for start_end_pair in start_end_pairs
            if start_end_pair[0][1] + start_end_pair[1][1] <= max_total_distance
        ]

    start_end_pairs = sorted(start_end_pairs, key=lambda pair: pair[0][1] + pair[1][1])

    return start_end_pairs
