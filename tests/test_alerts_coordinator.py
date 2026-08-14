"""Smoke tests for the MTA alerts coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mta_subway.const import ALERTS_API_URL
from custom_components.mta_subway.coordinator import MTAAlertsCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.test_util.aiohttp import (
        AiohttpClientMocker,
    )


SAMPLE_ALERTS_PAYLOAD: dict[str, object] = {
    "header": {"timestamp": 1778283933},
    "entity": [
        {
            "id": "lmm:alert:1",
            "alert": {
                "active_period": [{"start": 1000000000}],
                "informed_entity": [{"agency_id": "MTASBWY", "route_id": "1"}],
                "header_text": {
                    "translation": [
                        {"text": "Downtown 1 trains are delayed.", "language": "en"}
                    ]
                },
                "transit_realtime.mercury_alert": {"alert_type": "Delays"},
            },
        },
        {
            "id": "lmm:alert:2",
            "alert": {
                "active_period": [{"start": 1000000000}],
                "informed_entity": [{"agency_id": "MTASBWY", "route_id": "L"}],
                "header_text": {
                    "translation": [{"text": "L line weekend work.", "language": "en"}]
                },
                "transit_realtime.mercury_alert": {"alert_type": "Planned Work"},
            },
        },
    ],
}


async def test_alerts_update_success(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(ALERTS_API_URL, json=SAMPLE_ALERTS_PAYLOAD)
    coordinator = MTAAlertsCoordinator(hass)
    await coordinator.async_refresh()

    assert coordinator.last_update_success
    assert coordinator.data is not None
    assert len(coordinator.data) == 2
    first = coordinator.data[0]
    assert first.id == "lmm:alert:1"
    assert first.alert.alert_type == "Delays"
    assert first.alert.affects_route("1")
    assert not first.alert.affects_route("L")


async def test_alerts_http_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(ALERTS_API_URL, status=500)
    coordinator = MTAAlertsCoordinator(hass)
    await coordinator.async_refresh()

    assert not coordinator.last_update_success
    assert isinstance(coordinator.last_exception, UpdateFailed)


async def test_alerts_unchanged_returns_same_instance(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Equal payloads short-circuit so coordinator.data identity is preserved."""
    aioclient_mock.get(ALERTS_API_URL, json=SAMPLE_ALERTS_PAYLOAD)
    coordinator = MTAAlertsCoordinator(hass)
    await coordinator.async_refresh()
    first = coordinator.data
    await coordinator.async_refresh()

    assert coordinator.data is first


async def test_alerts_empty_feed(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(ALERTS_API_URL, json={"header": {}, "entity": []})
    coordinator = MTAAlertsCoordinator(hass)
    await coordinator.async_refresh()

    assert coordinator.last_update_success
    assert coordinator.data == []
