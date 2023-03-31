"""Module for interacting with MetroBus API."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, cast

from ..models.area import Area
from .const import BusEndpoint
from .models.bus_incident import BusIncident
from .models.live_position import LiveBusPosition
from .models.next_bus import NextBus
from .models.route import Route
from .models.route_path import RoutePath, RoutePathData
from .models.route_schedule import RouteSchedule, RouteScheduleData
from .models.stop import Stop, StopData
from .models.stop_schedule import StopArrival

if TYPE_CHECKING:
    from ..client import Client


class MetroBus:
    """Class to represent client for MetroBus APIs."""

    client: "Client"
    routes: dict[str, Route]
    stops: dict[str, Stop]

    def __init__(self, client: "Client") -> None:
        """Initialize."""
        self.client = client
        self.routes = {}
        self.stops = {}

    async def load_data(self) -> None:
        """Load the base data."""
        self.routes = await self.get_all_routes()
        self.stops = await self.get_stops()

    def get_stop_from_stop_data(
        self, stop_data: StopData, use_internal_data: bool = True
    ) -> Stop:
        """Get stop from stop ID."""
        stop_id = stop_data["StopID"]
        if not isinstance(stop_id, str):
            stop_id = stop_data["Name"]
        if not use_internal_data:
            return Stop(self, stop_data)
        if stop_id not in self.stops:
            raise ValueError(f"Stop `{stop_id}` not found.")
        return self.stops[stop_id]

    def get_all_stops_from_stop_data(
        self, stops_data: list[StopData], use_internal_data: bool = True
    ) -> dict[str, Stop]:
        """Get all stops from list of StopData."""
        data: dict[str, Stop] = {}
        for stop_data in stops_data:
            stop = self.get_stop_from_stop_data(stop_data, use_internal_data)
            data[stop.stop_id] = stop

        return data

    async def get_all_routes(self) -> dict[str, Route]:
        """Get all routes."""
        data = await self.client.fetch(BusEndpoint.ROUTES)
        return {
            route_data["RouteID"]: Route(route_data) for route_data in data["Routes"]
        }

    async def get_stops(self, area: Area | None = None) -> dict[str, Stop]:
        """Get stops."""
        params: dict | None = None
        if area:
            params = dict(area.to_dict())
        data = await self.client.fetch(BusEndpoint.STOPS, params=params)
        return self.get_all_stops_from_stop_data(data["Stops"], use_internal_data=False)

    async def get_live_positions(
        self,
        route: Route | None = None,
        area: Area | None = None,
    ) -> list[LiveBusPosition]:
        """
        Get live bus position(s).

        If no route or area is provided, all bus positions will be
        returned.
        """
        params: dict[str, Any] = {}
        if route:
            params["RouteID"] = route.route_id
        if area:
            params.update(area.to_dict())

        data = await self.client.fetch(BusEndpoint.POSITIONS, params=params)
        return sorted(
            [LiveBusPosition(self, position) for position in data["BusPositions"]],
            key=lambda position: position.trip_start_time,
        )

    async def get_bus_incidents(self, route: Route | None = None) -> list[BusIncident]:
        """
        Get bus incidents.

        If no route is provided, all bus incidents for all routes will be returned.
        """
        params = None
        if route:
            params = {"Route": route.route_id}

        data = await self.client.fetch(BusEndpoint.BUS_INCIDENTS, params=params)

        return sorted(
            [BusIncident(self, incident) for incident in data["BusIncidents"]],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def get_route_path(
        self, route: Route, date_: date | None = None
    ) -> RoutePath:
        """
        Return path for a given route.

        If no date_ is provided, the current date will be used.
        """
        params = {"RouteID": route.route_id}
        if date_:
            params["Date"] = date_.strftime("%Y-%m-%d")

        data = cast(
            RoutePathData,
            await self.client.fetch(BusEndpoint.ROUTE_PATH, params=params),
        )
        return RoutePath(self, data)

    async def get_route_schedule(
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
            await self.client.fetch(BusEndpoint.ROUTE_SCHEDULE, params=params),
        )
        return RouteSchedule(self, route, data)

    async def get_next_buses_at_stop(self, stop: Stop) -> list[NextBus]:
        """Return next buses for a given stop."""
        data = await self.client.fetch(
            BusEndpoint.NEXT_BUSES, params={"StopID": stop.stop_id}
        )
        return [NextBus(self, next_bus_data) for next_bus_data in data["Predictions"]]

    async def get_stop_schedule(
        self, stop: Stop, date_: date | None = None
    ) -> list[StopArrival]:
        """
        Return schedule for a given stop.

        If no date_ is provided, the current date will be used.
        """
        params = {"StopID": stop.stop_id}
        if date_:
            params["Date"] = date_.strftime("%Y-%m-%d")

        data = await self.client.fetch(BusEndpoint.STOP_SCHEDULE, params=params)
        return sorted(
            [
                StopArrival(self, stop, stop_arrival_schedule)
                for stop_arrival_schedule in data["ScheduleArrivals"]
            ],
            key=lambda stop_arrival_schedule: stop_arrival_schedule.schedule_time,
        )
