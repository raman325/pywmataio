"""Test pywmataio util module."""

from wmataio.util import get_lat_long_from_address


async def test_get_lat_long_from_address(geocode_responses):
    """Test get_lat_long_from_address function."""
    assert await get_lat_long_from_address(
        "4600 Silver Hill Rd, Washington, DC 20233"
    ) == (-76.9274328556918, 38.845989080537514)

    assert (
        await get_lat_long_from_address(
            "Tower Bridge Rd, London SE1 2UP, United Kingdom"
        )
        is None
    )
