"""Module for interacting with MetroRail API."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, cast

from .const import RailEndpoint
from .models.elevator_and_escalator_incident import ElevatorAndEscalatorIncident
from .models.line import Line
from .models.live_position import LiveTrainPosition
from .models.next_train import NextTrain
from .models.rail_incident import RailIncident
from .models.standard_route import StandardRoute
from .models.station import Station
from .models.station_entrance import StationEntrance
from .models.station_parking import StationParking
from .models.station_timings import StationTime
from .models.station_to_station import StationToStation, StationToStationPathData
from .models.track_circuit import TrackCircuit

if TYPE_CHECKING:
    from ..client import Client


class MetroRail:
    """Class to represent client for MetroRail APIs."""

    client: "Client"
    lines: dict[str, Line]
    stations: dict[str, Station]

    def __init__(self, client: "Client") -> None:
        """Initialize."""
        self.client = client
        self.lines = {}
        self.stations = {}

    async def load_data(self) -> None:
        """Load the base data."""
        self.lines = await self.get_all_lines()
        self.stations = await self.get_stations()

    async def get_all_lines(self) -> dict[str, Line]:
        """Get all lines."""
        standard_routes_data, lines_data = await asyncio.gather(
            self.client.fetch(
                RailEndpoint.STANDARD_ROUTES, params={"contentType": "json"}
            ),
            self.client.fetch(RailEndpoint.LINES),
        )
        standard_routes = defaultdict(list)
        for standard_route_data in standard_routes_data["StandardRoutes"]:
            standard_route = StandardRoute(self, standard_route_data)
            standard_routes[standard_route.line_code].append(standard_route)
        return {
            line["LineCode"]: Line(self, line, standard_routes[line["LineCode"]])
            for line in lines_data["Lines"]
        }

    def __get_entrances(
        self, entrances_data: dict
    ) -> defaultdict[str, list[StationEntrance]]:
        """Get entrances from entrances data."""
        entrances = defaultdict(list)
        for entrance_data in entrances_data["Entrances"]:
            entrance = StationEntrance(self, entrance_data)
            for code_num in range(1, 3):
                if code := entrance_data[f"StationCode{code_num}"]:
                    entrances[code].append(entrance)
        return entrances

    def __get_station_times(
        self, stations_times_data: dict
    ) -> defaultdict[str, list[StationTime]]:
        """Get station times from station times data."""
        stations_times = defaultdict(list)
        for station_time_data in stations_times_data["StationTimes"]:
            station_time = StationTime(self, station_time_data)
            stations_times[station_time.station_code].append(station_time)
        return stations_times

    async def get_stations(self, line: Line | None = None) -> dict[str, Station]:
        """Get all stations."""
        params = {}
        if line:
            params = {"LineCode": line.line_code}
        (
            station_parking_data,
            entrances_data,
            stations_times_data,
            stations_data,
        ) = await asyncio.gather(
            self.client.fetch(RailEndpoint.STATION_PARKING_INFORMATION),
            self.client.fetch(RailEndpoint.STATION_ENTRANCES),
            self.client.fetch(RailEndpoint.STATION_TIMINGS),
            self.client.fetch(RailEndpoint.STATIONS, params=params),
        )

        station_parking = {
            station_parking["Code"]: StationParking(self, station_parking)
            for station_parking in station_parking_data["StationsParking"]
        }
        entrances = self.__get_entrances(entrances_data)
        stations_times = self.__get_station_times(stations_times_data)

        return {
            station_data["Code"]: Station(
                self,
                station_data,
                station_parking.get(station_data["Code"]),
                entrances[station_data["Code"]],
                stations_times[station_data["Code"]],
            )
            for station_data in stations_data["Stations"]
        }

    async def get_station_to_station_data(
        self, from_station: Station, to_station: Station
    ) -> StationToStation:
        """Get the path from one station to another."""
        params = {
            "FromStationCode": from_station.station_code,
            "ToStationCode": to_station.station_code,
        }
        path_data = cast(
            StationToStationPathData,
            await self.client.fetch(
                RailEndpoint.STATION_TO_STATION_PATH, params=params
            ),
        )
        info_data = await self.client.fetch(
            RailEndpoint.STATION_TO_STATION_INFO, params=params
        )
        return StationToStation(
            self,
            from_station,
            to_station,
            path_data,
            info_data["StationToStationInfos"],
        )

    async def get_elevator_escalator_incidents(
        self, station: Station | None = None
    ) -> list[ElevatorAndEscalatorIncident]:
        """Get elevator and escalator incidents."""
        params = {}
        if station:
            params["StationCode"] = station.station_code
        data = await self.client.fetch(
            RailEndpoint.ELEVATOR_ESCALATOR_INCIDENTS, params=params
        )
        return sorted(
            [
                ElevatorAndEscalatorIncident(self, elevator_escalator_data)
                for elevator_escalator_data in data["ElevatorIncidents"]
            ],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def get_rail_incidents(self) -> list[RailIncident]:
        """Get rail incidents."""
        data = await self.client.fetch(RailEndpoint.RAIL_INCIDENTS)
        return sorted(
            [RailIncident(self, incident_data) for incident_data in data["Incidents"]],
            reverse=True,
            key=lambda incident: incident.date_updated,
        )

    async def get_next_trains_at_station(
        self, stations: Station | list[Station]
    ) -> list[NextTrain]:
        """Return next trains for given station(s)."""

        def key_func(train: NextTrain) -> int:
            if not train.minutes:
                return -3
            if train.minutes == "BRD":
                return -2
            if train.minutes == "ARR":
                return -1
            assert isinstance(train.minutes, int)
            return train.minutes

        if not isinstance(stations, list):
            stations = [stations]
        station_codes = ",".join([station.station_code for station in stations])
        data = await self.client.fetch(
            RailEndpoint.NEXT_TRAINS, additional_path=station_codes
        )
        return sorted(
            [NextTrain(self, next_train_data) for next_train_data in data["Trains"]],
            key=key_func,
        )

    async def get_live_positions(self) -> dict[str, LiveTrainPosition]:
        """Get live train positions."""
        data = await self.client.fetch(
            RailEndpoint.TRAIN_POSITIONS, params={"contentType": "json"}
        )
        return {
            train_position["TrainId"]: LiveTrainPosition(self, train_position)
            for train_position in data["TrainPositions"]
        }

    async def get_track_circuits(self) -> dict[int, TrackCircuit]:
        """Get track circuits."""
        track_circuits_data = await self.client.fetch(
            RailEndpoint.TRACK_CIRCUITS, params={"contentType": "json"}
        )
        track_circuits: dict[int, TrackCircuit] = {}
        for track_circuit in track_circuits_data["TrackCircuits"]:
            track_circuits[track_circuit["CircuitId"]] = TrackCircuit(
                track_circuits, track_circuit
            )
        return track_circuits
