"""Sensor platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XiaomiMiioDataUpdateCoordinator
from .entity import XiaomiMiioEntity


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioSensorEntityDescription(SensorEntityDescription):
    """Describes Xiaomi Miio sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    exists_fn: Callable[[dict[str, Any]], bool] | None = None


# Sensor descriptions for different device types
SENSOR_DESCRIPTIONS: tuple[XiaomiMiioSensorEntityDescription, ...] = (
    # Air Quality
    XiaomiMiioSensorEntityDescription(
        key="aqi",
        translation_key="aqi",
        name="Air Quality Index",
        native_unit_of_measurement="AQI",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda data: data.get("aqi"),
        exists_fn=lambda data: "aqi" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="pm25",
        translation_key="pm25",
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pm25"),
        exists_fn=lambda data: "pm25" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="average_aqi",
        translation_key="average_aqi",
        name="Average AQI",
        native_unit_of_measurement="AQI",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda data: data.get("average_aqi"),
        exists_fn=lambda data: "average_aqi" in data,
    ),
    # Temperature & Humidity
    XiaomiMiioSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("temperature"),
        exists_fn=lambda data: "temperature" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("humidity"),
        exists_fn=lambda data: "humidity" in data,
    ),
    # CO2
    XiaomiMiioSensorEntityDescription(
        key="co2",
        translation_key="co2",
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement="ppm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2"),
        exists_fn=lambda data: "co2" in data,
    ),
    # Filter
    XiaomiMiioSensorEntityDescription(
        key="filter_life_remaining",
        translation_key="filter_life_remaining",
        name="Filter Life Remaining",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("filter_life_remaining"),
        exists_fn=lambda data: "filter_life_remaining" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="filter_hours_used",
        translation_key="filter_hours_used",
        name="Filter Hours Used",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("filter_hours_used"),
        exists_fn=lambda data: "filter_hours_used" in data,
    ),
    # Motor
    XiaomiMiioSensorEntityDescription(
        key="motor_speed",
        translation_key="motor_speed",
        name="Motor Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("motor_speed"),
        exists_fn=lambda data: "motor_speed" in data,
    ),
    # Usage stats
    XiaomiMiioSensorEntityDescription(
        key="use_time",
        translation_key="use_time",
        name="Use Time",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("use_time"),
        exists_fn=lambda data: "use_time" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="purify_volume",
        translation_key="purify_volume",
        name="Purify Volume",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-purifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("purify_volume"),
        exists_fn=lambda data: "purify_volume" in data,
    ),
    # Humidifier specific
    XiaomiMiioSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        name="Water Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water",
        value_fn=lambda data: data.get("water_level"),
        exists_fn=lambda data: "water_level" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="target_humidity",
        translation_key="target_humidity",
        name="Target Humidity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        value_fn=lambda data: data.get("target_humidity"),
        exists_fn=lambda data: "target_humidity" in data,
    ),
    # Fan specific
    XiaomiMiioSensorEntityDescription(
        key="battery",
        translation_key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery"),
        exists_fn=lambda data: "battery" in data,
    ),
    # Mode (as diagnostic)
    XiaomiMiioSensorEntityDescription(
        key="mode",
        translation_key="mode",
        name="Mode",
        icon="mdi:information-outline",
        value_fn=lambda data: data.get("mode"),
        exists_fn=lambda data: "mode" in data,
    ),
    # Air Purifier additional sensors
    XiaomiMiioSensorEntityDescription(
        key="illuminance",
        translation_key="illuminance",
        name="Illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement="lx",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("illuminance"),
        exists_fn=lambda data: "illuminance" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="tvoc",
        translation_key="tvoc",
        name="TVOC",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:molecule",
        value_fn=lambda data: data.get("tvoc"),
        exists_fn=lambda data: "tvoc" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="pm10",
        translation_key="pm10",
        name="PM10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pm10"),
        exists_fn=lambda data: "pm10" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="motor2_speed",
        translation_key="motor2_speed",
        name="Motor 2 Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("motor2_speed"),
        exists_fn=lambda data: "motor2_speed" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="filter_left_time",
        translation_key="filter_left_time",
        name="Filter Days Left",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("filter_left_time"),
        exists_fn=lambda data: "filter_left_time" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="filter_type",
        translation_key="filter_type",
        name="Filter Type",
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("filter_type"),
        exists_fn=lambda data: "filter_type" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="volume",
        translation_key="volume",
        name="Volume",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:volume-high",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("volume") or data.get("buzzer_volume"),
        exists_fn=lambda data: "volume" in data or "buzzer_volume" in data,
    ),
    # Air Fresh additional sensors
    XiaomiMiioSensorEntityDescription(
        key="temperature_outside",
        translation_key="temperature_outside",
        name="Outside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("temperature_outside"),
        exists_fn=lambda data: "temperature_outside" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="dust_filter_life_remaining",
        translation_key="dust_filter_life_remaining",
        name="Dust Filter Life",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("dust_filter_life_remaining"),
        exists_fn=lambda data: "dust_filter_life_remaining" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="dust_filter_life_remaining_days",
        translation_key="dust_filter_life_remaining_days",
        name="Dust Filter Days Left",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("dust_filter_life_remaining_days"),
        exists_fn=lambda data: "dust_filter_life_remaining_days" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="upper_filter_life_remaining",
        translation_key="upper_filter_life_remaining",
        name="Upper Filter Life",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("upper_filter_life_remaining"),
        exists_fn=lambda data: "upper_filter_life_remaining" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="upper_filter_life_remaining_days",
        translation_key="upper_filter_life_remaining_days",
        name="Upper Filter Days Left",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("upper_filter_life_remaining_days"),
        exists_fn=lambda data: "upper_filter_life_remaining_days" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="favorite_speed",
        translation_key="favorite_speed",
        name="Favorite Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("favorite_speed"),
        exists_fn=lambda data: "favorite_speed" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="control_speed",
        translation_key="control_speed",
        name="Control Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("control_speed"),
        exists_fn=lambda data: "control_speed" in data,
    ),
    # Fan additional sensors
    XiaomiMiioSensorEntityDescription(
        key="speed",
        translation_key="speed",
        name="Speed",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("speed"),
        exists_fn=lambda data: "speed" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="natural_speed",
        translation_key="natural_speed",
        name="Natural Speed",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda data: data.get("natural_speed"),
        exists_fn=lambda data: "natural_speed" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="direct_speed",
        translation_key="direct_speed",
        name="Direct Speed",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        value_fn=lambda data: data.get("direct_speed"),
        exists_fn=lambda data: "direct_speed" in data,
    ),
    XiaomiMiioSensorEntityDescription(
        key="angle",
        translation_key="angle",
        name="Oscillation Angle",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:rotate-3d-variant",
        value_fn=lambda data: data.get("angle"),
        exists_fn=lambda data: "angle" in data,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio sensors from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    entities: list[XiaomiMiioSensor] = []

    # Create sensors based on available data
    for description in SENSOR_DESCRIPTIONS:
        if description.exists_fn and coordinator.data:
            if description.exists_fn(coordinator.data):
                entities.append(XiaomiMiioSensor(coordinator, description))

    async_add_entities(entities)


class XiaomiMiioSensor(XiaomiMiioEntity, SensorEntity):
    """Representation of a Xiaomi Miio sensor."""

    entity_description: XiaomiMiioSensorEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
