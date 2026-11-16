"""Number platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XiaomiMiioDataUpdateCoordinator
from .device_profiles import get_device_profile
from .entity import XiaomiMiioEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioNumberEntityDescription(NumberEntityDescription):
    """Describes Xiaomi Miio number entity."""

    value_fn: Callable[[dict[str, Any]], float | None] | None = None
    exists_fn: Callable[[dict[str, Any]], bool] | None = None
    set_fn: str | None = None  # Method name to call on device


# Number descriptions
NUMBER_DESCRIPTIONS: tuple[XiaomiMiioNumberEntityDescription, ...] = (
    XiaomiMiioNumberEntityDescription(
        key="favorite_level",
        translation_key="favorite_level",
        name="Favorite Level",
        icon="mdi:heart",
        native_min_value=0,
        native_max_value=16,
        native_step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("favorite_level"),
        exists_fn=lambda data: "favorite_level" in data,
        set_fn="set_favorite_level",
    ),
    XiaomiMiioNumberEntityDescription(
        key="fan_level",
        translation_key="fan_level",
        name="Fan Level",
        icon="mdi:fan",
        native_min_value=1,
        native_max_value=3,
        native_step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("fan_level"),
        exists_fn=lambda data: "fan_level" in data,
        set_fn="set_fan_level",
    ),
    XiaomiMiioNumberEntityDescription(
        key="volume",
        translation_key="volume",
        name="Volume",
        icon="mdi:volume-medium",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("volume"),
        exists_fn=lambda data: "volume" in data,
        set_fn="set_volume",
    ),
    XiaomiMiioNumberEntityDescription(
        key="target_humidity",
        translation_key="target_humidity",
        name="Target Humidity",
        icon="mdi:water-percent",
        device_class=NumberDeviceClass.HUMIDITY,
        native_min_value=30,
        native_max_value=80,
        native_step=10,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("target_humidity"),
        exists_fn=lambda data: "target_humidity" in data,
        set_fn="set_target_humidity",
    ),
    XiaomiMiioNumberEntityDescription(
        key="angle",
        translation_key="angle",
        name="Oscillation Angle",
        icon="mdi:angle-acute",
        native_min_value=30,
        native_max_value=120,
        native_step=30,
        native_unit_of_measurement="°",
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("angle"),
        exists_fn=lambda data: "angle" in data,
        set_fn="set_angle",
    ),
    XiaomiMiioNumberEntityDescription(
        key="delay_off_countdown",
        translation_key="delay_off_countdown",
        name="Delay Off",
        icon="mdi:timer-off",
        native_min_value=0,
        native_max_value=480,
        native_step=1,
        native_unit_of_measurement="min",
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("delay_off_countdown"),
        exists_fn=lambda data: "delay_off_countdown" in data,
        set_fn="delay_off",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio number entities from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    known_keys: set[str] = set()

    @callback
    def _async_discover_numbers() -> None:
        """Discover number entities based on coordinator data."""
        new_entities: list[XiaomiMiioNumber] = []
        for description in NUMBER_DESCRIPTIONS:
            if description.key in known_keys:
                continue
            if description.exists_fn and coordinator.data:
                if (
                    description.exists_fn(coordinator.data)
                    and description.set_fn in get_device_profile(coordinator.model).commands
                ):
                    known_keys.add(description.key)
                    new_entities.append(XiaomiMiioNumber(coordinator, description))
        if new_entities:
            async_add_entities(new_entities)

    _async_discover_numbers()
    entry.async_on_unload(coordinator.async_add_listener(_async_discover_numbers))


class XiaomiMiioNumber(XiaomiMiioEntity, NumberEntity):
    """Representation of a Xiaomi Miio number entity."""

    entity_description: XiaomiMiioNumberEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description
        if description.key == "target_humidity" and self.profile.humidity:
            self._attr_native_min_value = self.profile.humidity.minimum
            self._attr_native_max_value = self.profile.humidity.maximum
            self._attr_native_step = self.profile.humidity.step
        elif description.key == "favorite_level":
            self._attr_native_max_value = (
                14 if self.profile.driver.__name__ == "AirPurifierMiot" else 17
            )
        if description.key == "delay_off_countdown":
            self._attr_native_max_value = self.profile.delay_max_minutes

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and self.entity_description.value_fn:
            value = self.entity_description.value_fn(self.coordinator.data)
            if value is not None:
                return (
                    float(value) / 60
                    if self.entity_description.key == "delay_off_countdown"
                    and self.profile.delay_unit_seconds
                    else float(value)
                )
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Validate model limits before selecting a shared device operation."""
        from homeassistant.exceptions import ServiceValidationError

        if not self.native_min_value <= value <= self.native_max_value or value != int(value):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        if self.entity_description.key == "target_humidity":
            await self.coordinator.async_set_humidity(int(value))
        else:
            if (value - self.native_min_value) % (self.native_step or 1):
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="invalid_value"
                )
            encoded = (
                int(value) * 60
                if self.entity_description.key == "delay_off_countdown"
                and self.profile.delay_unit_seconds
                else int(value)
            )
            await self._async_command(self.entity_description.set_fn or "", encoded)
