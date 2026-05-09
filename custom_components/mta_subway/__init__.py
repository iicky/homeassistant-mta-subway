"""The MTA Subway integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform

from .const import DOMAIN, ICONS_BASE
from .coordinator import MTAAlertsCoordinator, MTASubwayCoordinator, MTASubwayData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

_ICONS_DIR = Path(__file__).parent / "icons"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the bundled subway-bullet icons as static assets."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(ICONS_BASE, str(_ICONS_DIR), True)]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MTA Subway from a config entry."""
    routes = MTASubwayCoordinator(hass)
    alerts = MTAAlertsCoordinator(hass)
    await routes.async_config_entry_first_refresh()
    await alerts.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = MTASubwayData(
        routes=routes, alerts=alerts
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
