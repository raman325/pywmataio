"""Fixtures for pywmataio tests."""
import json
import logging
import pathlib
import re

import pytest
from aioresponses import CallbackResult, aioresponses

from wmataio.bus.const import BusEndpoint
from wmataio.const import ADDITIONAL_PATH_HEADER, CLASS_HEADER, ENUM_HEADER
from wmataio.rail.const import RailEndpoint

CLASS_MAP = {
    BusEndpoint.__name__: {"class": BusEndpoint, "api_type": "bus"},
    RailEndpoint.__name__: {"class": RailEndpoint, "api_type": "rail"},
}


_LOGGER = logging.getLogger(__name__)
API_REGEX = re.compile(r"https:\/\/api\.wmata\.com.*$")


def _callback(url: str, **kwargs) -> CallbackResult:
    """Respond to WMATA API calls."""
    _LOGGER.debug("Received request for %s", url)
    params = kwargs.get("params")
    headers = kwargs["headers"]
    class_name = headers[CLASS_HEADER]
    enum_name = headers[ENUM_HEADER]
    additional_path = headers[ADDITIONAL_PATH_HEADER]
    cls_data = CLASS_MAP[class_name]
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

    path = pathlib.Path(f"test/fixtures/{api_type}/{fixture_name}.json")

    if not path.exists():
        _LOGGER.error("Fixture %s does not exist", path)
        return CallbackResult(status=404)

    with open(path, "r") as fp:
        data = json.load(fp)

    return CallbackResult(status=200, payload=data)


@pytest.fixture(name="aioresponses", scope="session")
def mock_aioresponse():
    """Mock aiohttp responses."""
    with aioresponses() as m:
        m.get(API_REGEX, callback=_callback, repeat=True)
        yield m
