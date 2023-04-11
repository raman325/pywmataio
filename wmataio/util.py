"""Utility functions for pywmataio."""
from __future__ import annotations

import logging
from contextlib import nullcontext

from aiohttp import ClientSession

from .const import DEFAULT_GEOCODE_PARAMS, GEOCODE_URL

_LOGGER = logging.getLogger(__name__)


async def get_lat_long_from_address(
    address: str, session: ClientSession | None = None
) -> tuple[float, float] | None:
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
        return (
            found_addresses[0]["coordinates"]["x"],
            found_addresses[0]["coordinates"]["y"],
        )
