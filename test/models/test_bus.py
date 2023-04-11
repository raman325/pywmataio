"""Test pywmataio client for buses."""
from datetime import date, datetime

from wmataio.bus.util import find_direct_route_start_end_stop_pairs
from wmataio.client import Client
from wmataio.const import TZ
from wmataio.models.area import Area


async def test_bus_apis(wmata_responses):
    """Callback for aioresponse."""
    client = Client("", test_mode=True)
    await client.bus.load_data()
    assert client.bus.routes
    assert client.bus.stops

    assert len(client.bus.routes) == 390

    route = client.bus.routes["10A"]
    assert route.route_id == "10A"
    assert route.name == "10A - HUNTINGTON STA - PENTAGON"
    assert route.line_description == "Alexandria-Pentagon Line"
    assert hash(route) == hash("10A")

    assert len(client.bus.stops) == 9360

    stop = client.bus.stops["3000454"]
    assert stop.coordinates.latitude == 38.820495
    assert stop.coordinates.longitude == -76.957391
    assert stop.name == "ST BARNABAS RD + LIME ST"
    assert stop.route_ids == ["D12", "D12*5"]
    assert stop.routes == {client.bus.routes["D12"], client.bus.routes["D12*5"]}
    assert hash(stop) == hash("3000454")

    positions = await client.bus.get_live_positions(route=client.bus.routes["10A"])
    assert positions
    assert len(positions) == 4

    positions = await client.bus.get_live_positions(
        area=Area(2000, 38.9031442, -77.0785817)
    )
    assert positions
    assert len(positions) == 3

    positions = await client.bus.get_live_positions()
    assert positions
    assert len(positions) == 301
    position = positions[0]
    assert position.vehicle_id == "2971"
    assert position.coordinates.latitude == 38.91981887817383
    assert position.coordinates.longitude == -77.22313690185547
    assert position.deviation == -1.0
    assert position.last_update == datetime(2023, 3, 31, 22, 17, 6, tzinfo=TZ)
    assert position.trip_id == "20801060"
    assert position.route_id == "28A"
    assert position.route == client.bus.routes["28A"]
    assert position.direction_text == "WEST"
    assert position.trip_headsign == "TYSONS"
    assert position.trip_start_time == datetime(2023, 3, 31, 20, 48, 0, tzinfo=TZ)
    assert position.trip_end_time == datetime(2023, 3, 31, 22, 1, 0, tzinfo=TZ)

    incidents = await client.bus.get_bus_incidents(route=client.bus.routes["10A"])
    assert not incidents

    incidents = await client.bus.get_bus_incidents()
    assert incidents
    assert len(incidents) == 6
    incident = incidents[0]
    assert incident.incident_id == "B1D890F9-0A65-4FA4-A9AA-565B61CEC94A"
    assert incident.incident_type == "Alert"
    assert incident.route_ids_affected == ["96"]
    assert incident.routes_affected == [client.bus.routes["96"]]
    assert incident.description == (
        "Due to an incident at Tenleytown Station on the 96 route, "
        "buses are experiencing delays."
    )
    assert incident.date_updated == datetime(2023, 3, 31, 22, 13, 54, tzinfo=TZ)

    route_path = await client.bus.get_route_path(
        route=client.bus.routes["10A"], date_=date(2023, 3, 31)
    )
    assert route_path

    route_path = await client.bus.get_route_path(route=client.bus.routes["10A"])
    assert route_path
    assert route_path.route_id == "10A"
    assert route_path.route == client.bus.routes["10A"]
    assert route_path.name == "10A - PENTAGON - HUNTINGTON STA"
    assert len(route_path.path_directions) == 2
    assert route_path.path_directions[1]
    direction = route_path.path_directions[0]
    assert direction.trip_headsign == "PENTAGON"
    assert direction.direction == "NORTH"
    assert direction.direction_num == 0
    assert len(direction.shapes) == 184
    shape = direction.shapes[0]
    assert shape.coordinates.latitude == 38.79524
    assert shape.coordinates.longitude == -77.075059
    assert shape.sequence_number == 1
    assert len(direction.stops) == 57
    stop = direction.stops[0]
    assert stop.stop_id == "5002201"
    assert stop.name == "HUNTINGTON STATION (N) + BUS BAY B"
    assert stop.coordinates.latitude == 38.79524
    assert stop.coordinates.longitude == -77.075059
    assert stop.route_ids == ["10A"]
    assert stop.routes == {client.bus.routes["10A"]}

    route_schedule = await client.bus.get_route_schedule(
        route=client.bus.routes["10A"], date_=date(2023, 3, 31)
    )
    assert route_schedule

    route_schedule = await client.bus.get_route_schedule(route=client.bus.routes["10A"])
    assert route_schedule
    assert route_schedule.route == client.bus.routes["10A"]
    assert len(route_schedule.directions_schedules) == 2
    assert route_schedule.directions_schedules[1]
    direction_schedules = route_schedule.directions_schedules[0]
    assert len(direction_schedules) == 41
    direction_schedule = direction_schedules[0]
    assert direction_schedule.route_id == "10A"
    assert direction_schedule.route == client.bus.routes["10A"]
    assert direction_schedule.trip_direction == "NORTH"
    assert direction_schedule.trip_headsign == "PENTAGON"
    assert direction_schedule.start_time == datetime(2023, 3, 31, 4, 25, tzinfo=TZ)
    assert direction_schedule.end_time == datetime(2023, 3, 31, 5, 7, tzinfo=TZ)
    assert direction_schedule.trip_id == "30399060"
    assert len(direction_schedule.stop_times) == 57
    stop_time = direction_schedule.stop_times[0]
    assert stop_time.stop_id == "5002201"
    assert stop_time.stop == client.bus.stops["5002201"]
    assert stop_time.stop_name == "HUNTINGTON STATION (N) + BUS BAY B"
    assert stop_time.stop_sequence == 1
    assert stop_time.time == datetime(2023, 3, 31, 4, 25, tzinfo=TZ)

    next_buses = await client.bus.get_next_buses_at_stop(client.bus.stops["1002916"])
    assert len(next_buses) == 3
    next_bus = next_buses[0]
    assert next_bus.route_id == "S2"
    assert next_bus.route == client.bus.routes["S2"]
    assert next_bus.direction_text == "North to Silver Spring Station"
    assert next_bus.direction_number == 0
    assert next_bus.minutes == 0
    assert next_bus.vehicle_id == "5528"
    assert next_bus.trip_id == "33841060"

    assert (
        len(
            await client.bus.get_stop_schedule(
                client.bus.stops["1000533"], date_=date(2023, 3, 31)
            )
        )
        == 50
    )
    stop_schedule = await client.bus.get_stop_schedule(client.bus.stops["1000533"])
    assert len(stop_schedule) == 50
    stop_arrival = stop_schedule[0]
    assert stop_arrival.route_id == "V4"
    assert stop_arrival.route == client.bus.routes["V4"]
    assert stop_arrival.trip_direction_text == "EAST"
    assert stop_arrival.trip_headsign == "CAPITOL HEIGHTS STATION"
    assert stop_arrival.trip_id == "3944060"
    assert stop_arrival.direction_number == 0
    assert stop_arrival.schedule_time == datetime(2023, 3, 31, 4, 53, 28, tzinfo=TZ)
    assert stop_arrival.start_time == datetime(2023, 3, 31, 4, 47, tzinfo=TZ)
    assert stop_arrival.end_time == datetime(2023, 3, 31, 5, 24, tzinfo=TZ)


async def test_bus_utils(wmata_responses):
    """Tests for MetroBus utility functions."""
    client = Client("", test_mode=True)
    await client.bus.load_data()
    stop_1 = client.bus.stops["5002201"]
    stop_2 = client.bus.stops["4000025"]
    data = await find_direct_route_start_end_stop_pairs(
        client, {stop_1, stop_2}, {stop_1, stop_2}
    )
    assert len(data) == 1
    assert len(data[(stop_1, stop_2)]) == 1
    assert next(direction for direction in data[(stop_1, stop_2)]).direction == "NORTH"

    assert (stop_2, stop_1) not in data
