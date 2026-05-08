"""Data update coordinator for the MTA Subway integration."""

from __future__ import annotations

import logging
from typing import Any, cast

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)


class MTASubwayCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls subwaynow.app once and shares the result with all line sensors."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self._session.get(API_URL, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                payload: Any = await response.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error fetching MTA subway data: {err}") from err

        if not isinstance(payload, dict):
            raise UpdateFailed("Response is not a JSON object")
        routes = cast("Any", payload).get("routes")
        if not isinstance(routes, dict) or not routes:
            raise UpdateFailed("Response missing 'routes' object")
        return cast("dict[str, Any]", routes)
