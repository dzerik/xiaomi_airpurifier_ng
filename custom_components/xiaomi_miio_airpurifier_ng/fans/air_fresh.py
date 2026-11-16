"""Air Fresh fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..const import DOMAIN
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)

# Default config for unknown air fresh models

# Model → config lookup (replaces if/elif chain)


class XiaomiAirFreshFan(XiaomiMiioBaseFan):
    """Ventilator presets and model-specific favorite speed."""

    async def async_set_percentage(self, percentage: int) -> None:
        from homeassistant.exceptions import ServiceValidationError

        from ..coordinator import DeviceCommand
        from ..device_profiles import speed_value_for_percentage

        if percentage == 0:
            await self._async_device_off()
            return
        try:
            speed = speed_value_for_percentage(self.profile, percentage)
        except ValueError as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_value"
            ) from exc
        commands = []
        if not self.is_on:
            commands.append(DeviceCommand("on"))
        if self.profile.speed_modes:
            commands.append(
                DeviceCommand(
                    "set_mode", (self.profile.mode_enum[self.profile.speed_modes[speed - 1]],)
                )
            )
        else:
            commands.extend(
                (
                    DeviceCommand("set_mode", (self.profile.mode_enum.Favorite,)),
                    DeviceCommand("set_favorite_speed", (speed,)),
                )
            )
        await self.coordinator.async_execute_commands(commands)
