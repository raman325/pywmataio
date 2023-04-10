"""Base Client logic for WMATA API clients."""
from __future__ import annotations

import asyncio
import logging
from contextlib import nullcontext
from dataclasses import dataclass, field
from json.decoder import JSONDecodeError
from typing import Any, cast

from aiohttp import ClientSession, client_exceptions

from .bus import MetroBus
from .bus.const import BusEndpoint
from .const import ADDITIONAL_PATH_HEADER, CLASS_HEADER, ENUM_HEADER, WMATAEndpoint
from .exceptions import WMATAError
from .rail import MetroRail
from .rail.const import RailEndpoint

_LOGGER = logging.getLogger(__name__)


@dataclass
class Client:
    """Client to provide API request support."""

    api_key: str
    session: ClientSession | None = None
    test_mode: bool = False
    bus: MetroBus = field(init=False)
    rail: MetroRail = field(init=False)
    _headers: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.bus = MetroBus(self)
        self.rail = MetroRail(self)
        self._headers = {"api_key": self.api_key}

    def _get_headers(
        self,
        enum_: BusEndpoint | RailEndpoint | WMATAEndpoint,
        additional_path: str | None = None,
    ) -> dict[str, Any]:
        """Get headers."""
        if self.test_mode:
            return {
                **self._headers,
                CLASS_HEADER: enum_.__class__.__name__,
                ENUM_HEADER: enum_.name,
                ADDITIONAL_PATH_HEADER: additional_path or "",
            }
        return self._headers

    async def fetch(
        self,
        enum_: BusEndpoint | RailEndpoint | WMATAEndpoint,
        params: dict[str, Any] | None = None,
        additional_path: str | None = None,
    ) -> dict:
        """Fetch data from WMATA API."""
        url = enum_.value
        if additional_path:
            url = f"{url}/{additional_path}"

        _LOGGER.debug("Fetching %s with params %s", url, params or {})
        retry = True
        context_manager = nullcontext(self.session) if self.session else ClientSession()
        async with context_manager as session:
            while retry:
                try:
                    response = await session.get(
                        url,
                        params=params,
                        headers=self._get_headers(enum_, additional_path),
                        raise_for_status=True,
                    )
                except client_exceptions.ClientResponseError as error:
                    if error.status != 429:
                        raise WMATAError("Error while making request") from error
                    _LOGGER.warning("Too many requests, sleeping for 1.1 seconds")
                    await asyncio.sleep(1.1)
                except client_exceptions.ClientError as error:
                    raise WMATAError("Error while making request") from error
                else:
                    retry = False

            try:
                response_json = await response.json(content_type=None)
            except JSONDecodeError as error:
                _LOGGER.error("Invalid JSON: %s", response.text())
                raise WMATAError("Invalid JSON") from error
            _LOGGER.debug("Response: %s", response_json)

            try:
                return cast(dict, response_json)
            except Exception as error:
                raise WMATAError("Could not parse response json into object") from error
