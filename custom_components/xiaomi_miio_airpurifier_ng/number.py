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

from .coordinator import XiaomiMiioDataUpdateCoordinator
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
                if description.exists_fn(coordinator.data):
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

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and self.entity_description.value_fn:
            value = self.entity_description.value_fn(self.coordinator.data)
            if value is not None:
                return float(value)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        device = self.coordinator.device
        method_name = self.entity_description.set_fn

        if not method_name:
            _LOGGER.warning(
                "No method defined for setting %s",
                self.entity_description.key,
            )
            return

        try:
            method = getattr(device, method_name, None)
            if method:
                # Always convert to int (Xiaomi devices expect int values)
                set_value = int(value)
                await self.hass.async_add_executor_job(method, set_value)
                await self.coordinator.async_request_refresh()
                _LOGGER.debug(
                    "Successfully set %s to %s",
                    self.entity_description.key,
                    set_value,
                )
            else:
                _LOGGER.error(
                    "Method %s not found on device for %s",
                    method_name,
                    self.entity_description.key,
                )
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error(
                "Failed to set %s to %s: %s",
                self.entity_description.key,
                value,
                ex,
            )
