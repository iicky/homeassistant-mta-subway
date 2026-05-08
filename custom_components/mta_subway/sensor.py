"""Sensor platform for MTA Subway service status."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LINE, DOMAIN, ICONS_BASE, SUBWAY_LINES
from .coordinator import MTASubwayCoordinator

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(  # pyright: ignore[reportUnknownMemberType]
    {
        vol.Required(CONF_LINE): vol.All(cv.ensure_list, [vol.In(SUBWAY_LINES)]),
    }
)

_DIRECTION_DEFAULT: dict[str, Any] = {"north": None, "south": None}
_CHANGE_DEFAULT: dict[str, Any] = {"both": [], "north": [], "south": []}


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up MTA Subway sensors from YAML."""
    domain_data: dict[str, Any] = hass.data.setdefault(DOMAIN, {})
    coordinator: MTASubwayCoordinator | None = domain_data.get("coordinator")
    if coordinator is None:
        coordinator = MTASubwayCoordinator(hass)
        await coordinator.async_refresh()
        domain_data["coordinator"] = coordinator

    lines: list[str] = config[CONF_LINE]
    async_add_entities(MTASubwaySensor(coordinator, line) for line in lines)


class MTASubwaySensor(CoordinatorEntity[MTASubwayCoordinator], SensorEntity):
    """Service-status sensor for a single MTA Subway line."""

    _attr_icon = "mdi:subway"

    def __init__(self, coordinator: MTASubwayCoordinator, line: str) -> None:
        super().__init__(coordinator)
        self._line = line
        self._route_present = False
        self._attr_name = f"MTA Subway {line}"
        self._attr_unique_id = f"{DOMAIN}_{line.lower()}"
        self._attr_entity_picture = f"{ICONS_BASE}/{line.upper()}.svg"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "service")},
            name="MTA Subway",
            manufacturer="Metropolitan Transportation Authority",
            model="Subway service status",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.subwaynow.app/",
        )
        self._refresh_attrs()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._refresh_attrs()
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride]
        return super().available and self._route_present

    def _refresh_attrs(self) -> None:
        data = self.coordinator.data
        route: dict[str, Any] | None = data.get(self._line) if data else None
        if route is None:
            self._route_present = False
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
            return
        self._route_present = True
        self._attr_native_value = route.get("status")
        self._attr_extra_state_attributes = {
            "color": route.get("color"),
            "scheduled": route.get("scheduled"),
            "has_direction_statuses": "direction_statuses" in route,
            "direction_statuses": route.get("direction_statuses", _DIRECTION_DEFAULT),
            "has_delay_summaries": "delay_summaries" in route,
            "delay_summaries": route.get("delay_summaries", _DIRECTION_DEFAULT),
            "has_service_irregularity_summaries": "service_irregularity_summaries"
            in route,
            "service_irregularity_summaries": route.get(
                "service_irregularity_summaries", _DIRECTION_DEFAULT
            ),
            "has_service_change_summaries": "service_change_summaries" in route,
            "service_change_summaries": route.get(
                "service_change_summaries", _CHANGE_DEFAULT
            ),
        }
