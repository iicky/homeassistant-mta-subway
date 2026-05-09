"""Tests for the MTA Subway integration setup and unload."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aioresponses import aioresponses
from homeassistant.config_entries import ConfigEntryState
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mta_subway.const import (
    ALERTS_API_URL,
    API_URL,
    CONF_LINE,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


ROUTES_PAYLOAD: dict[str, object] = {
    "routes": {
        "1": {
            "id": "1",
            "name": "1",
            "color": "#ee352e",
            "status": "Good Service",
            "scheduled": True,
        }
    },
    "timestamp": 1234567890,
}

ALERTS_PAYLOAD: dict[str, object] = {"header": {}, "entity": []}


async def test_setup_entry_loads_and_unloads(hass: HomeAssistant) -> None:
    """Full setup-and-unload cycle uses runtime_data and creates entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LINE: ["1"]},
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)
    assert await async_setup_component(hass, "http", {})

    with aioresponses() as mocked:
        mocked.get(API_URL, payload=ROUTES_PAYLOAD, repeat=True)
        mocked.get(ALERTS_API_URL, payload=ALERTS_PAYLOAD, repeat=True)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None
    assert entry.runtime_data.routes.data is not None
    assert "1" in entry.runtime_data.routes.data

    line_state = hass.states.get("sensor.mta_subway_1")
    assert line_state is not None
    assert line_state.state == "Good Service"

    north_state = hass.states.get("sensor.mta_subway_1_northbound")
    assert north_state is not None

    planned_work = hass.states.get("binary_sensor.mta_subway_1_planned_work")
    assert planned_work is not None
    assert planned_work.state == "off"

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_options_change_reloads_entry(hass: HomeAssistant) -> None:
    """Updating options triggers entry reload via update listener."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LINE: ["1"]},
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)
    assert await async_setup_component(hass, "http", {})

    with aioresponses() as mocked:
        mocked.get(API_URL, payload=ROUTES_PAYLOAD, repeat=True)
        mocked.get(ALERTS_API_URL, payload=ALERTS_PAYLOAD, repeat=True)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        hass.config_entries.async_update_entry(entry, options={CONF_LINE: ["1", "2"]})
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get("sensor.mta_subway_2") is not None
