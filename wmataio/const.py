"""Constants for WMATA API."""
from enum import Enum
from zoneinfo import ZoneInfo

BASE_URL = "https://api.wmata.com"
TZ = ZoneInfo("US/Eastern")
HEADER_PREFIX = "wmataio"
CLASS_HEADER = f"{HEADER_PREFIX}-class"
ENUM_HEADER = f"{HEADER_PREFIX}-enum"
ADDITIONAL_PATH_HEADER = f"{HEADER_PREFIX}-additional-path"


class WMATAEndpoint(Enum):
    """Generic WMATA Endpoints."""

    VALIDATE_API_KEY = f"{BASE_URL}/Misc/Validate"
