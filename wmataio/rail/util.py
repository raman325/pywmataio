"""Utility functions for the WMATA Bus API."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .models.station import Station
from .models.station_to_station import StationToStation

if TYPE_CHECKING:
    from ..client import Client


async def get_line_directions_from_station_pair(
    client: "Client", start_station: Station, end_station: Station
) -> tuple[StationToStation, StationToStation]:
    """
    Get line directions between a pair of stations.

    Returns tuple that contains forward direction and reverse direction station to
    station data.
    """
    return (
        await client.rail.get_station_to_station_data(start_station, end_station),
        await client.rail.get_station_to_station_data(end_station, start_station),
    )
