"""Data update coordinator."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_STATION_ID,
    DASHBOARD_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    USER_AGENT,
)
from .parser import parse_dashboard

_LOGGER = logging.getLogger(__name__)


async def async_fetch_station(hass: HomeAssistant, station_id: str) -> dict[str, Any]:
    """Download and parse one station dashboard."""
    session = async_get_clientsession(hass)
    url = DASHBOARD_URL.format(station_id=station_id)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en"}
    try:
        async with session.get(
            url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            if resp.status == 404:
                raise ValueError(f"Station {station_id} not found")
            resp.raise_for_status()
            html = await resp.text()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise ConnectionError(str(err)) from err
    return parse_dashboard(html)


class WundergroundCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the dashboard page at the configured interval."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        minutes = entry.options.get(
            CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_STATION_ID]}",
            update_interval=timedelta(minutes=minutes),
        )
        self.station_id: str = entry.data[CONF_STATION_ID]

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await async_fetch_station(self.hass, self.station_id)
        except (ConnectionError, ValueError) as err:
            raise UpdateFailed(f"{self.station_id}: {err}") from err
