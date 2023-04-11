"""Constants for WMATA API."""
from enum import Enum
from zoneinfo import ZoneInfo

BASE_WMATA_URL = "https://api.wmata.com"
TZ = ZoneInfo("US/Eastern")
HEADER_PREFIX = "wmataio"
CLASS_HEADER = f"{HEADER_PREFIX}-class"
ENUM_HEADER = f"{HEADER_PREFIX}-enum"
ADDITIONAL_PATH_HEADER = f"{HEADER_PREFIX}-additional-path"

GEOCODE_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
DEFAULT_GEOCODE_PARAMS = {
    "benchmark": "Public_AR_Current",
    "format": "json",
}


class WMATAEndpoint(Enum):
    """Generic WMATA Endpoints."""

    VALIDATE_API_KEY = f"{BASE_WMATA_URL}/Misc/Validate"
