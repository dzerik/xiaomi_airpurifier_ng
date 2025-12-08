"""Air Fresh fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from miio.integrations.airpurifier.zhimi.airfresh import (
    LedBrightness as AirfreshLedBrightness,
    OperationMode as AirfreshOperationMode,
)
from miio.integrations.airpurifier.dmaker.airfresh_t2017 import (
    DisplayOrientation as AirfreshT2017DisplayOrientation,
    OperationMode as AirfreshT2017OperationMode,
    PtcLevel as AirfreshT2017PtcLevel,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_AIRFRESH,
    AVAILABLE_ATTRIBUTES_AIRFRESH_A1,
    AVAILABLE_ATTRIBUTES_AIRFRESH_T2017,
    AVAILABLE_ATTRIBUTES_AIRFRESH_VA4,
    FEATURE_FLAGS_AIRFRESH,
    FEATURE_FLAGS_AIRFRESH_A1,
    FEATURE_FLAGS_AIRFRESH_T2017,
    FEATURE_FLAGS_AIRFRESH_VA4,
    FEATURE_SET_DISPLAY_ORIENTATION,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_PTC,
    FEATURE_SET_PTC_LEVEL,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA4,
    OPERATION_MODES_AIRFRESH,
    OPERATION_MODES_AIRFRESH_T2017,
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiAirFreshFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Air Fresh devices."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the air fresh fan entity."""
        model = coordinator.model

        # Determine device type
        self._is_t2017 = model in [MODEL_AIRFRESH_T2017, MODEL_AIRFRESH_A1]

        # Set device features and available attributes based on model
        if model == MODEL_AIRFRESH_T2017:
            self._device_features = FEATURE_FLAGS_AIRFRESH_T2017
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_T2017
            self._preset_modes = list(OPERATION_MODES_AIRFRESH_T2017)
        elif model == MODEL_AIRFRESH_A1:
            self._device_features = FEATURE_FLAGS_AIRFRESH_A1
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_A1
            self._preset_modes = list(OPERATION_MODES_AIRFRESH_T2017)
        elif model == MODEL_AIRFRESH_VA4:
            self._device_features = FEATURE_FLAGS_AIRFRESH_VA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_VA4
            self._preset_modes = list(OPERATION_MODES_AIRFRESH)
        else:
            self._device_features = FEATURE_FLAGS_AIRFRESH
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH
            self._preset_modes = list(OPERATION_MODES_AIRFRESH)

        # Initialize base class after setting attributes
        super().__init__(coordinator)

    @property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.coordinator.data:
            mode = self.coordinator.data.get("mode")
            if mode:
                if self._is_t2017:
                    return AirfreshT2017OperationMode(mode).name
                return AirfreshOperationMode(mode).name
        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if self._is_t2017:
            mode_enum = AirfreshT2017OperationMode[preset_mode.title()]
        else:
            mode_enum = AirfreshOperationMode[preset_mode.title()]

        await self._try_command(
            "Setting preset mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_led_brightness(self, brightness: int = 2) -> None:
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        brightness_enum = AirfreshLedBrightness(brightness)

        await self._try_command(
            "Setting the led brightness of the miio device failed: %s",
            self.coordinator.device.set_led_brightness,
            brightness_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_on(self) -> None:
        """Turn the PTC heater on."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return

        await self._try_command(
            "Turning the PTC of the miio device on failed: %s",
            self.coordinator.device.set_ptc,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_off(self) -> None:
        """Turn the PTC heater off."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return

        await self._try_command(
            "Turning the PTC of the miio device off failed: %s",
            self.coordinator.device.set_ptc,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_level(self, level: str) -> None:
        """Set the PTC level (T2017 only)."""
        if self._device_features & FEATURE_SET_PTC_LEVEL == 0:
            return

        ptc_level = AirfreshT2017PtcLevel[level]

        await self._try_command(
            "Setting the PTC level of the miio device failed: %s",
            self.coordinator.device.set_ptc_level,
            ptc_level,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_display_orientation(self, orientation: str) -> None:
        """Set the display orientation (T2017 only)."""
        if self._device_features & FEATURE_SET_DISPLAY_ORIENTATION == 0:
            return

        display_orientation = AirfreshT2017DisplayOrientation[orientation]

        await self._try_command(
            "Setting the display orientation of the miio device failed: %s",
            self.coordinator.device.set_display_orientation,
            display_orientation,
        )
        await self.coordinator.async_request_refresh()
