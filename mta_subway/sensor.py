"""
Sensor for checking the status of NYC MTA Subway lines.
"""

import logging
import re
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from bs4 import BeautifulSoup as Soup
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_LINE = "line"
SCAN_INTERVAL = timedelta(seconds=60)

SUBWAY_LINES = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    "A",
    "C",
    "E",
    "B",
    "D",
    "F",
    "M",
    "G",
    "J",
    "Z",
    "L",
    "N",
    "Q",
    "R",
    "W",
    "S",
    "SI",
]

STATE_PRIORITY = {
    "Essential Service": 1,
    "Delays": 2,
    "Service Change": 3,
    "Local to Express": 4,
    "Planned Work": 5,
    "Good Service": 6,
}

URL = "http://web.mta.info/status/ServiceStatusSubway.xml"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_LINE):
        vol.All(cv.ensure_list, [vol.In(list(SUBWAY_LINES))]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the MTA Subway sensors.
    """
    data = MTASubwayData()
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
        self._state = None
        self._direction_0_state = None
        self._direction_1_state = None
        self._delays_description = None
        self._service_change_description = None
        self._planned_work_description = None

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
    def icon(self):
        """ Returns the icon used for the frontend.
        """
        return "mdi:subway"

    @property
    def entity_picture(self):
        """ Returns the icon used for the frontend.
        """
        return "/local/mta_subway/{}.svg".format(
            str(self._line).lower()
        )

    @property
    def device_state_attributes(self):
        """ Returns the attributes of the sensor.
        """
        attrs = {}
        attrs["direction_0_state"] = self._direction_0_state
        attrs["direction_1_state"] = self._direction_1_state
        attrs["delays_description"] = self._delays_description
        attrs["service_change_description"] = self._service_change_description
        attrs["planned_work_description"] = self._planned_work_description

        return attrs

    def update(self):
        """ Updates the sensor.
        """
        self._data.update()
        line_data = self._data.data[self._line]
        self._state = line_data["state"]
        self._direction_0_state = line_data["direction_0_state"]
        self._direction_1_state = line_data["direction_1_state"]
        self._delays_description = line_data["delays_description"]
        self._service_change_description = (
            line_data["service_change_description"]
        )
        self._planned_work_description = line_data["planned_work_description"]


class MTASubwayData(object):
    """ Query MTA Subway data from the XML feed.
    """

    def __init__(self):

        self.data = None

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """ Update data based on SCAN_INTERVAL.
        """
        response = requests.get(URL)
        if response.status_code != 200:
            _LOGGER.warning("Invalid response from MTA Subway XML feed.")
        else:
            self.data = parse_subway_status(response)


def parse_subway_status(data):
    """ Returns a nested dictionary of MTA subway line statues
        given an XML response.
    """
    # Set all line statuses to base status.
    line_status = {
        line: {
            "state": None,
            "direction_0_state": None,
            "direction_1_state": None,
            "delays_description": None,
            "service_change_description": None,
            "planned_work_description": None
        }
        for line in SUBWAY_LINES
    }

    # Parse MTA lines from XML
    soup = Soup(data.text, "xml")

    # Iterate over line lookup and parse status.
    for line in SUBWAY_LINES:

        # Rename the MTA alias for Shuttle (S).
        line_alias = "H" if line == "S" else str(line)

        # Search for line name in affected lines XML.
        line_re = re.compile("NYCT_" + line_alias + "$")
        hits = [
            _ for _ in soup.find_all("Affects")
            if _.findChildren("LineRef", text=line_re)
        ]

        # Set line status to Good Service if no status.
        if not hits:
            line_status[line].update({
                "state": "Good Service",
                "direction_0_state": "Good Service",
                "direction_1_state": "Good Service",
            })
            continue

        # Parse all subway line situations that contain
        # affected line.
        situations = [
            _.find_parent("PtSituationElement")
            for _ in hits
        ]

        # Parse subway line state.
        statuses = [
            _.ReasonName.text
            for _ in situations
        ]

        # Look for overlap of statuses with known states
        # in STATE_PRIORITY dictionary
        matches = set(
            STATE_PRIORITY.keys()
        ).intersection(set(statuses))

        # Set the current state using the minimum of the
        # ordinal STATE_PRIORITY dictionary, or unknown if
        # state does not exist in dictionary.
        if len(matches) > 0:
            line_status[line]["state"] = min(
                {_: STATE_PRIORITY[_] for _ in matches},
                key=STATE_PRIORITY.get
            )
        else:
            line_status[line]["state"] = "Unknown"

        # Determine state for each direction on the line.
        dir_states = {
            "0": ["Good Service"],
            "1": ["Good Service"],
        }
        for sit in situations:

            # Find affected line directions.
            directions = [
                _.DirectionRef.text
                for _ in sit.find_all("AffectedVehicleJourney")
                if _.findChildren("LineRef", text=line_re)
            ]

            # Add states to line direction.
            for dct in directions:
                dir_states[dct].append(sit.ReasonName.text)

        # Set the direction states using STATE_PRIORITY.
        for dct in dir_states:
            matches = set(
                STATE_PRIORITY.keys()
            ).intersection(set(dir_states[dct]))

            direction = "direction_{}_state".format(dct)

            if len(matches) > 0:
                line_status[line][direction] = min(
                    {_: STATE_PRIORITY[_] for _ in matches},
                    key=STATE_PRIORITY.get
                )
            else:
                line_status[line][direction] = "Unknown"

        # Set line status descriptions.
        for status in STATE_PRIORITY:
            desc_key = (
                status.lower().replace(" ", "_") +
                "_description"
            )

            descs = [
                _.find("Description").text
                for _ in situations
                if _.find("ReasonName").text == status
            ]
            if descs:
                line_status[line][desc_key] = (
                    descs if len(descs) > 1
                    else descs[0]
                )

    return line_status
