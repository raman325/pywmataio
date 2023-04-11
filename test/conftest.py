"""Fixtures for pywmataio tests."""
import json
import logging
import pathlib
import re

import pytest
from aioresponses import CallbackResult, aioresponses

from wmataio.bus.const import BusEndpoint
from wmataio.const import (
    ADDITIONAL_PATH_HEADER,
    BASE_WMATA_URL,
    CLASS_HEADER,
    ENUM_HEADER,
    GEOCODE_URL,
)
from wmataio.rail.const import RailEndpoint

_LOGGER = logging.getLogger(__name__)

WMATA_MODEL_CLASS_MAP = {
    BusEndpoint.__name__: {"class": BusEndpoint, "api_type": "bus"},
    RailEndpoint.__name__: {"class": RailEndpoint, "api_type": "rail"},
}


def _process_fixture_path_as_result(path: pathlib.Path) -> CallbackResult:
    """Process fixture data and return callback result."""
    if not path.exists():
        _LOGGER.error("Fixture %s does not exist", path)
        return CallbackResult(status=404)

    with open(path, "r") as fp:
        data = json.load(fp)

    return CallbackResult(status=200, payload=data)


def _wmata_callback(url: str, **kwargs) -> CallbackResult:
    """Respond to WMATA API calls."""
    _LOGGER.debug("Received request for %s", url)
    params = kwargs.get("params")
    headers = kwargs["headers"]
    class_name = headers[CLASS_HEADER]
    enum_name = headers[ENUM_HEADER]
    additional_path = headers[ADDITIONAL_PATH_HEADER]
    cls_data = WMATA_MODEL_CLASS_MAP[class_name]
    enum_: BusEndpoint | RailEndpoint = cls_data["class"][enum_name]
    api_type = cls_data["api_type"]

    base_fixture_name = enum_.name.lower()

    additional_path_fixture_name = ""
    if additional_path:
        additional_path_fixture_name = additional_path.replace("/", "_")

    params_fixture_name = ""
    if params:
        params_fixture_name = "_".join(f"{k}_{v}" for k, v in params.items())

    fixture_name = base_fixture_name
    if additional_path_fixture_name or params_fixture_name:
        fixture_name = ".".join(
            [base_fixture_name, additional_path_fixture_name, params_fixture_name]
        )

    return _process_fixture_path_as_result(
        pathlib.Path(f"test/fixtures/models/{api_type}/{fixture_name}.json")
    )


@pytest.fixture(name="wmata_responses", scope="module")
def mock_wmata_responses():
    """Mock aiohttp response from WMATA API."""
    with aioresponses() as m:
        m.get(re.compile(f"{BASE_WMATA_URL}.*$"), callback=_wmata_callback, repeat=True)
        yield m


def _geocode_callback(url: str, **kwargs) -> CallbackResult:
    """Respond to Geocode API calls."""
    _LOGGER.debug("Received request for %s", url)
    address = kwargs["params"]["address"]
    return _process_fixture_path_as_result(
        pathlib.Path(f"test/fixtures/util/geocode/{address}.json")
    )


@pytest.fixture(name="geocode_responses", scope="module")
def mock_geocode_responses():
    """Mock aiohttp responses from geocode_service."""
    with aioresponses() as m:
        m.get(re.compile(f"{GEOCODE_URL}.*$"), callback=_geocode_callback, repeat=True)
        yield m
