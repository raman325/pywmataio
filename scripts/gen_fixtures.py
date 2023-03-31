"""Script to generate fixture data."""
import asyncio
import json
import pathlib
from typing import TypedDict

from wmataio.bus.const import BusEndpoint
from wmataio.client import Client
from wmataio.rail.const import RailEndpoint

CONTENT_TYPE = {"contentType": "json"}

api_key_path = pathlib.Path(__file__).parent / "api_key"
if not api_key_path.exists():
    raise FileNotFoundError("`api_key` file not found")

with open(api_key_path, "r") as fp:
    client = Client(fp.readline())


class APICall(TypedDict, total=False):
    """API call to make."""

    enum: BusEndpoint | RailEndpoint  # required
    params: dict[str, str | float | int]
    additional_path: str | None


API_CALLS: dict[str, list[APICall]] = {
    "bus": [
        {"enum": BusEndpoint.BUS_INCIDENTS},
        {"enum": BusEndpoint.BUS_INCIDENTS, "params": {"Route": "10A"}},
        {"enum": BusEndpoint.NEXT_BUSES, "params": {"StopID": "1002916"}},
        {"enum": BusEndpoint.ROUTE_PATH, "params": {"RouteID": "10A"}},
        {
            "enum": BusEndpoint.ROUTE_PATH,
            "params": {"RouteID": "10A", "Date": "2023-03-31"},
        },
        {"enum": BusEndpoint.POSITIONS},
        {"enum": BusEndpoint.POSITIONS, "params": {"RouteID": "10A"}},
        {
            "enum": BusEndpoint.POSITIONS,
            "params": {"Radius": 2000, "Lat": 38.9031442, "Lon": -77.0785817},
        },
        {
            "enum": BusEndpoint.ROUTE_SCHEDULE,
            "params": {"RouteID": "10A", "IncludingVariations": False},
        },
        {
            "enum": BusEndpoint.ROUTE_SCHEDULE,
            "params": {
                "RouteID": "10A",
                "IncludingVariations": False,
                "Date": "2023-03-31",
            },
        },
        {"enum": BusEndpoint.ROUTES},
        {"enum": BusEndpoint.STOP_SCHEDULE, "params": {"StopID": "1000533"}},
        {
            "enum": BusEndpoint.STOP_SCHEDULE,
            "params": {"StopID": "1000533", "Date": "2023-03-31"},
        },
        {"enum": BusEndpoint.STOPS},
        {
            "enum": BusEndpoint.STOPS,
            "params": {"Radius": 2000, "Lat": 38.9031442, "Lon": -77.0785817},
        },
    ],
    "rail": [
        {"enum": RailEndpoint.ELEVATOR_ESCALATOR_INCIDENTS},
        {
            "enum": RailEndpoint.ELEVATOR_ESCALATOR_INCIDENTS,
            "params": {"StationCode": "A01"},
        },
        {"enum": RailEndpoint.RAIL_INCIDENTS},
        {"enum": RailEndpoint.LINES},
        {"enum": RailEndpoint.NEXT_TRAINS, "additional_path": "A15"},
        {"enum": RailEndpoint.STANDARD_ROUTES, "params": CONTENT_TYPE},
        {"enum": RailEndpoint.STATION_ENTRANCES},
        {"enum": RailEndpoint.STATION_PARKING_INFORMATION},
        {"enum": RailEndpoint.STATION_TIMINGS},
        {
            "enum": RailEndpoint.STATION_TO_STATION_INFO,
            "params": {"FromStationCode": "A15", "ToStationCode": "N12"},
        },
        {
            "enum": RailEndpoint.STATION_TO_STATION_PATH,
            "params": {"FromStationCode": "A15", "ToStationCode": "N12"},
        },
        {
            "enum": RailEndpoint.STATION_TO_STATION_INFO,
            "params": {"FromStationCode": "A15", "ToStationCode": "A01"},
        },
        {
            "enum": RailEndpoint.STATION_TO_STATION_PATH,
            "params": {"FromStationCode": "A15", "ToStationCode": "A01"},
        },
        {"enum": RailEndpoint.STATIONS},
        {"enum": RailEndpoint.STATIONS, "params": {"LineCode": "RD"}},
        {"enum": RailEndpoint.TRACK_CIRCUITS, "params": CONTENT_TYPE},
        {"enum": RailEndpoint.TRAIN_POSITIONS, "params": CONTENT_TYPE},
    ],
}


async def call_api(
    client: Client,
    enum_: BusEndpoint | RailEndpoint,
    params: dict[str, str | float | int] | None,
    additional_path: str | None,
):
    """Call API and return response."""
    return await client.fetch(enum_, params=params, additional_path=additional_path)


base_path = pathlib.Path(__file__).parents[1]
for api_type, calls in API_CALLS.items():
    for call in calls:
        enum_ = call["enum"]
        params = call.get("params")
        base_fixture_name = enum_.name.lower()

        additional_path_fixture_name = ""
        if additional_path := call.get("additional_path"):
            additional_path_fixture_name = additional_path.replace("/", "_")

        params_fixture_name = ""
        if params:
            params_fixture_name = "_".join(f"{k}_{v}" for k, v in params.items())

        fixture_name = base_fixture_name
        if additional_path_fixture_name or params_fixture_name:
            fixture_name = ".".join(
                [base_fixture_name, additional_path_fixture_name, params_fixture_name]
            )

        path = base_path / f"test/fixtures/{api_type}/"
        if not path.exists():
            path.mkdir(parents=True)

        full_path = path / f"{fixture_name}.json"

        if full_path.exists():
            continue

        with open(full_path, "w") as fp:
            json.dump(
                asyncio.run(call_api(client, enum_, params, additional_path)),
                fp,
                indent=4,
            )
