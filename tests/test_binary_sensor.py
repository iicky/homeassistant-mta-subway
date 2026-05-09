"""Smoke tests for the MTA alert binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from custom_components.mta_subway.binary_sensor import (
    CATEGORIES,
    MTAAlertBinarySensor,
)
from custom_components.mta_subway.coordinator import MTAAlertsCoordinator
from custom_components.mta_subway.models import AlertEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def _make_alert(
    alert_id: str,
    route_id: str,
    alert_type: str,
    header: str = "Test alert",
    start: int = 1000000000,
    end: int | None = None,
) -> AlertEntity:
    payload: dict[str, object] = {
        "id": alert_id,
        "alert": {
            "active_period": [
                {"start": start, "end": end} if end else {"start": start}
            ],
            "informed_entity": [{"agency_id": "MTASBWY", "route_id": route_id}],
            "header_text": {"translation": [{"text": header, "language": "en"}]},
            "transit_realtime.mercury_alert": {"alert_type": alert_type},
        },
    }
    return AlertEntity.model_validate(payload)


@pytest.fixture
async def coordinator(hass: HomeAssistant) -> MTAAlertsCoordinator:
    coord = MTAAlertsCoordinator(hass)
    coord.data = [
        _make_alert("a1", "1", "Delays", "Downtown 1 delayed"),
        _make_alert("a2", "1", "Planned Work", "Weekend track work on 1"),
        _make_alert("a3", "L", "Service Change", "L reroute", end=1000000),
    ]
    coord.last_update_success = True
    return coord


def _category(key: str):
    return next(c for c in CATEGORIES if c.key == key)


async def test_binary_sensor_on_when_matching_alert_active(
    coordinator: MTAAlertsCoordinator,
) -> None:
    sensor = MTAAlertBinarySensor(coordinator, "1", _category("delays"))
    with patch(
        "custom_components.mta_subway.binary_sensor.time.time",
        return_value=2_000_000_000,
    ):
        sensor._refresh()
    assert sensor.is_on is True
    assert sensor.extra_state_attributes is not None
    assert sensor.extra_state_attributes["count"] == 1
    assert "Downtown 1 delayed" in sensor.extra_state_attributes["titles"]


async def test_binary_sensor_off_when_no_matching_category(
    coordinator: MTAAlertsCoordinator,
) -> None:
    sensor = MTAAlertBinarySensor(coordinator, "1", _category("service_change"))
    with patch(
        "custom_components.mta_subway.binary_sensor.time.time",
        return_value=2_000_000_000,
    ):
        sensor._refresh()
    assert sensor.is_on is False
    assert sensor.extra_state_attributes is not None
    assert sensor.extra_state_attributes["count"] == 0


async def test_binary_sensor_filters_by_line(
    coordinator: MTAAlertsCoordinator,
) -> None:
    sensor = MTAAlertBinarySensor(coordinator, "L", _category("planned_work"))
    with patch(
        "custom_components.mta_subway.binary_sensor.time.time",
        return_value=2_000_000_000,
    ):
        sensor._refresh()
    assert sensor.is_on is False  # L has Service Change, not Planned Work


async def test_binary_sensor_excludes_expired_alerts(
    coordinator: MTAAlertsCoordinator,
) -> None:
    sensor = MTAAlertBinarySensor(coordinator, "L", _category("service_change"))
    with patch(
        "custom_components.mta_subway.binary_sensor.time.time",
        return_value=2_000_000_000,
    ):
        sensor._refresh()
    assert sensor.is_on is False  # alert expired (end=1000000)


async def test_binary_sensor_unique_id(
    coordinator: MTAAlertsCoordinator,
) -> None:
    sensor = MTAAlertBinarySensor(coordinator, "1", _category("planned_work"))
    assert sensor.unique_id == "mta_subway_1_planned_work"
