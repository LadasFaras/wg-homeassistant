"""Sensors for the Wunderground PWS integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfIrradiance,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DASHBOARD_URL, DOMAIN
from .coordinator import WundergroundCoordinator

# Unit codes used on the dashboard: m = metric, e = imperial, h = UK hybrid.
_T = {"m": UnitOfTemperature.CELSIUS, "e": UnitOfTemperature.FAHRENHEIT, "h": UnitOfTemperature.CELSIUS}
_WIND = {"m": UnitOfSpeed.KILOMETERS_PER_HOUR, "e": UnitOfSpeed.MILES_PER_HOUR, "h": UnitOfSpeed.MILES_PER_HOUR}
_PRESS = {"m": UnitOfPressure.HPA, "e": UnitOfPressure.INHG, "h": UnitOfPressure.HPA}
_RAIN = {"m": UnitOfPrecipitationDepth.MILLIMETERS, "e": UnitOfPrecipitationDepth.INCHES, "h": UnitOfPrecipitationDepth.MILLIMETERS}
_RATE = {"m": UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR, "e": UnitOfVolumetricFlux.INCHES_PER_HOUR, "h": UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR}


@dataclass(frozen=True, kw_only=True)
class WuSensorDescription(SensorEntityDescription):
    units: dict[str, str] | None = None  # unit code -> native unit


SENSORS: tuple[WuSensorDescription, ...] = (
    WuSensorDescription(key="temperature", translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, units=_T),
    WuSensorDescription(key="feels_like", translation_key="feels_like",
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, units=_T),
    WuSensorDescription(key="dew_point", translation_key="dew_point",
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, units=_T),
    WuSensorDescription(key="humidity", translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY, state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE),
    WuSensorDescription(key="wind_speed", translation_key="wind_speed",
        device_class=SensorDeviceClass.WIND_SPEED, state_class=SensorStateClass.MEASUREMENT, units=_WIND),
    WuSensorDescription(key="wind_gust", translation_key="wind_gust",
        device_class=SensorDeviceClass.WIND_SPEED, state_class=SensorStateClass.MEASUREMENT, units=_WIND),
    WuSensorDescription(key="wind_direction", translation_key="wind_direction",
        state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=DEGREE, icon="mdi:compass"),
    WuSensorDescription(key="pressure", translation_key="pressure",
        device_class=SensorDeviceClass.PRESSURE, state_class=SensorStateClass.MEASUREMENT, units=_PRESS),
    WuSensorDescription(key="precip_rate", translation_key="precip_rate",
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY, state_class=SensorStateClass.MEASUREMENT, units=_RATE),
    WuSensorDescription(key="precip_total", translation_key="precip_total",
        device_class=SensorDeviceClass.PRECIPITATION, state_class=SensorStateClass.TOTAL_INCREASING, units=_RAIN),
    WuSensorDescription(key="uv_index", translation_key="uv_index",
        state_class=SensorStateClass.MEASUREMENT, icon="mdi:sun-wireless"),
    WuSensorDescription(key="solar_radiation", translation_key="solar_radiation",
        device_class=SensorDeviceClass.IRRADIANCE, state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: WundergroundCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(WundergroundSensor(coordinator, entry, d) for d in SENSORS)


class WundergroundSensor(CoordinatorEntity[WundergroundCoordinator], SensorEntity):
    _attr_has_entity_name = True
    entity_description: WuSensorDescription

    def __init__(self, coordinator: WundergroundCoordinator, entry: ConfigEntry,
                 description: WuSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        sid = coordinator.station_id
        self._attr_unique_id = f"{sid}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, sid)},
            name=entry.title,
            manufacturer="Weather Underground",
            model="Personal Weather Station",
            configuration_url=DASHBOARD_URL.format(station_id=sid),
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("values", {}).get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self):
        units = self.entity_description.units
        if units is None:
            return self.entity_description.native_unit_of_measurement
        code = (self.coordinator.data or {}).get("unit", "m")
        return units.get(code, units["m"])

    @property
    def extra_state_attributes(self):
        status = (self.coordinator.data or {}).get("status")
        return {"station_id": self.coordinator.station_id, "station_status": status}
