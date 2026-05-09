"""Binary sensor platform for MTA Subway alerts."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALERT_CATEGORY_DELAYS,
    ALERT_CATEGORY_PLANNED_WORK,
    ALERT_CATEGORY_SERVICE_CHANGE,
    CONF_LINE,
    DOMAIN,
)
from .coordinator import MTAAlertsCoordinator
from .models import AlertEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import MTASubwayConfigEntry


PARALLEL_UPDATES = 0


PLANNED_WORK_TYPES = frozenset({"Planned Work"})
DELAY_TYPES = frozenset({"Delays"})

MAX_TITLES_IN_ATTRS = 5


@dataclass(frozen=True)
class _Category:
    key: str
    label: str


CATEGORIES: list[_Category] = [
    _Category(ALERT_CATEGORY_PLANNED_WORK, "planned work"),
    _Category(ALERT_CATEGORY_DELAYS, "delays"),
    _Category(ALERT_CATEGORY_SERVICE_CHANGE, "service change"),
]


def _classify(alert_type: str | None) -> str:
    if alert_type in PLANNED_WORK_TYPES:
        return ALERT_CATEGORY_PLANNED_WORK
    if alert_type in DELAY_TYPES:
        return ALERT_CATEGORY_DELAYS
    return ALERT_CATEGORY_SERVICE_CHANGE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MTASubwayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up alert binary sensors from a config entry."""
    data = entry.runtime_data
    lines: list[str] = entry.options.get(CONF_LINE) or entry.data[CONF_LINE]
    async_add_entities(
        MTAAlertBinarySensor(data.alerts, line, category)
        for line in lines
        for category in CATEGORIES
    )


class MTAAlertBinarySensor(CoordinatorEntity[MTAAlertsCoordinator], BinarySensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Per-line, per-category binary sensor for MTA service alerts."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: MTAAlertsCoordinator,
        line: str,
        category: _Category,
    ) -> None:
        super().__init__(coordinator)
        self._line = line
        self._category = category
        self._matching: list[AlertEntity] = []
        self._attr_name = f"MTA Subway {line} {category.label}"
        self._attr_unique_id = f"{DOMAIN}_{line.lower()}_{category.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "service")},
            name="MTA Subway",
            manufacturer="Metropolitan Transportation Authority",
            model="Subway service status",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.subwaynow.app/",
        )
        self._refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._refresh()
        super()._handle_coordinator_update()

    def _refresh(self) -> None:
        now = int(time.time())
        all_alerts = self.coordinator.data or []
        self._matching = [
            entity
            for entity in all_alerts
            if entity.alert.affects_route(self._line)
            and entity.alert.is_active_at(now)
            and _classify(entity.alert.alert_type) == self._category.key
        ]
        self._attr_is_on = bool(self._matching)
        self._attr_extra_state_attributes = self._build_attrs()

    def _build_attrs(self) -> dict[str, Any]:
        titles: list[str] = []
        for entity in self._matching[:MAX_TITLES_IN_ATTRS]:
            text = entity.alert.header_text.text() if entity.alert.header_text else None
            if text:
                titles.append(text)
        alert_types = sorted(
            {
                entity.alert.alert_type
                for entity in self._matching
                if entity.alert.alert_type
            }
        )
        return {
            "count": len(self._matching),
            "titles": titles,
            "alert_types": alert_types,
        }
