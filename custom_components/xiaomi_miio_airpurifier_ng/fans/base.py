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
from ..service_mixin import DeviceServiceMixin

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiMiioBaseFan(DeviceServiceMixin, XiaomiMiioEntity, FanEntity):
    """Base class for coordinator-based Xiaomi fan entities.

    Core fan logic (on/off, features, attributes). Service handler methods
    are inherited from DeviceServiceMixin.
    """

    _enable_turn_on_off_backwards_compatibility = False

    # Subclasses should override these
    _device_features: int = FEATURE_SET_CHILD_LOCK
    _available_attributes: dict[str, str] = {}

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator, unique_id_suffix="fan")
        self._attr_name = None  # Use device name

        # Initialize state attributes with model
        self._state_attrs: dict[str, Any] = {ATTR_MODEL: coordinator.model}

        # Initialize available attribute values to None
        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes of the device."""
        # Update state attributes from coordinator data
        if self.coordinator.data:
            for key, attr_name in self._available_attributes.items():
                value = self.coordinator.data.get(attr_name)
                if value is not None:
                    self._state_attrs[key] = self._extract_value_from_attribute(value)
        return self._state_attrs

    @property
    def is_on(self) -> bool | None:
        """Return true if the device is on.

        python-miio returns power as string "on"/"off" for all models.
        Using bool(power) would be incorrect since bool("off") == True.
        """
        if self.coordinator.data:
            power = self.coordinator.data.get("power")
            if power is not None:
                if isinstance(power, str):
                    return power == "on"
                return bool(power)
            is_on = self.coordinator.data.get("is_on")
            if is_on is not None:
                return bool(is_on)
        return None

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
            # If operation mode was set the device must not be turned on.
            await self.async_set_preset_mode(preset_mode)
        else:
            await self._try_command(
                "Turning the miio device on failed: %s",
                self.coordinator.device.on,
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        await self._try_command(
            "Turning the miio device off failed: %s",
            self.coordinator.device.off,
        )
        await self.coordinator.async_request_refresh()


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
