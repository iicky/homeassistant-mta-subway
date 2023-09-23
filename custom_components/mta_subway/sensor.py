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
from homeassistant import config_entries

class MTASubwayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        # This step is called when user initializes a configuration flow from the UI.
        errors = {}
        if user_input is not None:
            # Validate the user input and if valid, create a new entry
            # For example:
            valid = await self._validate_input(user_input)
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_STATION] + " " + user_input[CONF_LINE],
                    data=user_input,
                )
            else:
                errors["base"] = "invalid_input"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_STATION): str,
                vol.Required(CONF_LINE): str,
            }),
            errors=errors,
        )
    
    async def _validate_input(self, user_input):
        # Perform validation of user input, possibly by making a request to the API
        # Return True if valid, else False
        pass


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
        attrs["direction_statuses"] = (
            self._route_data["direction_statuses"]
            if "direction_statuses" in self._route_data
            else {"north": None, "south": None}
        )
        attrs["delay_summaries"] = (
            self._route_data["delay_summaries"]
            if "delay_summaries" in self._route_data
            else {"north": None, "south": None}
        )
        attrs["service_irregularity_summaries"] = (
            self._route_data["service_irregularity_summaries"]
            if "service_irregularity_summaries" in self._route_data
            else {"north": None, "south": None}
        )
        attrs["service_change_summaries"] = (
            self._route_data["service_change_summaries"]
            if "service_change_summaries" in self._route_data
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

class GoodServiceData:
    async def get_arrival_times(self, station, line):
        # Make a request to the API to get the arrival times of the next two trains
        # for the specified line at the specified station.
        # Parse the response and return the required information.
        
        # Example:
        url = f"https://api.example.com/arrival_times?station={station}&line={line}"
        response = await self._session.get(url)
        data = await response.json()
        return data["arrival_times"]

class MTAArrivalTimeSensor(Entity):
    def __init__(self, station, line, data):
        self._station = station
        self._line = line
        self._data = data
        self._state = None
        # Initialize other required variables
    
    async def async_update(self):
        # Fetch the arrival time information for the specified station and line from the API
        # Update the state and attributes of the sensor with the retrieved information
        
        # Example:
        response = await self._data.get_arrival_times(self._station, self._line)
        self._state = response["next_arrival_time"]
