"""Constants for the Wunderground PWS integration."""

DOMAIN = "wunderground_pws"

CONF_STATION_ID = "station_id"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"  # minutes

DEFAULT_SCAN_INTERVAL = 5  # minutes
MIN_SCAN_INTERVAL = 1
MAX_SCAN_INTERVAL = 1440

DASHBOARD_URL = "https://www.wunderground.com/dashboard/pws/{station_id}"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
