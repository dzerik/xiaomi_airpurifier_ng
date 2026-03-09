"""Air Purifier fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from miio.integrations.airpurifier.airdog.airpurifier_airdog import (
    OperationMode as AirDogOperationMode,
)
from miio.integrations.airpurifier.zhimi.airpurifier import (
    LedBrightness as AirpurifierLedBrightness,
)
from miio.integrations.airpurifier.zhimi.airpurifier import (
    OperationMode as AirpurifierOperationMode,
)
from miio.integrations.airpurifier.zhimi.airpurifier_miot import (
    LedBrightness as AirpurifierMiotLedBrightness,
)
from miio.integrations.airpurifier.zhimi.airpurifier_miot import (
    OperationMode as AirpurifierMiotOperationMode,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_AIRPURIFIER,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_3,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X5,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X7SM,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7,
    AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3,
    FEATURE_FLAGS_AIRPURIFIER,
    FEATURE_FLAGS_AIRPURIFIER_2H,
    FEATURE_FLAGS_AIRPURIFIER_2S,
    FEATURE_FLAGS_AIRPURIFIER_3,
    FEATURE_FLAGS_AIRPURIFIER_AIRDOG,
    FEATURE_FLAGS_AIRPURIFIER_PRO,
    FEATURE_FLAGS_AIRPURIFIER_PRO_V7,
    FEATURE_FLAGS_AIRPURIFIER_V3,
    MODEL_AIRPURIFIER_2H,
    MODEL_AIRPURIFIER_2S,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_AIRDOG_X5,
    MODEL_AIRPURIFIER_AIRDOG_X7SM,
    MODEL_AIRPURIFIER_PRO,
    MODEL_AIRPURIFIER_PRO_V7,
    MODEL_AIRPURIFIER_V3,
    OPERATION_MODES_AIRPURIFIER,
    OPERATION_MODES_AIRPURIFIER_2H,
    OPERATION_MODES_AIRPURIFIER_2S,
    OPERATION_MODES_AIRPURIFIER_3,
    OPERATION_MODES_AIRPURIFIER_PRO,
    OPERATION_MODES_AIRPURIFIER_PRO_V7,
    OPERATION_MODES_AIRPURIFIER_V3,
    PURIFIER_MIOT,
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Speed conversion constants
MIOT_SPEED_LEVELS = 3  # fan_level 1-3
MIOT_PERCENT_PER_LEVEL = 100 / MIOT_SPEED_LEVELS  # ~33.33%
LEGACY_SPEED_LEVELS = 16  # favorite_level 0-16
LEGACY_PERCENT_PER_LEVEL = 100 / LEGACY_SPEED_LEVELS  # 6.25%


class XiaomiAirPurifierFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Air Purifiers."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the air purifier fan entity."""
        model = coordinator.model

        # Set device features and available attributes based on model
        if model == MODEL_AIRPURIFIER_PRO:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_PRO)
        elif model == MODEL_AIRPURIFIER_PRO_V7:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO_V7
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_PRO_V7)
        elif model == MODEL_AIRPURIFIER_2S:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2S
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_2S)
        elif model == MODEL_AIRPURIFIER_2H:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2H
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_2H)
        elif model in PURIFIER_MIOT:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_3
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_3)
        elif model == MODEL_AIRPURIFIER_V3:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_V3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER_V3)
        elif model == MODEL_AIRPURIFIER_AIRDOG_X3:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_AIRDOG
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3
            self._preset_modes = [mode.name for mode in AirDogOperationMode]
        elif model == MODEL_AIRPURIFIER_AIRDOG_X5:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_AIRDOG
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X5
            self._preset_modes = [mode.name for mode in AirDogOperationMode]
        elif model == MODEL_AIRPURIFIER_AIRDOG_X7SM:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_AIRDOG
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X7SM
            self._preset_modes = [mode.name for mode in AirDogOperationMode]
        else:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER
            self._preset_modes = list(OPERATION_MODES_AIRPURIFIER)

        # Initialize base class after setting attributes
        super().__init__(coordinator)

        # Store model type for use in methods
        self._is_miot = model in PURIFIER_MIOT
        self._is_airdog = model and model.startswith("airdog.airpurifier.")

    @property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.coordinator.data:
            # Use mode name directly (already extracted in coordinator)
            mode = self.coordinator.data.get("mode")
            if mode:
                return mode
        return None

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.coordinator.data:
            # For MIOT devices, use fan_level
            fan_level = self.coordinator.data.get("fan_level")
            if fan_level is not None:
                return int(fan_level * MIOT_PERCENT_PER_LEVEL)
            # For legacy devices, use favorite_level
            fav_level = self.coordinator.data.get("favorite_level")
            if fav_level is not None:
                return int(fav_level * LEGACY_PERCENT_PER_LEVEL)
        return None

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        if self._is_miot:
            return MIOT_SPEED_LEVELS
        return LEGACY_SPEED_LEVELS

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        try:
            if self._is_miot:
                mode_enum = AirpurifierMiotOperationMode[preset_mode.title()]
            elif self._is_airdog:
                mode_enum = AirDogOperationMode[preset_mode.title()]
            else:
                mode_enum = AirpurifierOperationMode[preset_mode.title()]
        except KeyError:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        await self._try_command(
            "Setting preset mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        if self._is_miot:
            # Convert percentage to fan_level (1-3)
            level = max(1, min(MIOT_SPEED_LEVELS, int(percentage / MIOT_PERCENT_PER_LEVEL) + 1))
            await self._try_command(
                "Setting the fan level of the miio device failed: %s",
                self.coordinator.device.set_fan_level,
                level,
            )
        else:
            # Convert percentage to favorite_level (0-16)
            level = int(percentage / LEGACY_PERCENT_PER_LEVEL)
            await self._try_command(
                "Setting the favorite level of the miio device failed: %s",
                self.coordinator.device.set_favorite_level,
                level,
            )
        await self.coordinator.async_request_refresh()

    async def async_set_led_brightness(self, brightness: int = 2) -> None:
        """Set the led brightness with proper enum type."""
        from ..const import FEATURE_SET_LED_BRIGHTNESS

        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        if self._is_miot:
            brightness_enum = AirpurifierMiotLedBrightness(brightness)
        else:
            brightness_enum = AirpurifierLedBrightness(brightness)

        await self._try_command(
            "Setting the led brightness of the miio device failed: %s",
            self.coordinator.device.set_led_brightness,
            brightness_enum,
        )
        await self.coordinator.async_request_refresh()
