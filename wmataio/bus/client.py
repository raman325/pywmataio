"""Client for MetroBus APIs."""
from __future__ import annotations

from datetime import date
from typing import Any, cast

from aiohttp import ClientSession

from ..base_client import BaseClient
from ..location import Area
from .const import Endpoint
from .models.incident import Incident
from .models.position import Position
from .models.prediction import NextPrediction
from .models.route import Route
from .models.route_path import RoutePath, RoutePathData
from .models.route_schedule import RouteSchedule, RouteScheduleData
from .models.stop import Stop, StopData
from .models.stop_schedule import StopArrivalSchedule


class MetroBus(BaseClient):
    """Class to represent client for MetroBus APIs."""

    routes: dict[str, Route]
    stops: dict[str, Stop]

    def __init__(self, api_key: str, session: ClientSession | None = None):
        """Initialize."""
        super().__init__(api_key, session)
        self.routes = {}
        self.stops = {}

    def get_stop_from_stop_data(self, stop_data: StopData) -> Stop:
        """Get stop from stop ID."""
        stop_id = stop_data["StopID"]
        if not isinstance(stop_id, str):
            stop_id = stop_data["Name"]
        if stop_id not in self.stops:
            raise ValueError(f"Stop `{stop_id}` not found.")
        return self.stops[stop_id]

    def get_all_stops_from_stop_data(
        self, stops_data: list[StopData]
    ) -> dict[str, Stop]:
        """Get all stops from list of StopData."""
        data = {}
        for stop_data in stops_data:
            stop: Stop = self.get_stop_from_stop_data(stop_data)
            data[stop.stop_id] = stop
        return data

    async def get_all_routes(self) -> dict[str, Route]:
        """Get all routes."""
        data = await self.fetch(Endpoint.ROUTES.value)
        return {
            route_data["RouteID"]: Route(route_data) for route_data in data["Routes"]
        }

    async def get_all_stops(self) -> dict[str, Stop]:
        """Get all stops."""
        data = await self.fetch(Endpoint.STOPS.value)
        return {stop["StopID"]: Stop(self, stop) for stop in data["Stops"]}

    async def load_data(self) -> None:
        """Setup the client."""
        self.routes = await self.get_all_routes()
        self.stops = await self.get_all_stops()

    async def search_stops(self, search_data: Area) -> dict[str, Stop]:
        """Get all stops."""
        raw_data = await self.fetch(
            Endpoint.STOPS.value, params=dict(search_data.to_dict())
        )
        return self.get_all_stops_from_stop_data(raw_data["stops"])

    async def positions(
        self,
        route: Route | None = None,
        area: Area | None = None,
    ) -> list[Position]:
        """
        Get bus position(s).

        If no route or area is provided, all bus positions will be
        returned.
        """
        params: dict[str, Any] = {}
        if route:
            params["Route"] = route.route_id
        if area:
            params.update(area.to_dict())

        data = await self.fetch(Endpoint.POSITIONS.value, params=params)
        return sorted(
            [Position(self, position) for position in data["BusPositions"]],
            key=lambda position: position.trip_start_time,
        )

    async def incidents(self, route: Route | None = None) -> list[Incident]:
        """
        Get bus incidents.

        If no route is provided, all bus incidents for all routes will be returned.
        """
        params = None
        if route:
            params = {"Route": route.route_id}

        data = await self.fetch(Endpoint.INCIDENTS.value, params=params)

        return sorted(
            [Incident(self, incident) for incident in data["BusIncidents"]],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def route_path(self, route: Route, date_: date | None = None) -> RoutePath:
        """
        Return path for a given route.

        If no date_ is provided, the current date will be used.
        """
        params = {"RouteID": route.route_id}
        if date_:
            params["Date"] = date_.strftime("%Y-%m-%d")

        data = cast(
            RoutePathData, await self.fetch(Endpoint.PATH_DETAILS.value, params=params)
        )
        return RoutePath(self, data)

    async def route_schedule(
        self,
        route: Route,
        date_: date | None = None,
        include_variations: bool = False,
    ) -> RouteSchedule:
        """
        Return schedule for a given route.

        - If no date_ is provided, the current date will be used.
        - include_variations specifies whether variations for the input route should be
        included.
        """
        params = {
            "RouteID": route.route_id,
            "IncludingVariations": str(include_variations).lower(),
        }
        if date_:
            params["Date"] = date_.strftime("%Y-%m-%d")

        data = cast(
            RouteScheduleData,
            await self.fetch(Endpoint.ROUTE_SCHEDULE.value, params=params),
        )
        return RouteSchedule(self, route, data)

    async def next_buses_at_stop(self, stop: Stop) -> list[NextPrediction]:
        """Return next buses for a given stop."""
        data = await self.fetch(
            Endpoint.NEXT_BUSES.value, params={"StopID": stop.stop_id}
        )
        return [NextPrediction(self, prediction) for prediction in data["Predictions"]]

    async def stop_schedule(
        self, stop: Stop, date_: date | None = None
    ) -> list[StopArrivalSchedule]:
        """
        Return schedule for a given stop.

        If no date_ is provided, the current date will be used.
        """
        params = {"StopID": stop.stop_id}
        if date_:
            params["Date"] = date_.strftime("%Y-%m-%d")

        data = await self.fetch(Endpoint.STOP_SCHEDULE.value, params=params)
        return sorted(
            [
                StopArrivalSchedule(self, stop, stop_arrival_schedule)
                for stop_arrival_schedule in data["ScheduleArrivals"]
            ],
            key=lambda stop_arrival_schedule: stop_arrival_schedule.schedule_time,
        )
