"""Smoke tests for the MTA Subway coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aioresponses import aioresponses
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mta_subway.const import API_URL
from custom_components.mta_subway.coordinator import MTASubwayCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


SAMPLE_PAYLOAD: dict[str, object] = {
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


async def test_update_data_success(hass: HomeAssistant) -> None:
    coordinator = MTASubwayCoordinator(hass)
    with aioresponses() as mocked:
        mocked.get(API_URL, payload=SAMPLE_PAYLOAD)  # pyright: ignore[reportUnknownMemberType]
        await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data is not None
    assert coordinator.data["1"].status == "Good Service"
    assert coordinator.data["1"].color == "#ee352e"


async def test_update_data_http_error(hass: HomeAssistant) -> None:
    coordinator = MTASubwayCoordinator(hass)
    with aioresponses() as mocked:
        mocked.get(API_URL, status=500)  # pyright: ignore[reportUnknownMemberType]
        await coordinator.async_refresh()
    assert not coordinator.last_update_success
    assert isinstance(coordinator.last_exception, UpdateFailed)


async def test_update_data_unchanged_returns_same_instance(hass: HomeAssistant) -> None:
    """Equal payloads short-circuit so coordinator.data identity is preserved."""
    coordinator = MTASubwayCoordinator(hass)
    with aioresponses() as mocked:
        mocked.get(API_URL, payload=SAMPLE_PAYLOAD, repeat=True)  # pyright: ignore[reportUnknownMemberType]
        await coordinator.async_refresh()
        first = coordinator.data
        await coordinator.async_refresh()

    assert coordinator.data is first


async def test_update_data_missing_routes(hass: HomeAssistant) -> None:
    coordinator = MTASubwayCoordinator(hass)
    with aioresponses() as mocked:
        mocked.get(API_URL, payload={"timestamp": 0})  # pyright: ignore[reportUnknownMemberType]
        await coordinator.async_refresh()
    assert not coordinator.last_update_success
    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert "routes" in str(coordinator.last_exception)
