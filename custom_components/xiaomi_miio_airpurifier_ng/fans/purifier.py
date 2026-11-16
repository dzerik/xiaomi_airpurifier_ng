"""Air Purifier fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..const import DOMAIN
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)

# Speed conversion constants
MIOT_SPEED_LEVELS = 3  # fan_level 1-3
MIOT_PERCENT_PER_LEVEL = 100 / MIOT_SPEED_LEVELS  # ~33.33%
LEGACY_SPEED_LEVELS = 16  # favorite_level 0-16
LEGACY_PERCENT_PER_LEVEL = 100 / LEGACY_SPEED_LEVELS  # 6.25%

# Pre-compute airdog modes from enum

# Default config for unknown purifier models

# MIOT config shared by 13 models

# Model → config lookup (replaces if/elif chain)


class XiaomiAirPurifierFan(XiaomiMiioBaseFan):
    """Purifier controls using the model's supported manual-speed protocol."""

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
        if self.profile.speed_kind is SpeedKind.AIRDOG:
            commands.append(
                DeviceCommand("set_mode_and_speed", (self.profile.mode_enum.Manual, value))
            )
        else:
            command = (
                "set_fan_level"
                if "set_fan_level" in self.profile.commands
                else "set_favorite_rpm"
                if "set_favorite_rpm" in self.profile.commands
                else "set_favorite_level"
            )
            mode_name = "Fan" if command == "set_fan_level" else "Favorite"
            if (self.coordinator.data or {}).get("mode") != mode_name:
                commands.append(DeviceCommand("set_mode", (self.profile.mode_enum[mode_name],)))
            commands.append(DeviceCommand(command, (value,)))
        await self.coordinator.async_execute_commands(commands)
