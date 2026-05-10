"""Config flow for the MTA Subway integration."""

from __future__ import annotations

from typing import Any, cast

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,  # pyright: ignore[reportUnknownVariableType]
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_LINE, DOMAIN, SUBWAY_LINES


def _line_selector() -> Any:
    return cast(
        "Any",
        SelectSelector(
            SelectSelectorConfig(
                options=SUBWAY_LINES,
                multiple=True,
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    )


class MTASubwayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the MTA Subway config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required(CONF_LINE): _line_selector()}),
            )
        return self.async_create_entry(title="MTA Subway", data=user_input)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        return self.async_create_entry(title="MTA Subway", data=import_data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MTASubwayOptionsFlow()


class MTASubwayOptionsFlow(OptionsFlow):
    """Options flow for changing the tracked lines after install."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_lines = self.config_entry.options.get(
            CONF_LINE, self.config_entry.data.get(CONF_LINE, [])
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_LINE, default=current_lines): _line_selector()}
            ),
        )
