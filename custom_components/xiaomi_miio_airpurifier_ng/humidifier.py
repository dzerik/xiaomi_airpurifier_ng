"""Support for Xiaomi Air Humidifier as humidifier platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DeviceCategory,
    classify_model,
)
from .entity import XiaomiMiioEntity

if TYPE_CHECKING:
    from .coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

MIN_HUMIDITY = 30
MAX_HUMIDITY = 80

# Pre-compute mode lists from enums (replaces inline list comprehensions)

# Default config for unknown humidifier models

# Model → config lookup (replaces if/elif chain)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio humidifier from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    model = coordinator.model
    category = classify_model(model)

    if category == DeviceCategory.HUMIDIFIER:
        async_add_entities([XiaomiAirHumidifier(coordinator)])


class XiaomiAirHumidifier(XiaomiMiioEntity, HumidifierEntity):
    """Humidifier controls constrained by the selected device profile."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_supported_features = HumidifierEntityFeature.MODES

    def __init__(self, coordinator: XiaomiMiioDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._device_features = self.profile.features
        self._available_attributes = dict(self.profile.attributes)
        self._attr_name = None
        self._attr_available_modes = [name.lower() for name in self.profile.preset_modes]
        if self.profile.humidity:
            self._attr_min_humidity = self.profile.humidity.minimum
            self._attr_max_humidity = self.profile.humidity.maximum

    @property
    def target_humidity(self) -> int | None:
        return (
            (self.coordinator.data or {}).get("target_humidity") if self.profile.humidity else None
        )

    @property
    def current_humidity(self) -> int | None:
        return (self.coordinator.data or {}).get("humidity")

    @property
    def mode(self) -> str | None:
        mode = (self.coordinator.data or {}).get("mode")
        return mode.lower() if isinstance(mode, str) and mode else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_device_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_device_off()

    async def async_set_humidity(self, humidity: int) -> None:
        await self.coordinator.async_set_humidity(humidity)

    async def async_set_mode(self, mode: str) -> None:
        from homeassistant.exceptions import ServiceValidationError

        selected = next(
            (
                item
                for item in self.profile.mode_enum
                if item.name.lower() == mode.lower() and item.name in self.profile.preset_modes
            ),
            None,
        )
        if selected is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        await self._async_command("set_mode", selected)
