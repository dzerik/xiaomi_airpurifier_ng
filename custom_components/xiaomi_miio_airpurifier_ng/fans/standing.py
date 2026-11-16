"""Standing fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..const import DOMAIN
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)

# Pre-compute mode lists

# P5-style models list (shared between config and protocol flag)

# Default config for unknown/legacy fan models


# Model → config lookup (replaces if/elif chain)


class XiaomiStandingFan(XiaomiMiioBaseFan):
    """Standing fan speeds and real automatic presets."""

    @property
    def _is_natural_mode(self) -> bool:
        data = self.coordinator.data or {}
        return data.get("mode") in ("Nature", "Natural") or bool(data.get("natural_speed"))

    @property
    def preset_mode(self) -> str | None:
        from ..device_profiles import SpeedKind

        if self.profile.speed_kind is SpeedKind.LEGACY:
            return "Nature" if self._is_natural_mode else None
        return super().preset_mode

    @property
    def oscillating(self) -> bool | None:
        return (self.coordinator.data or {}).get("oscillate")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        from homeassistant.exceptions import ServiceValidationError

        from ..coordinator import DeviceCommand
        from ..device_profiles import SpeedKind

        if preset_mode not in self.profile.preset_modes:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        commands = []
        if not self.is_on:
            commands.append(DeviceCommand("on"))
        if self.profile.speed_kind is SpeedKind.LEGACY:
            speed = (self.coordinator.data or {}).get("direct_speed") or 50
            commands.append(DeviceCommand("set_natural_speed", (speed,)))
        else:
            commands.append(DeviceCommand("set_mode", (self.profile.mode_enum[preset_mode],)))
        await self.coordinator.async_execute_commands(commands)

    async def async_oscillate(self, oscillating: bool) -> None:
        await self._async_command("set_oscillate", oscillating)

    async def async_set_percentage(self, percentage: int) -> None:
        from homeassistant.exceptions import ServiceValidationError

        from ..coordinator import DeviceCommand
        from ..device_profiles import SpeedKind, speed_value_for_percentage

        if percentage == 0:
            await self._async_device_off()
            return
        try:
            value = speed_value_for_percentage(self.profile, percentage)
        except ValueError as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_value"
            ) from exc
        commands = []
        if not self.is_on:
            commands.append(DeviceCommand("on"))
        if self.profile.speed_kind is SpeedKind.LEGACY:
            commands.append(DeviceCommand("set_direct_speed", (value,)))
        else:
            mode = self.profile.mode_enum.__members__.get(
                "Normal"
            ) or self.profile.mode_enum.__members__.get("Manual")
            if mode is not None and (self.coordinator.data or {}).get("mode") != mode.name:
                commands.append(DeviceCommand("set_mode", (mode,)))
            commands.append(DeviceCommand("set_speed", (value,)))
        await self.coordinator.async_execute_commands(commands)

    async def async_set_direction(self, direction: str) -> None:
        from homeassistant.exceptions import ServiceValidationError

        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
