"""Tests for the MTA Subway config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mta_subway.const import CONF_LINE, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with (
        patch("custom_components.mta_subway.async_setup", return_value=True),
        patch(
            "custom_components.mta_subway.async_setup_entry", return_value=True
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_LINE: ["1", "L"]}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "MTA Subway"
    assert result["data"] == {CONF_LINE: ["1", "L"]}
    assert len(mock_setup_entry.mock_calls) == 1


async def test_already_configured_aborts(hass: HomeAssistant) -> None:
    MockConfigEntry(
        domain=DOMAIN, data={CONF_LINE: ["1"]}, unique_id=DOMAIN
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_yaml_import_creates_entry(hass: HomeAssistant) -> None:
    with (
        patch("custom_components.mta_subway.async_setup", return_value=True),
        patch(
            "custom_components.mta_subway.async_setup_entry", return_value=True
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={CONF_LINE: ["A", "C", "E"]},
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_LINE: ["A", "C", "E"]}
    assert len(mock_setup_entry.mock_calls) == 1


async def test_options_flow_updates_lines(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_LINE: ["1"]}, unique_id=DOMAIN)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_LINE: ["1", "2", "3"]}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_LINE] == ["1", "2", "3"]
