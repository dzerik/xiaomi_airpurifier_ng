"""Base fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.fan import FanEntity, FanEntityFeature

from ..const import (
    ATTR_MODEL,
    DOMAIN,
)
from ..entity import XiaomiMiioEntity

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiMiioBaseFan(XiaomiMiioEntity, FanEntity):
    """Fan state and controls derived from an explicit protocol profile."""

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, coordinator: XiaomiMiioDataUpdateCoordinator) -> None:
        super().__init__(coordinator, unique_id_suffix="fan")
        self._attr_name = None
        self._device_features = self.profile.features
        self._available_attributes = dict(self.profile.attributes)
        self._state_attrs = {ATTR_MODEL: coordinator.model}
        self._preset_modes = list(self.profile.preset_modes)

    @property
    def supported_features(self) -> FanEntityFeature:
        features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if self.profile.preset_modes:
            features |= FanEntityFeature.PRESET_MODE
        if self.profile.speed_range:
            features |= FanEntityFeature.SET_SPEED
        if "set_oscillate" in self.profile.commands:
            features |= FanEntityFeature.OSCILLATE
        return features

    @property
    def preset_modes(self) -> list[str]:
        return self._preset_modes

    @property
    def preset_mode(self) -> str | None:
        mode = (self.coordinator.data or {}).get("mode")
        return mode if mode in self._preset_modes else None

    @property
    def percentage(self) -> int | None:
        from ..device_profiles import read_speed_percentage

        return read_speed_percentage(self.profile, self.coordinator.data or {})

    @property
    def speed_count(self) -> int:
        limits = self.profile.speed_range
        return (limits[1] - limits[0]) // self.profile.speed_step + 1 if limits else 0

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any
    ) -> None:
        """A preset controls its own speed; otherwise apply the requested manual speed."""
        if percentage == 0:
            await self._async_device_off()
        elif preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            await self._async_device_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_device_off()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Validate before powering on, then apply mode in one serialized transaction."""
        from homeassistant.exceptions import ServiceValidationError

        from ..coordinator import DeviceCommand

        if preset_mode not in self._preset_modes or self.profile.mode_enum is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        commands = []
        if not self.is_on:
            commands.append(DeviceCommand("on"))
        commands.append(DeviceCommand("set_mode", (self.profile.mode_enum[preset_mode],)))
        await self.coordinator.async_execute_commands(commands)


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
