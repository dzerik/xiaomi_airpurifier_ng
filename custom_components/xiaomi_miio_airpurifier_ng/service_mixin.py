"""Service handler mixin for Xiaomi Miio device entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import (
    FEATURE_RESET_FILTER,
    FEATURE_SET_AUTO_DETECT,
    FEATURE_SET_BUZZER,
    FEATURE_SET_CHILD_LOCK,
    FEATURE_SET_CLEAN_MODE,
    FEATURE_SET_DISPLAY_ORIENTATION,
    FEATURE_SET_DRY,
    FEATURE_SET_EXTRA_FEATURES,
    FEATURE_SET_FAN_LEVEL,
    FEATURE_SET_FAVORITE_LEVEL,
    FEATURE_SET_FAVORITE_SPEED,
    FEATURE_SET_LEARN_MODE,
    FEATURE_SET_LED,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_MOTOR_SPEED,
    FEATURE_SET_NATURAL_MODE,
    FEATURE_SET_OSCILLATION_ANGLE,
    FEATURE_SET_PTC,
    FEATURE_SET_PTC_LEVEL,
    FEATURE_SET_TARGET_HUMIDITY,
    FEATURE_SET_VOLUME,
    FEATURE_SET_WET_PROTECTION,
)

if TYPE_CHECKING:
    from .coordinator import XiaomiMiioDataUpdateCoordinator


class DeviceServiceMixin:
    """Mixin providing common service handler methods for Xiaomi devices.

    Requires the host class to provide:
    - _device_features: int (bitwise feature flags)
    - _try_command(mask_error, func, *args) -> bool (from XiaomiMiioEntity)
    - coordinator: XiaomiMiioDataUpdateCoordinator (from CoordinatorEntity)

    Must be listed AFTER XiaomiMiioEntity in MRO, or mixed so that
    XiaomiMiioEntity provides the concrete _try_command.
    """

    _device_features: int
    coordinator: XiaomiMiioDataUpdateCoordinator

    # --- Toggle services (on/off pairs) ---

    async def async_set_buzzer_on(self) -> None:
        """Turn the buzzer on."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return
        await self._try_command(
            "Turning the buzzer of the miio device on failed: %s",
            self.coordinator.device.set_buzzer,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_buzzer_off(self) -> None:
        """Turn the buzzer off."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return
        await self._try_command(
            "Turning the buzzer of the miio device off failed: %s",
            self.coordinator.device.set_buzzer,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_child_lock_on(self) -> None:
        """Turn the child lock on."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return
        await self._try_command(
            "Turning the child lock of the miio device on failed: %s",
            self.coordinator.device.set_child_lock,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_child_lock_off(self) -> None:
        """Turn the child lock off."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return
        await self._try_command(
            "Turning the child lock of the miio device off failed: %s",
            self.coordinator.device.set_child_lock,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_led_on(self) -> None:
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return
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
        await self._try_command(
            "Turning the led of the miio device off failed: %s",
            self.coordinator.device.set_led,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_led_brightness(self, brightness: int = 2) -> None:
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return
        await self._try_command(
            "Setting the led brightness of the miio device failed: %s",
            self.coordinator.device.set_led_brightness,
            brightness,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_favorite_level(self, level: int = 1) -> None:
        """Set the favorite level."""
        if self._device_features & FEATURE_SET_FAVORITE_LEVEL == 0:
            return
        await self._try_command(
            "Setting the favorite level of the miio device failed: %s",
            self.coordinator.device.set_favorite_level,
            level,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_fan_level(self, level: int = 1) -> None:
        """Set the fan level."""
        if self._device_features & FEATURE_SET_FAN_LEVEL == 0:
            return
        await self._try_command(
            "Setting the fan level of the miio device failed: %s",
            self.coordinator.device.set_fan_level,
            level,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_auto_detect_on(self) -> None:
        """Turn the auto detect on."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return
        await self._try_command(
            "Turning the auto detect of the miio device on failed: %s",
            self.coordinator.device.set_auto_detect,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_auto_detect_off(self) -> None:
        """Turn the auto detect off."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return
        await self._try_command(
            "Turning the auto detect of the miio device off failed: %s",
            self.coordinator.device.set_auto_detect,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_learn_mode_on(self) -> None:
        """Turn the learn mode on."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return
        await self._try_command(
            "Turning the learn mode of the miio device on failed: %s",
            self.coordinator.device.set_learn_mode,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_learn_mode_off(self) -> None:
        """Turn the learn mode off."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return
        await self._try_command(
            "Turning the learn mode of the miio device off failed: %s",
            self.coordinator.device.set_learn_mode,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_volume(self, volume: int = 50) -> None:
        """Set the sound volume."""
        if self._device_features & FEATURE_SET_VOLUME == 0:
            return
        await self._try_command(
            "Setting the sound volume of the miio device failed: %s",
            self.coordinator.device.set_volume,
            volume,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_extra_features(self, features: int = 1) -> None:
        """Set the extra features."""
        if self._device_features & FEATURE_SET_EXTRA_FEATURES == 0:
            return
        await self._try_command(
            "Setting the extra features of the miio device failed: %s",
            self.coordinator.device.set_extra_features,
            features,
        )
        await self.coordinator.async_request_refresh()

    async def async_reset_filter(self) -> None:
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return
        await self._try_command(
            "Resetting the filter lifetime of the miio device failed: %s",
            self.coordinator.device.reset_filter,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_target_humidity(self, humidity: int) -> None:
        """Set the target humidity."""
        if self._device_features & FEATURE_SET_TARGET_HUMIDITY == 0:
            return
        await self._try_command(
            "Setting the target humidity of the miio device failed: %s",
            self.coordinator.device.set_target_humidity,
            humidity,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_dry_on(self) -> None:
        """Turn the dry mode on."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return
        await self._try_command(
            "Turning the dry mode of the miio device on failed: %s",
            self.coordinator.device.set_dry,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_dry_off(self) -> None:
        """Turn the dry mode off."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return
        await self._try_command(
            "Turning the dry mode of the miio device off failed: %s",
            self.coordinator.device.set_dry,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_clean_mode_on(self) -> None:
        """Turn the clean mode on."""
        if self._device_features & FEATURE_SET_CLEAN_MODE == 0:
            return
        await self._try_command(
            "Turning the clean mode of the miio device on failed: %s",
            self.coordinator.device.set_clean_mode,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_clean_mode_off(self) -> None:
        """Turn the clean mode off."""
        if self._device_features & FEATURE_SET_CLEAN_MODE == 0:
            return
        await self._try_command(
            "Turning the clean mode of the miio device off failed: %s",
            self.coordinator.device.set_clean_mode,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_wet_protection_on(self) -> None:
        """Turn the wet protection on."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return
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
        await self._try_command(
            "Turning the wet protection of the miio device off failed: %s",
            self.coordinator.device.set_wet_protection,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_motor_speed(self, motor_speed: int) -> None:
        """Set the motor speed."""
        if self._device_features & FEATURE_SET_MOTOR_SPEED == 0:
            return
        await self._try_command(
            "Setting the motor speed of the miio device failed: %s",
            self.coordinator.device.set_motor_speed,
            motor_speed,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_favorite_speed(self, speed: int) -> None:
        """Set the favorite speed."""
        if self._device_features & FEATURE_SET_FAVORITE_SPEED == 0:
            return
        await self._try_command(
            "Setting the favorite speed of the miio device failed: %s",
            self.coordinator.device.set_favorite_speed,
            speed,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_oscillation_angle(self, angle: int) -> None:
        """Set the oscillation angle."""
        if self._device_features & FEATURE_SET_OSCILLATION_ANGLE == 0:
            return
        await self._try_command(
            "Setting the oscillation angle of the miio device failed: %s",
            self.coordinator.device.set_angle,
            angle,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set the delay off countdown."""
        await self._try_command(
            "Setting the delay off countdown of the miio device failed: %s",
            self.coordinator.device.delay_off,
            delay_off_countdown,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_natural_mode_on(self) -> None:
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return
        await self._try_command(
            "Turning the natural mode of the miio device on failed: %s",
            self.coordinator.device.set_natural_mode,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_natural_mode_off(self) -> None:
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return
        await self._try_command(
            "Turning the natural mode of the miio device off failed: %s",
            self.coordinator.device.set_natural_mode,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_on(self) -> None:
        """Turn the PTC on."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return
        await self._try_command(
            "Turning the PTC of the miio device on failed: %s",
            self.coordinator.device.set_ptc,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_off(self) -> None:
        """Turn the PTC off."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return
        await self._try_command(
            "Turning the PTC of the miio device off failed: %s",
            self.coordinator.device.set_ptc,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_ptc_level(self, level: str) -> None:
        """Set the PTC level."""
        if self._device_features & FEATURE_SET_PTC_LEVEL == 0:
            return
        await self._try_command(
            "Setting the PTC level of the miio device failed: %s",
            self.coordinator.device.set_ptc_level,
            level,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_display_on(self) -> None:
        """Turn the display on."""
        await self._try_command(
            "Turning the display of the miio device on failed: %s",
            self.coordinator.device.set_display,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_display_off(self) -> None:
        """Turn the display off."""
        await self._try_command(
            "Turning the display of the miio device off failed: %s",
            self.coordinator.device.set_display,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_display_orientation(self, orientation: str) -> None:
        """Set the display orientation."""
        if self._device_features & FEATURE_SET_DISPLAY_ORIENTATION == 0:
            return
        await self._try_command(
            "Setting the display orientation of the miio device failed: %s",
            self.coordinator.device.set_display_orientation,
            orientation,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_filters_cleaned(self) -> None:
        """Reset the filters cleaned counter."""
        await self._try_command(
            "Resetting the filters cleaned counter failed: %s",
            self.coordinator.device.reset_dust_filter,
        )
        await self.coordinator.async_request_refresh()
