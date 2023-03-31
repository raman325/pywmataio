"""Constants for WMATA API."""
from zoneinfo import ZoneInfo

BASE_URL = "https://api.wmata.com"
TZ = ZoneInfo("US/Eastern")
HEADER_PREFIX = "wmataio"
CLASS_HEADER = f"{HEADER_PREFIX}-class"
ENUM_HEADER = f"{HEADER_PREFIX}-enum"
ADDITIONAL_PATH_HEADER = f"{HEADER_PREFIX}-additional-path"
