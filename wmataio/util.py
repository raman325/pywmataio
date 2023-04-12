"""Utility functions for pywmataio."""
from __future__ import annotations

import logging
from contextlib import nullcontext
from dataclasses import astuple
from typing import Callable, TypeVar, cast

from aiohttp import ClientSession
from haversine import Unit, haversine

from .bus import MetroBus
from .bus.models.route import Route
from .bus.models.stop import Stop
from .const import DEFAULT_GEOCODE_PARAMS, GEOCODE_URL
from .models.coordinates import Coordinates
from .rail import MetroRail
from .rail.models.line import Line
from .rail.models.station import Station

_LOGGER = logging.getLogger(__name__)

# TODO: give everything a generic ID that maps to its specific ID (eg. stop_id, station_id, etc.)

T = TypeVar("T", Station, Stop)
U = TypeVar("U", Line, Route)
StopDistanceType = tuple[T, float]


async def get_lat_long_from_address(
    address: str, session: ClientSession | None = None
) -> Coordinates | None:
    """Get the lat long for a US address."""
    async with nullcontext(session) if session else ClientSession() as client_session:
        data = await client_session.get(
            GEOCODE_URL,
            params={**DEFAULT_GEOCODE_PARAMS, "address": address},
            raise_for_status=True,
        )
        json_data = await data.json()
        found_addresses = json_data["result"]["addressMatches"]
        if not found_addresses:
            return None
        if len(found_addresses) > 1:
            _LOGGER.warning(
                "Multiple addresses found for %s, returning the first one",
                address,
            )
        return Coordinates(
            found_addresses[0]["coordinates"]["y"],
            found_addresses[0]["coordinates"]["x"],
        )


async def get_stop_or_station_pairs_closest_to_coordinates(
    transit_instance: MetroBus | MetroRail,
    locations_dict: dict[str, T],
    routes_func: Callable[[T], set[U]],
    start_coord: Coordinates,
    end_coord: Coordinates,
    max_pairs: int | None = 10,
    max_total_distance: float | None = None,
    dist_precision: int = 2,
) -> list[tuple[StopDistanceType, StopDistanceType]]:
    """Get the closest stop/station pairs to the start and end coordinates."""
    if not locations_dict:
        await transit_instance.load_data()

    def _dist_between(start: Coordinates, end: T) -> float:
        """Get the distance between two coordinates."""
        return cast(
            float, haversine(astuple(start), astuple(end.coordinates), unit=Unit.MILES)
        )

    # Sort the locations by distance from the start and end locations
    start_locations_and_dist: list[StopDistanceType] = sorted(
        (
            (location, _dist_between(start_coord, location))
            for location in locations_dict.values()
        ),
        key=lambda location_and_dist: location_and_dist[1],
    )
    end_locations_and_dist: list[StopDistanceType] = sorted(
        (
            (location, _dist_between(end_coord, location))
            for location in locations_dict.values()
        ),
        key=lambda location_and_dist: location_and_dist[1],
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

        if max_total_distance and (max_total_distance < start_dist + end_dist):
            break

        routes_covered.update(
            routes_func(end_location).intersection(routes_func(start_location))
        )
        start_end_pairs.append(
            (
                (start_location, round(start_dist, dist_precision)),
                (end_location, round(end_dist, dist_precision)),
            )
        )

        if max_pairs and max_pairs > 0 and len(start_end_pairs) == max_pairs:
            break

    return start_end_pairs
