"""Smoke tests for the MTA Subway sensor entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from custom_components.mta_subway.coordinator import MTASubwayCoordinator
from custom_components.mta_subway.models import Route
from custom_components.mta_subway.sensor import (
    MTASubwayDirectionSensor,
    MTASubwaySensor,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


ROUTE_PAYLOAD: dict[str, Any] = {
    "id": "1",
    "name": "1",
    "color": "#ee352e",
    "status": "Delays",
    "scheduled": True,
    "direction_statuses": {"north": "Delays", "south": "Good Service"},
    "delay_summaries": {"north": "Trains running 10 mins late", "south": None},
    "service_irregularity_summaries": {"north": None, "south": None},
    "service_change_summaries": {"both": [], "north": [], "south": []},
}


@pytest.fixture
async def coordinator(hass: HomeAssistant) -> MTASubwayCoordinator:
    coord = MTASubwayCoordinator(hass)
    coord.data = {"1": Route.model_validate(ROUTE_PAYLOAD)}
    coord.last_update_success = True
    return coord


async def test_sensor_state(coordinator: MTASubwayCoordinator) -> None:
    sensor = MTASubwaySensor(coordinator, "1")
    assert sensor.native_value == "Delays"


async def test_sensor_unique_id(coordinator: MTASubwayCoordinator) -> None:
    sensor = MTASubwaySensor(coordinator, "1")
    assert sensor.unique_id == "mta_subway_1"


async def test_sensor_attributes_full(coordinator: MTASubwayCoordinator) -> None:
    sensor = MTASubwaySensor(coordinator, "1")
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["color"] == "#ee352e"
    assert attrs["scheduled"] is True
    assert attrs["has_direction_statuses"] is True
    assert attrs["direction_statuses"]["north"] == "Delays"
    assert attrs["has_delay_summaries"] is True
    assert attrs["has_service_change_summaries"] is True


async def test_sensor_attributes_fall_back_when_keys_missing(
    coordinator: MTASubwayCoordinator,
) -> None:
    coordinator.data = {
        "1": Route.model_validate(
            {
                "id": "1",
                "name": "1",
                "color": "#ee352e",
                "status": "Good Service",
                "scheduled": True,
            }
        )
    }
    sensor = MTASubwaySensor(coordinator, "1")
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["has_direction_statuses"] is False
    assert attrs["direction_statuses"] == {"north": None, "south": None}
    assert attrs["has_service_change_summaries"] is False
    assert attrs["service_change_summaries"] == {
        "both": [],
        "north": [],
        "south": [],
    }


async def test_sensor_unavailable_when_route_missing(
    coordinator: MTASubwayCoordinator,
) -> None:
    sensor = MTASubwaySensor(coordinator, "ZZ")
    assert sensor.available is False


async def test_direction_sensor_reports_north_status(
    coordinator: MTASubwayCoordinator,
) -> None:
    sensor = MTASubwayDirectionSensor(coordinator, "1", "north")
    assert sensor.native_value == "Delays"
    assert sensor.unique_id == "mta_subway_1_north"


async def test_direction_sensor_reports_south_status(
    coordinator: MTASubwayCoordinator,
) -> None:
    sensor = MTASubwayDirectionSensor(coordinator, "1", "south")
    assert sensor.native_value == "Good Service"


async def test_direction_sensor_unavailable_when_no_direction_data(
    coordinator: MTASubwayCoordinator,
) -> None:
    coordinator.data = {
        "1": Route.model_validate(
            {
                "id": "1",
                "name": "1",
                "color": "#ee352e",
                "status": "Good Service",
                "scheduled": True,
            }
        )
    }
    sensor = MTASubwayDirectionSensor(coordinator, "1", "north")
    assert sensor.available is False
    assert sensor.native_value is None
