"""Client for MetroRail APIs."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import cast

from aiohttp import ClientSession

from ..base_client import BaseClient
from .const import Endpoint
from .models.elevator_and_escalator_incident import ElevatorAndEscalatorIncident
from .models.incident import Incident
from .models.line import Line
from .models.position import Position
from .models.prediction import Prediction
from .models.standard_route import StandardRoute
from .models.station import Station
from .models.station_entrance import StationEntrance
from .models.station_parking import StationParking
from .models.station_timings import StationTime
from .models.station_to_station import (
    StationToStation,
    StationToStationInfoData,
    StationToStationPathData,
)
from .models.track_circuit import TrackCircuit


class MetroRail(BaseClient):
    """Class to represent client for MetroRail APIs."""

    lines: dict[str, Line]
    stations: dict[str, Station]

    def __init__(self, api_key: str, session: ClientSession | None = None):
        """Initialize."""
        super().__init__(api_key, session)
        self.lines = {}
        self.stations = {}

    async def get_all_lines(self) -> dict[str, Line]:
        """Get all lines."""
        standard_routes_data, lines_data = await asyncio.gather(
            self.fetch(Endpoint.STANDARD_ROUTES.value), self.fetch(Endpoint.LINES.value)
        )
        standard_routes = defaultdict(list)
        for standard_route_data in standard_routes_data["StandardRoutes"]:
            standard_route = StandardRoute(self, standard_route_data)
            standard_routes[standard_route.line_code].append(standard_route)
        return {
            line["LineCode"]: Line(self, line, standard_routes[line["LineCode"]])
            for line in lines_data["Lines"]
        }

    async def get_all_stations(self) -> dict[str, Station]:
        """Get all stations."""
        (
            station_parking_data,
            entrances_data,
            stations_times_data,
            stations_data,
        ) = await asyncio.gather(
            self.fetch(Endpoint.STATION_PARKING_INFORMATION.value),
            self.fetch(Endpoint.STATION_ENTRANCES.value),
            self.fetch(Endpoint.STATION_TIMINGS.value),
            self.fetch(Endpoint.STATIONS.value),
        )

        station_parking = {
            station_parking["Code"]: StationParking(self, station_parking)
            for station_parking in station_parking_data["StationsParking"]
        }

        entrances = defaultdict(list)
        for entrance_data in entrances_data["Entrances"]:
            entrance = StationEntrance(self, entrance_data)
            for code_num in range(1, 3):
                if code := entrance_data[f"StationCode{code_num}"]:
                    entrances[code].append(entrance)

        stations_times = defaultdict(list)
        for station_time_data in stations_times_data["StationTimes"]:
            station_time = StationTime(self, station_time_data)
            stations_times[station_time.code].append(station_time)

        return {
            station_data["Code"]: Station(
                self,
                station_data,
                station_parking[station_data["Code"]],
                entrances[station_data["Code"]],
                stations_times[station_data["Code"]],
            )
            for station_data in stations_data["Stations"]
        }

    async def load_data(self) -> None:
        """Setup the client."""
        self.lines = await self.get_all_lines()
        self.stations = await self.get_all_stations()

    async def station_to_station(
        self, from_station: Station, to_station: Station
    ) -> StationToStation:
        """Get the path from one station to another."""
        params = {
            "FromStationCode": from_station.code,
            "ToStationCode": to_station.code,
        }
        path_data = cast(
            StationToStationPathData,
            await self.fetch(Endpoint.STATION_TO_STATION_PATH.value, params=params),
        )
        info_data = cast(
            StationToStationInfoData,
            await self.fetch(Endpoint.STATION_TO_STATION_INFO.value, params=params),
        )
        return StationToStation(self, path_data, info_data)

    async def elevator_escalator_incidents(
        self, station: Station | None = None
    ) -> list[ElevatorAndEscalatorIncident]:
        """Get elevator and escalator incidents."""
        params = {}
        if station:
            params["StationCode"] = station.code
        data = await self.fetch(
            Endpoint.ELEVATOR_ESCALATOR_INCIDENTS.value, params=params
        )
        return sorted(
            [
                ElevatorAndEscalatorIncident(self, elevator_escalator_data)
                for elevator_escalator_data in data["ElevatorIncidents"]
            ],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def incidents(self) -> list[Incident]:
        """Get rail incidents."""
        data = await self.fetch(Endpoint.INCIDENTS.value)
        return sorted(
            [Incident(self, incident_data) for incident_data in data["Incidents"]],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def next_trains_at_station(
        self, stations: Station | list[Station]
    ) -> list[Prediction]:
        """Return next trains for given station(s)."""
        if not isinstance(stations, list):
            stations = [stations]
        station_codes = ",".join([station.code for station in stations])
        data = await self.fetch(
            Endpoint.NEXT_TRAINS.value, params={"StationCodes": station_codes}
        )
        return [Prediction(self, prediction) for prediction in data["Trains"]]

    async def live_positions(self) -> list[Position]:
        """Get live positions."""
        data = await self.fetch(
            Endpoint.TRAIN_POSITIONS.value, params={"contentType": "json"}
        )
        return [
            Position(self, train_position) for train_position in data["TrainPositions"]
        ]

    async def track_circuits(self) -> list[TrackCircuit]:
        """Get track circuits."""
        track_circuits_data = await self.fetch(
            Endpoint.TRACK_CIRCUITS.value, params={"contentType": "json"}
        )
        track_circuits: list[TrackCircuit] = []
        for track_circuit in track_circuits_data:
            track_circuits.append(TrackCircuit(self, track_circuits, track_circuit))
        return track_circuits
