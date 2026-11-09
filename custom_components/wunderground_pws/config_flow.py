"""Config flow: paste a dashboard URL (or station ID) and pick an interval."""
from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_STATION_ID,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .coordinator import async_fetch_station

_URL_RE = re.compile(r"/pws/([A-Za-z0-9_-]+)")
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{3,}$")


def extract_station_id(text: str) -> str | None:
    text = text.strip()
    if m := _URL_RE.search(text):
        return m.group(1).upper()
    if _ID_RE.match(text):
        return text.upper()
    return None


def _interval_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=MIN_SCAN_INTERVAL,
            max=MAX_SCAN_INTERVAL,
            step=1,
            unit_of_measurement="min",
            mode=NumberSelectorMode.BOX,
        )
    )


class WundergroundConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            station_id = extract_station_id(user_input[CONF_URL])
            if station_id is None:
                errors[CONF_URL] = "invalid_url"
            else:
                await self.async_set_unique_id(station_id)
                self._abort_if_unique_id_configured()
                try:
                    await async_fetch_station(self.hass, station_id)
                except ConnectionError:
                    errors["base"] = "cannot_connect"
                except ValueError:
                    errors["base"] = "no_data"
                else:
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME) or station_id,
                        data={
                            CONF_STATION_ID: station_id,
                            CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL): str,
                vol.Optional(CONF_NAME): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): _interval_selector(),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WundergroundOptionsFlow()


class WundergroundOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL])}
            )
        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_SCAN_INTERVAL, default=current): _interval_selector()}
            ),
        )
