"""Constants for the MTA Subway integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "mta_subway"

CONF_LINE = "line"

API_URL = "https://api.subwaynow.app/routes?detailed=1"
ICONS_BASE = (
    "https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/main/icons"
)

UPDATE_INTERVAL = timedelta(seconds=60)

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
