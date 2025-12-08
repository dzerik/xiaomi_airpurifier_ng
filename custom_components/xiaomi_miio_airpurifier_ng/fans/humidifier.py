"""Air Humidifier fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from miio.integrations.humidifier.zhimi.airhumidifier import (
    LedBrightness as AirhumidifierLedBrightness,
    OperationMode as AirhumidifierOperationMode,
)
from miio.integrations.humidifier.zhimi.airhumidifier_miot import (
    LedBrightness as AirhumidifierMiotLedBrightness,
    OperationMode as AirhumidifierMiotOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_mjjsq import (
    OperationMode as AirhumidifierMjjsqOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_jsqs import (
    OperationMode as AirhumidifierJsqsOperationMode,
)
from miio.integrations.humidifier.shuii.airhumidifier_jsq import (
    LedBrightness as AirhumidifierJsqLedBrightness,
    OperationMode as AirhumidifierJsqOperationMode,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ,
    FEATURE_FLAGS_AIRHUMIDIFIER,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA4,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQS,
    FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ,
    FEATURE_SET_LED,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_MOTOR_SPEED,
    FEATURE_SET_WET_PROTECTION,
    HUMIDIFIER_MIOT,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiAirHumidifierFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Air Humidifiers."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the air humidifier fan entity."""
        model = coordinator.model

        # Determine device type for later use
        self._is_miot = model in HUMIDIFIER_MIOT
        self._is_mjjsq = model in [
            MODEL_AIRHUMIDIFIER_MJJSQ,
            MODEL_AIRHUMIDIFIER_JSQ,
            MODEL_AIRHUMIDIFIER_JSQ1,
        ]
        self._is_jsqs = model in [
            MODEL_AIRHUMIDIFIER_JSQ2W,
            MODEL_AIRHUMIDIFIER_JSQ3,
            MODEL_AIRHUMIDIFIER_JSQ5,
            MODEL_AIRHUMIDIFIER_JSQS,
        ]
        self._is_jsq = model == MODEL_AIRHUMIDIFIER_JSQ001

        # Set device features and available attributes based on model
        if model in [MODEL_AIRHUMIDIFIER_CA1, MODEL_AIRHUMIDIFIER_CB1, MODEL_AIRHUMIDIFIER_CB2]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Strong
            ]
        elif model == MODEL_AIRHUMIDIFIER_CA4:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._preset_modes = [mode.name for mode in AirhumidifierMiotOperationMode]
        elif model == MODEL_AIRHUMIDIFIER_JSQ1:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_MJJSQ, MODEL_AIRHUMIDIFIER_JSQ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ3, MODEL_AIRHUMIDIFIER_JSQ5]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5
            self._preset_modes = [mode.name for mode in AirhumidifierJsqsOperationMode]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ2W, MODEL_AIRHUMIDIFIER_JSQS]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS
            self._preset_modes = [mode.name for mode in AirhumidifierJsqsOperationMode]
        elif model == MODEL_AIRHUMIDIFIER_JSQ001:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ
            self._preset_modes = [mode.name for mode in AirhumidifierJsqOperationMode]
        elif self._is_miot:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._preset_modes = [mode.name for mode in AirhumidifierMiotOperationMode]
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Auto
            ]

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
                # Handle different operation mode enums based on device type
                if self._is_miot:
                    return AirhumidifierMiotOperationMode(mode).name
                if self._is_mjjsq:
                    return AirhumidifierMjjsqOperationMode(mode).name
                if self._is_jsqs:
                    return AirhumidifierJsqsOperationMode(mode).name
                if self._is_jsq:
                    return AirhumidifierJsqOperationMode(mode).name
                return AirhumidifierOperationMode(mode).name
        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if self._is_miot:
            mode_enum = AirhumidifierMiotOperationMode[preset_mode.title()]
        elif self._is_mjjsq:
            mode_enum = AirhumidifierMjjsqOperationMode[preset_mode.title()]
        elif self._is_jsqs:
            mode_enum = AirhumidifierJsqsOperationMode[preset_mode.title()]
        elif self._is_jsq:
            mode_enum = AirhumidifierJsqOperationMode[preset_mode.title()]
        else:
            mode_enum = AirhumidifierOperationMode[preset_mode.title()]

        await self._try_command(
            "Setting preset mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_led_on(self) -> None:
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        # JSQS models use set_light instead of set_led
        if self._is_jsqs:
            await self._try_command(
                "Turning the led of the miio device on failed: %s",
                self.coordinator.device.set_light,
                True,
            )
        else:
            await self._try_command(
                "Turning the led of the miio device on failed: %s",
                self.coordinator.device.set_led,
                True,
            )
        await self.coordinator.async_request_refresh()

    async def async_set_led_off(self) -> None:
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        # JSQS models use set_light instead of set_led
        if self._is_jsqs:
            await self._try_command(
                "Turning the led of the miio device off failed: %s",
                self.coordinator.device.set_light,
                False,
            )
        else:
            await self._try_command(
                "Turning the led of the miio device off failed: %s",
                self.coordinator.device.set_led,
                False,
            )
        await self.coordinator.async_request_refresh()

    async def async_set_led_brightness(self, brightness: int = 2) -> None:
        """Set the led brightness with proper enum type."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        if self._is_miot:
            brightness_enum = AirhumidifierMiotLedBrightness(brightness)
        elif self._is_jsq:
            brightness_enum = AirhumidifierJsqLedBrightness(brightness)
        else:
            brightness_enum = AirhumidifierLedBrightness(brightness)

        await self._try_command(
            "Setting the led brightness of the miio device failed: %s",
            self.coordinator.device.set_led_brightness,
            brightness_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_motor_speed(self, motor_speed: int = 400) -> None:
        """Set the target motor speed (MIOT models only)."""
        if self._device_features & FEATURE_SET_MOTOR_SPEED == 0:
            return

        await self._try_command(
            "Setting the target motor speed of the miio device failed: %s",
            self.coordinator.device.set_speed,
            motor_speed,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_wet_protection_on(self) -> None:
        """Turn the wet protection on."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        # JSQS models use set_overwet_protect instead of set_wet_protection
        if self._is_jsqs:
            await self._try_command(
                "Turning the wet protection of the miio device on failed: %s",
                self.coordinator.device.set_overwet_protect,
                True,
            )
        else:
            await self._try_command(
                "Turning the wet protection of the miio device on failed: %s",
                self.coordinator.device.set_wet_protection,
                True,
            )
        await self.coordinator.async_request_refresh()

    async def async_set_wet_protection_off(self) -> None:
        """Turn the wet protection off."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        # JSQS models use set_overwet_protect instead of set_wet_protection
        if self._is_jsqs:
            await self._try_command(
                "Turning the wet protection of the miio device off failed: %s",
                self.coordinator.device.set_overwet_protect,
                False,
            )
        else:
            await self._try_command(
                "Turning the wet protection of the miio device off failed: %s",
                self.coordinator.device.set_wet_protection,
                False,
            )
        await self.coordinator.async_request_refresh()
