"""Test pywmataio util module."""
from wmataio.client import Client
from wmataio.models.coordinates import Coordinates
from wmataio.util import (
    get_closest_stop_or_station_pairs_to_coordinates,
    get_lat_long_from_address,
)


async def test_get_lat_long_from_address(geocode_responses):
    """Test get_lat_long_from_address function."""
    assert await get_lat_long_from_address(
        "4600 Silver Hill Rd, Washington, DC 20233"
    ) == Coordinates(38.845989080537514, -76.9274328556918)

    assert (
        await get_lat_long_from_address(
            "Tower Bridge Rd, London SE1 2UP, United Kingdom"
        )
        is None
    )


async def test_get_closest_stop_or_station_pairs_to_coordinates(wmata_responses):
    """Test get_closest_stop_or_station_pairs_to_coordinates function."""
    client = Client("", test_mode=True)
    await client.bus.load_data()

    # Test with max_pairs
    pairs = await get_closest_stop_or_station_pairs_to_coordinates(
        client.bus,
        client.bus.stops,
        Coordinates(38.9579014, -77.0343505),
        Coordinates(38.9200463, -77.0342637),
        lambda x: x.routes,
        max_pairs=2,
    )
    assert len(pairs) == 2
    assert pairs == [
        ((client.bus.stops["1002631"], 0.07), (client.bus.stops["1001746"], 0.12)),
        ((client.bus.stops["1002920"], 0.11), (client.bus.stops["1001777"], 0.13)),
    ]

    # Test with max_total_distance
    pairs = await get_closest_stop_or_station_pairs_to_coordinates(
        client.bus,
        client.bus.stops,
        Coordinates(38.9579014, -77.0343505),
        Coordinates(38.9200463, -77.0342637),
        lambda x: x.routes,
        max_total_distance=0.2,
    )
    assert len(pairs) == 1
    assert pairs == [
        ((client.bus.stops["1002631"], 0.07), (client.bus.stops["1001746"], 0.12))
    ]
