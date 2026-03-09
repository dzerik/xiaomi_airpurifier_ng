"""Base fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.fan import FanEntity, FanEntityFeature

from ..const import (
    ATTR_MODEL,
    FEATURE_SET_CHILD_LOCK,
)
from ..entity import XiaomiMiioEntity

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiMiioBaseFan(XiaomiMiioEntity, FanEntity):
    """Base class for coordinator-based Xiaomi fan entities."""

    _enable_turn_on_off_backwards_compatibility = False

    # Subclasses should override these
    _device_features: int = FEATURE_SET_CHILD_LOCK

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator, unique_id_suffix="fan")
        self._attr_name = None  # Use device name

        # Initialize state attributes with model
        self._state_attrs: dict[str, Any] = {ATTR_MODEL: coordinator.model}
        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def supported_features(self) -> FanEntityFeature:
        """Return supported features."""
        features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if self.coordinator.data:
            if "mode" in self.coordinator.data:
                features |= FanEntityFeature.PRESET_MODE
            if "speed" in self.coordinator.data or "fan_level" in self.coordinator.data:
                features |= FanEntityFeature.SET_SPEED
        return features

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        """Turn the device on."""
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        else:
            await self._async_device_on()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        await self._async_device_off()


class XiaomiGenericFan(XiaomiMiioBaseFan):
    """Coordinator-based generic fan entity for unknown models."""

    @property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return None
