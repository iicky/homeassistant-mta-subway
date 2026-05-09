"""Constants for the MTA Subway integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "mta_subway"

CONF_LINE = "line"

API_URL = "https://api.subwaynow.app/routes?detailed=1"
ALERTS_API_URL = (
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"
)
ICONS_BASE = (
    "https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/main/icons"
)

UPDATE_INTERVAL = timedelta(seconds=60)
ALERTS_UPDATE_INTERVAL = timedelta(seconds=60)

ALERT_CATEGORY_PLANNED_WORK = "planned_work"
ALERT_CATEGORY_DELAYS = "delays"
ALERT_CATEGORY_SERVICE_CHANGE = "service_change"

SUBWAY_LINES = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "6X",
    "7",
    "7X",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "FX",
    "G",
    "J",
    "L",
    "M",
    "N",
    "Q",
    "R",
    "GS",
    "FS",
    "H",
    "SI",
    "W",
    "Z",
]
