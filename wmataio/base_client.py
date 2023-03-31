"""Base Client logic for WMATA API clients."""

from __future__ import annotations

from contextlib import nullcontext
from json.decoder import JSONDecodeError
from typing import Any, cast

from aiohttp import ClientSession, client_exceptions

from .error import WMATAError


class BaseClient:
    """Base Client to provide API request support."""

    api_key: str
    session: ClientSession | None = None

    def __init__(self, api_key: str, session: ClientSession | None = None):
        """Initialize."""
        self.api_key = api_key
        self.session = session

    async def fetch(self, url: str, params: dict[str, Any] | None = None) -> dict:
        """Fetch data from WMATA API."""
        context_manager = nullcontext(self.session) if self.session else ClientSession()
        async with context_manager as session:
            try:
                response = await session.get(
                    url,
                    params=params,
                    headers={"api_key": self.api_key},
                    raise_for_status=True,
                )
            except client_exceptions.ClientError as error:
                raise WMATAError("Error while making request") from error

            try:
                response_json = await response.json(content_type=None)
            except JSONDecodeError as error:
                raise WMATAError("Invalid JSON") from error

            try:
                return cast(dict, response_json)
            except Exception as error:
                raise WMATAError("Could not parse response json into object") from error
