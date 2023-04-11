"""Test pywmataio client for trains."""
from datetime import date, datetime, time

from wmataio.client import Client
from wmataio.const import TZ
from wmataio.rail.models.live_position import TrainDirection


async def test_rail_apis(wmata_responses):
    """Callback for aioresponse."""
    client = Client("", test_mode=True)
    await client.rail.load_data()
    assert client.rail.lines
    assert client.rail.stations

    assert len(client.rail.lines) == 6
    line = client.rail.lines["BL"]
    assert line.line_code == "BL"
    assert line.display_name == "Blue"
    assert line.start_station_code == "J03"
    assert line.start_station == client.rail.stations["J03"]
    assert line.end_station_code == "G05"
    assert line.end_station == client.rail.stations["G05"]
    assert line.internal_destination_code_1 is None
    assert line.internal_destination_1 is None
    assert line.internal_destination_code_2 is None
    assert line.internal_destination_2 is None
    assert hash(line) == hash("BL")

    assert len(line.standard_routes) == 2
    standard_route = line.standard_routes[0]
    assert standard_route.line_code == "BL"
    assert standard_route.line == line
    assert standard_route.track_number == 1
    assert len(standard_route.track_circuits) == 415

    track_circuit = standard_route.track_circuits[0]
    assert track_circuit.sequence_number == 0
    assert track_circuit.circuit_id == 2603
    assert track_circuit.station_code is None
    assert track_circuit.station is None

    assert len(client.rail.stations) == 101
    station = client.rail.stations["A01"]
    assert station.station_code == "A01"
    assert station.name == "Metro Center"
    assert station.station_together_code_1 == "C01"
    assert station.station_together_1 == client.rail.stations["C01"]
    assert station.station_together_code_2 is None
    assert station.station_together_2 is None
    assert station.line_codes == ["RD"]
    assert station.lines == [client.rail.lines["RD"]]
    assert station.coordinates.latitude == 38.898303
    assert station.coordinates.longitude == -77.028099
    assert station.address.street == "607 13th St. NW"
    assert station.address.city == "Washington"
    assert station.address.state == "DC"
    assert station.address.zip_code == "20005"
    assert len(station.entrances) == 8
    assert len(station.station_times) == 1
    assert station.parking is None
    assert hash(station) == hash("A01")

    entrance = station.entrances[0]
    assert entrance.entrance_id == "273"
    assert entrance.name == "11TH ST NW & G ST NW"
    assert entrance.station_code_1 == "A01"
    assert entrance.station_1 == client.rail.stations["A01"]
    assert entrance.station_code_2 == "C01"
    assert entrance.station_2 == client.rail.stations["C01"]
    assert entrance.description == (
        "Building Entrance from the southeast corner of 11th St NW and G St NW."
    )
    assert entrance.coordinates.latitude == 38.898073
    assert entrance.coordinates.longitude == -77.026789

    station_time = station.station_times[0]
    assert station_time.station_code == "A01"
    assert station_time.station == client.rail.stations["A01"]
    assert station_time.name == "Metro Center"

    day_time = station_time.get_day_time(date(2023, 3, 31))
    assert day_time.day == "Friday"
    assert day_time.day_of_week == 5
    assert day_time.opening_time == time(5, 14, 0, tzinfo=TZ)
    assert len(day_time.first_trains) == 2
    assert len(day_time.last_trains) == 2

    train_timing = day_time.first_trains[0]
    assert train_timing.time == time(5, 31, 0, tzinfo=TZ)
    assert train_timing.destination_station_code == "A15"
    assert train_timing.destination_station == client.rail.stations["A15"]

    parking = client.rail.stations["A07"].parking
    assert parking.code == "A07"
    assert parking.notes is None
    assert parking.all_day_parking.total_count == 0
    assert parking.all_day_parking.rider_cost is None
    assert parking.all_day_parking.non_rider_cost is None
    assert parking.all_day_parking.saturday_rider_cost is None
    assert parking.all_day_parking.saturday_non_rider_cost is None
    assert parking.short_term_parking.total_count == 17
    assert parking.short_term_parking.notes == (
        "Parking available 8:30 AM - 3:30 PM and 7 PM - 2 AM."
    )

    station_to_station = await client.rail.get_station_to_station_data(
        client.rail.stations["A15"], client.rail.stations["A01"]
    )
    assert len(station_to_station.path) == 15
    path_item = station_to_station.path[0]
    assert path_item.line_code == "RD"
    assert path_item.line == client.rail.lines["RD"]
    assert path_item.station_code == "A15"
    assert path_item.station == client.rail.stations["A15"]
    assert path_item.sequence_number == 1
    assert path_item.distance_to_previous == 0
    assert len(station_to_station.info) == 1
    info = station_to_station.info[0]
    assert info.source_station_code == "A15"
    assert info.source_station == client.rail.stations["A15"]
    assert info.destination_station_code == "A01"
    assert info.destination_station == client.rail.stations["A01"]
    assert info.composite_miles == 17.44
    assert info.rail_time == 36
    assert info.rail_fare.peak_time == 6.0
    assert info.rail_fare.off_peak_time == 3.85
    assert info.rail_fare.senior_disabled == 3.0

    station_to_station = await client.rail.get_station_to_station_data(
        client.rail.stations["A15"], client.rail.stations["N12"]
    )
    assert len(station_to_station.path) == 0

    elevator_escalator_incidents = await client.rail.get_elevator_escalator_incidents(
        client.rail.stations["A01"]
    )
    assert len(elevator_escalator_incidents) == 1

    elevator_escalator_incidents = await client.rail.get_elevator_escalator_incidents()
    assert len(elevator_escalator_incidents) == 34
    elevator_escalator_incident = elevator_escalator_incidents[0]
    assert elevator_escalator_incident.station_code == "C05"
    assert elevator_escalator_incident.station == client.rail.stations["C05"]
    assert elevator_escalator_incident.station_name == "Rosslyn"
    assert elevator_escalator_incident.unit_type == "ELEVATOR"
    assert elevator_escalator_incident.unit_name == "C05E03"
    assert elevator_escalator_incident.location_description == (
        "Elevator between street, and upper platform"
    )
    assert elevator_escalator_incident.symptom_description == "Service Call"
    assert elevator_escalator_incident.date_out_of_service == datetime(
        2023, 3, 31, 21, 5, 0, tzinfo=TZ
    )
    assert elevator_escalator_incident.date_updated == datetime(
        2023, 3, 31, 22, 11, 57, tzinfo=TZ
    )
    assert elevator_escalator_incident.estimated_return_to_service == datetime(
        2023, 4, 2, 23, 59, 59, tzinfo=TZ
    )

    rail_incidents = await client.rail.get_rail_incidents()
    assert len(rail_incidents) == 1
    rail_incident = rail_incidents[0]
    assert rail_incident.incident_id == "038F7C95-840B-4830-8EC3-ACAA9390DA09"
    assert rail_incident.description == (
        "No YL train service due to the bridge & tunnel project until May 2023. "
        "Use shuttle buses or BL/GR Line trains as alternate travel options."
    )
    assert rail_incident.incident_type == "Alert"
    assert rail_incident.line_codes_affected == ["YL"]
    assert rail_incident.lines_affected == [client.rail.lines["YL"]]
    assert rail_incident.date_updated == datetime(2023, 3, 8, 5, 23, 33, tzinfo=TZ)

    next_trains = await client.rail.get_next_trains_at_station(
        client.rail.stations["A15"]
    )
    assert len(next_trains) == 2
    next_train = next_trains[0]
    assert next_train.num_cars is None
    assert next_train.destination_station_code == "B11"
    assert next_train.destination_station == client.rail.stations["B11"]
    assert next_train.destination_station_name == "Glenmont"
    assert next_train.group == 2
    assert next_train.line_code == "RD"
    assert next_train.line == client.rail.lines["RD"]
    assert next_train.location_code == "A15"
    assert next_train.location == client.rail.stations["A15"]
    assert next_train.location_name == "Shady Grove"
    assert next_train.minutes == 9

    live_positions = await client.rail.get_live_positions()
    assert len(live_positions) == 82
    live_position = list(live_positions.values())[0]
    assert live_position.train_id == "075"
    assert live_position.train_number == "000"
    assert live_position.car_count == 6
    assert live_position.direction == TrainDirection.SOUTHBOUND_OR_WESTBOUND
    assert live_position.circuit_id == 1
    assert live_position.destination_station_code is None
    assert live_position.destination_station is None
    assert live_position.line_code is None
    assert live_position.line is None
    assert live_position.seconds_at_location == 12157
    assert live_position.service_type == "Unknown"

    track_circuits = await client.rail.get_track_circuits()
    assert len(track_circuits) == 3315
    track_circuit = list(track_circuits.values())[0]
    assert track_circuit.track == 1
    assert track_circuit.circuit_id == 1
    assert len(track_circuit.neighbors) == 1
    neighbor = track_circuit.neighbors[0]
    assert neighbor.neighbor_type == "Right"
    assert neighbor.circuit_ids == [2]
    assert neighbor.circuits == [track_circuits[2]]
