"""
Sensor for checking the status of NYC MTA Subway lines.
"""

import logging
import re
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_LINE = "line"
SCAN_INTERVAL = timedelta(seconds=60)

URL = "https://www.goodservice.io/api/routes?detailed=1"
ICONS = "https://raw.githubusercontent.com/iicky/homeassistant-mta-subway/main/icons"


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


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_LINE):
        vol.All(cv.ensure_list, [vol.In(list(SUBWAY_LINES))]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the MTA Subway sensors.
    """
    data = GoodServiceData()
    data.update()
    sensors = [
        MTASubwaySensor(line, data)
        for line in config.get(CONF_LINE)
    ]
    add_devices(sensors, True)

class MTASubwaySensor(Entity):
    """ Sensor that reads the status for an MTA Subway line.
    """
    def __init__(self, name, data):
        """ Initalize the sensor.
        """
        self._name = "MTA Subway " + str(name)
        self._line = name
        self._data = data
        self._route_data = None
        self._state = None

    @property
    def name(self):
        """ Returns the name of the sensor.
        """
        return self._name

    @property
    def state(self):
        """ Returns the state of the sensor.
        """
        return self._state

    @property
    def entity_picture(self):
        """ Returns the icon used for the frontend.
        """
        return f"{ICONS}/{str(self._line).upper()}.svg"

    @property
    def icon(self):
        """ Returns the icon used for the frontend.
        """
        return "mdi:subway"

    @property
    def extra_state_attributes (self):
        """ Returns the attributes of the sensor.
        """
        attrs = {}
        attrs["color"] = self._route_data["color"]
        attrs["scheduled"] = self._route_data["scheduled"]        
        has_direction_statuses = "direction_statuses" in self._route_data
        attrs["has_direction_statuses"] = has_direction_statuses
        attrs["direction_statuses"] = (
            self._route_data["direction_statuses"]
            if has_direction_statuses
            else {"north": None, "south": None}
        )
        has_delay_summaries = "delay_summaries" in self._route_data
        attrs["has_delay_summaries"] = has_delay_summaries
        attrs["delay_summaries"] = (
            self._route_data["delay_summaries"]
            if has_delay_summaries
            else {"north": None, "south": None}
        )
        has_service_irregularity_summaries = "service_irregularity_summaries" in self._route_data
        attrs["has_service_irregularity_summaries"] = has_service_irregularity_summaries
        attrs["service_irregularity_summaries"] = (
            self._route_data["service_irregularity_summaries"]
            if has_service_irregularity_summaries
            else {"north": None, "south": None}
        )
        has_service_change_summaries = "service_change_summaries" in self._route_data
        attrs["has_service_change_summaries"] = has_service_change_summaries
        attrs["service_change_summaries"] = (
            self._route_data["service_change_summaries"]
            if has_service_change_summaries
            else {"both": [], "north": [], "south": []}
        )
        return attrs

    def update(self):
        """ Updates the sensor.
        """
        self._data.update()
        self._route_data = self._data.data["routes"][self._line]
        
        # Update sensor state
        self._state = self._route_data["status"]

class GoodServiceData(object):
    """ Query goodservice.io API.
    """

    def __init__(self):
        self.data = None

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """ Update data based on SCAN_INTERVAL.
        """
        response = requests.get(URL)
        if response.status_code != 200:
            _LOGGER.warning("Invalid response from goodservice.io API.")
        else:
            self.data = response.json()
