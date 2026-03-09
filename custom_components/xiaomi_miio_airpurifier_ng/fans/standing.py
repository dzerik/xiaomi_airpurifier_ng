"""Standing fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.fan import FanEntityFeature
from miio.fan_common import (
    LedBrightness as FanLedBrightness,
)
from miio.fan_common import (
    MoveDirection as FanMoveDirection,
)
from miio.fan_common import (
    OperationMode as FanOperationMode,
)
from miio.integrations.fan.leshow.fan_leshow import (
    OperationMode as FanLeshowOperationMode,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_FAN,
    AVAILABLE_ATTRIBUTES_FAN_1C,
    AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4,
    AVAILABLE_ATTRIBUTES_FAN_P5,
    FAN_PRESET_MODE_VALUES,
    FAN_PRESET_MODE_VALUES_P5,
    FAN_PRESET_MODES,
    FAN_PRESET_MODES_1C,
    FAN_SPEEDS_1C,
    FEATURE_FLAGS_FAN,
    FEATURE_FLAGS_FAN_1C,
    FEATURE_FLAGS_FAN_LESHOW_SS4,
    FEATURE_FLAGS_FAN_P5,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_NATURAL_MODE,
    FEATURE_SET_OSCILLATION_ANGLE,
    MODEL_FAN_1C,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_P5,
    MODEL_FAN_P8,
    MODEL_FAN_P9,
    MODEL_FAN_P10,
    MODEL_FAN_P11,
    MODEL_FAN_P18,
    SPEED_OFF,
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiStandingFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Standing Fans."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the standing fan entity."""
        model = coordinator.model

        # Determine device type (P8 uses 1C protocol, not P5-style)
        self._is_1c = model in [MODEL_FAN_1C, MODEL_FAN_P8]
        self._is_leshow = model == MODEL_FAN_LESHOW_SS4
        self._is_p5_style = not self._is_1c and model in [
            MODEL_FAN_P5,
            MODEL_FAN_P9,
            MODEL_FAN_P10,
            MODEL_FAN_P11,
            MODEL_FAN_P18,
        ]

        # Set device features and available attributes based on model
        if self._is_leshow:
            self._device_features = FEATURE_FLAGS_FAN_LESHOW_SS4
            self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4
            self._preset_modes = [mode.name for mode in FanLeshowOperationMode]
        elif self._is_1c:
            self._device_features = FEATURE_FLAGS_FAN_1C
            self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_1C
            self._preset_modes = list(FAN_PRESET_MODES_1C.keys())
        elif self._is_p5_style:
            self._device_features = FEATURE_FLAGS_FAN_P5
            self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_P5
            self._preset_modes = list(FAN_PRESET_MODES.keys())
        else:
            self._device_features = FEATURE_FLAGS_FAN
            self._available_attributes = AVAILABLE_ATTRIBUTES_FAN
            self._preset_modes = list(FAN_PRESET_MODES.keys())

        # Initialize base class after setting attributes
        super().__init__(coordinator)

    @property
    def _is_natural_mode(self) -> bool:
        """Determine natural mode from coordinator data.

        For P5-style fans: mode == "Nature".
        For legacy fans: natural_speed > 0 indicates natural mode.
        """
        if not self.coordinator.data:
            return False
        if self._is_p5_style:
            return self.coordinator.data.get("mode") == "Nature"
        # Legacy fans: natural_speed > 0 means natural mode is active
        natural_speed = self.coordinator.data.get("natural_speed")
        return bool(natural_speed and natural_speed > 0)

    @property
    def supported_features(self) -> FanEntityFeature:
        """Return supported features."""
        features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )

        if self.coordinator.data:
            if "oscillate" in self.coordinator.data:
                features |= FanEntityFeature.OSCILLATE

        # Standard fans support direction
        if not self._is_leshow and not self._is_1c:
            features |= FanEntityFeature.DIRECTION

        return features

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
    def oscillating(self) -> bool | None:
        """Return whether oscillation is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("oscillate")
        return None

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.coordinator.data:
            speed = self.coordinator.data.get("speed")
            if speed is not None:
                return int(speed)

            # For 1C models, map preset to percentage
            if self._is_1c:
                mode = self.coordinator.data.get("mode")
                if mode:
                    for preset_mode, value in FAN_PRESET_MODES_1C.items():
                        if mode == value:
                            from homeassistant.util.percentage import (
                                ordered_list_item_to_percentage,
                            )

                            return ordered_list_item_to_percentage(FAN_SPEEDS_1C, preset_mode)
        return None

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        if self._is_1c:
            return len(FAN_SPEEDS_1C)
        return 100  # Percentage-based

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if preset_mode == SPEED_OFF:
            await self.async_turn_off()
            return

        if self._is_leshow:
            try:
                mode_enum = FanLeshowOperationMode[preset_mode.title()]
            except KeyError:
                _LOGGER.error("Invalid preset mode: %s", preset_mode)
                return
            await self._try_command(
                "Setting preset mode of the miio device failed: %s",
                self.coordinator.device.set_mode,
                mode_enum,
            )
        elif self._is_1c:
            speed = FAN_PRESET_MODES_1C.get(preset_mode, 1)
            await self._try_command(
                "Setting fan speed of the miio device failed: %s",
                self.coordinator.device.set_speed,
                speed,
            )
        elif self._is_p5_style:
            speed = FAN_PRESET_MODE_VALUES_P5.get(preset_mode, 35)
            await self._try_command(
                "Setting fan speed of the miio device failed: %s",
                self.coordinator.device.set_speed,
                speed,
            )
        else:
            # Standard fan - use natural or direct speed based on mode
            speed = FAN_PRESET_MODE_VALUES.get(preset_mode, 35)
            if self._is_natural_mode:
                await self._try_command(
                    "Setting fan speed of the miio device failed: %s",
                    self.coordinator.device.set_natural_speed,
                    speed,
                )
            else:
                await self._try_command(
                    "Setting fan speed of the miio device failed: %s",
                    self.coordinator.device.set_direct_speed,
                    speed,
                )

        await self.coordinator.async_request_refresh()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        await self._try_command(
            "Setting oscillate of the miio device failed: %s",
            self.coordinator.device.set_oscillate,
            oscillating,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        if self._is_1c:
            # Convert percentage to 1C speed level
            from homeassistant.util.percentage import (
                percentage_to_ordered_list_item,
            )

            preset_mode = percentage_to_ordered_list_item(FAN_SPEEDS_1C, percentage)
            speed = FAN_PRESET_MODES_1C.get(preset_mode, 1)
            await self._try_command(
                "Setting fan speed of the miio device failed: %s",
                self.coordinator.device.set_speed,
                speed,
            )
        elif self._is_p5_style or self._is_leshow:
            await self._try_command(
                "Setting fan speed percentage of the miio device failed: %s",
                self.coordinator.device.set_speed,
                percentage,
            )
        else:
            # Standard fan - use natural or direct speed
            if self._is_natural_mode:
                await self._try_command(
                    "Setting fan speed percentage of the miio device failed: %s",
                    self.coordinator.device.set_natural_speed,
                    percentage,
                )
            else:
                await self._try_command(
                    "Setting fan speed percentage of the miio device failed: %s",
                    self.coordinator.device.set_direct_speed,
                    percentage,
                )

        await self.coordinator.async_request_refresh()

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan (rotate)."""
        if self._is_leshow or self._is_1c:
            return

        # Map Home Assistant direction to device direction
        if direction == "forward":
            direction = "right"
        elif direction == "reverse":
            direction = "left"

        # Turn off oscillation before rotating
        if self.oscillating:
            await self._try_command(
                "Setting oscillate off of the miio device failed: %s",
                self.coordinator.device.set_oscillate,
                False,
            )

        try:
            move_direction = FanMoveDirection(direction)
        except ValueError:
            _LOGGER.error("Invalid move direction: %s", direction)
            return

        await self._try_command(
            "Setting move direction of the miio device failed: %s",
            self.coordinator.device.set_rotate,
            move_direction,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_oscillation_angle(self, angle: int) -> None:
        """Set oscillation angle."""
        if self._device_features & FEATURE_SET_OSCILLATION_ANGLE == 0:
            return

        await self._try_command(
            "Setting angle of the miio device failed: %s",
            self.coordinator.device.set_angle,
            angle,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""
        # P5-style fans use minutes directly, others use seconds
        if self._is_p5_style or self._is_leshow:
            delay = delay_off_countdown
        else:
            delay = delay_off_countdown * 60

        await self._try_command(
            "Setting delay off miio device failed: %s",
            self.coordinator.device.delay_off,
            delay,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_led_brightness(self, brightness: int = 2) -> None:
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        brightness_enum = FanLedBrightness(brightness)

        await self._try_command(
            "Setting the led brightness of the miio device failed: %s",
            self.coordinator.device.set_led_brightness,
            brightness_enum,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_natural_mode_on(self) -> None:
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        
        if self._is_p5_style:
            await self._try_command(
                "Turning on natural mode of the miio device failed: %s",
                self.coordinator.device.set_mode,
                FanOperationMode.Nature,
            )
        else:
            # For standard fans, re-set the speed in natural mode
            percentage = self.percentage or 50
            await self._try_command(
                "Setting fan speed in natural mode failed: %s",
                self.coordinator.device.set_natural_speed,
                percentage,
            )

        await self.coordinator.async_request_refresh()

    async def async_set_natural_mode_off(self) -> None:
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        
        if self._is_p5_style:
            await self._try_command(
                "Turning off natural mode of the miio device failed: %s",
                self.coordinator.device.set_mode,
                FanOperationMode.Normal,
            )
        else:
            # For standard fans, re-set the speed in direct mode
            percentage = self.percentage or 50
            await self._try_command(
                "Setting fan speed in direct mode failed: %s",
                self.coordinator.device.set_direct_speed,
                percentage,
            )

        await self.coordinator.async_request_refresh()
