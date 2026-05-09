"""Tests for the diagnostics platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aioresponses import aioresponses
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mta_subway.const import (
    ALERTS_API_URL,
    API_URL,
    CONF_LINE,
    DOMAIN,
)
from custom_components.mta_subway.diagnostics import (
    async_get_config_entry_diagnostics,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


ROUTES_PAYLOAD: dict[str, object] = {
    "routes": {
        "1": {
            "id": "1",
            "name": "1",
            "color": "#ee352e",
            "status": "Delays",
            "scheduled": True,
        },
        "L": {
            "id": "L",
            "name": "L",
            "color": "#a7a9ac",
            "status": "Good Service",
            "scheduled": True,
        },
    }
}

ALERTS_PAYLOAD: dict[str, object] = {
    "header": {},
    "entity": [
        {
            "id": "alert:1",
            "alert": {
                "active_period": [{"start": 1000000000}],
                "informed_entity": [{"agency_id": "MTASBWY", "route_id": "1"}],
                "header_text": {
                    "translation": [{"text": "Delay on 1", "language": "en"}]
                },
                "transit_realtime.mercury_alert": {"alert_type": "Delays"},
            },
        }
    ],
}


async def test_diagnostics_dump(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_LINE: ["1", "L"]}, unique_id=DOMAIN
    )
    entry.add_to_hass(hass)
    assert await async_setup_component(hass, "http", {})

    with aioresponses() as mocked:
        mocked.get(API_URL, payload=ROUTES_PAYLOAD, repeat=True)
        mocked.get(ALERTS_API_URL, payload=ALERTS_PAYLOAD, repeat=True)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        diag = await async_get_config_entry_diagnostics(hass, entry)

    assert diag["config_entry"]["data"] == {CONF_LINE: ["1", "L"]}
    assert diag["routes"]["last_update_success"] is True
    assert diag["routes"]["count"] == 2
    assert diag["routes"]["lines"] == ["1", "L"]
    assert diag["routes"]["sample"] is not None
    assert diag["alerts"]["last_update_success"] is True
    assert diag["alerts"]["count"] == 1
    assert "Delays" in diag["alerts"]["alert_types"]
    assert diag["alerts"]["by_route"]["1"] == 1
    assert diag["alerts"]["by_route"]["L"] == 0
