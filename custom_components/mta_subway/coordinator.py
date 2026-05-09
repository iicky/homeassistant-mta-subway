"""Data update coordinator for the MTA Subway integration."""

from __future__ import annotations

import logging

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pydantic import ValidationError

from .const import API_URL, DOMAIN, UPDATE_INTERVAL
from .models import Route, SubwayResponse

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)


class MTASubwayCoordinator(DataUpdateCoordinator[dict[str, Route]]):
    """Polls subwaynow.app once and shares parsed routes with all line sensors."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Route]:
        try:
            async with self._session.get(API_URL, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                payload = await response.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error fetching MTA subway data: {err}") from err

        try:
            parsed = SubwayResponse.model_validate(payload)
        except ValidationError as err:
            raise UpdateFailed(f"Invalid response from MTA subway API: {err}") from err

        if not parsed.routes:
            raise UpdateFailed("Response contained no routes")
        return parsed.routes
