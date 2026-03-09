"""Air Dehumidifier climate entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import UnitOfTemperature
from miio.airdehumidifier import (
    FanSpeed as AirdehumidifierFanSpeed,
    OperationMode as AirdehumidifierOperationMode,
)

from ..const import (
    ATTR_MODEL,
    AVAILABLE_ATTRIBUTES_AIRDEHUMIDIFIER,
    FEATURE_FLAGS_AIRDEHUMIDIFIER,
    FEATURE_SET_BUZZER,
    FEATURE_SET_CHILD_LOCK,
    FEATURE_SET_LED,
    FEATURE_SET_TARGET_HUMIDITY,
)
from ..entity import XiaomiMiioEntity

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiAirDehumidifierClimate(XiaomiMiioEntity, ClimateEntity):
    """Coordinator-based climate entity for Air Dehumidifier."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_humidity = 40
    _attr_max_humidity = 60
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.DRY]
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, unique_id_suffix="climate")
        self._attr_name = None  # Use device name

        # Set device features and available attributes
        self._device_features = FEATURE_FLAGS_AIRDEHUMIDIFIER
        self._available_attributes = AVAILABLE_ATTRIBUTES_AIRDEHUMIDIFIER

        # Initialize state attributes
        self._state_attrs: dict[str, Any] = {ATTR_MODEL: coordinator.model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

        # Set preset and fan modes
        self._attr_preset_modes = [mode.name for mode in AirdehumidifierOperationMode]
        self._attr_fan_modes = [
            mode.name
            for mode in AirdehumidifierFanSpeed
            if mode not in [AirdehumidifierFanSpeed.Sleep, AirdehumidifierFanSpeed.Strong]
        ]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes of the device."""
        if self.coordinator.data:
            for key, attr_name in self._available_attributes.items():
                value = self.coordinator.data.get(attr_name)
                if value is not None:
                    self._state_attrs[key] = self._extract_value_from_attribute(value)
        return self._state_attrs

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features based on current mode."""
        features = ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON

        if self.hvac_mode == HVACMode.OFF:
            return features

        features |= ClimateEntityFeature.PRESET_MODE

        if self.coordinator.data:
            mode_raw = self.coordinator.data.get("mode")
            if mode_raw is not None:
                try:
                    # mode can be raw value (from base coordinator) or name string
                    if isinstance(mode_raw, str):
                        mode = AirdehumidifierOperationMode[mode_raw]
                    else:
                        mode = AirdehumidifierOperationMode(mode_raw)
                    if mode == AirdehumidifierOperationMode.Auto:
                        features |= ClimateEntityFeature.TARGET_HUMIDITY
                    if mode != AirdehumidifierOperationMode.DryCloth:
                        features |= ClimateEntityFeature.FAN_MODE
                except (ValueError, KeyError):
                    pass

        return features

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode.

        python-miio returns power as string "on"/"off".
        """
        if self.coordinator.data:
            power = self.coordinator.data.get("power")
            if power is not None:
                is_on = power == "on" if isinstance(power, str) else bool(power)
                if is_on:
                    return HVACMode.DRY
        return HVACMode.OFF

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        if self.coordinator.data:
            return self.coordinator.data.get("humidity")
        return None

    @property
    def target_humidity(self) -> int | None:
        """Return the target humidity."""
        if self.coordinator.data:
            return self.coordinator.data.get("target_humidity")
        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.coordinator.data:
            mode = self.coordinator.data.get("mode")
            if mode is not None:
                try:
                    return AirdehumidifierOperationMode(mode).name
                except ValueError:
                    _LOGGER.debug("Unknown operation mode value: %s", mode)
        return None

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        if self.coordinator.data:
            fan_speed = self.coordinator.data.get("fan_speed")
            if fan_speed is not None:
                try:
                    return AirdehumidifierFanSpeed(fan_speed).name
                except ValueError:
                    _LOGGER.debug("Unknown fan speed value: %s", fan_speed)
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.DRY:
            await self._try_command(
                "Turning the miio device on failed: %s",
                self.coordinator.device.on,
            )
        elif hvac_mode == HVACMode.OFF:
            await self._try_command(
                "Turning the miio device off failed: %s",
                self.coordinator.device.off,
            )
        await self.coordinator.async_request_refresh()

    async def async_set_humidity(self, humidity: int) -> None:
        """Set new target humidity."""
        if self._device_features & FEATURE_SET_TARGET_HUMIDITY == 0:
            return

        # Switch to Auto mode if not already (device only accepts humidity in Auto mode)
        if self.preset_mode != AirdehumidifierOperationMode.Auto.name:
            await self._try_command(
                "Setting preset mode of the miio device failed: %s",
                self.coordinator.device.set_mode,
                AirdehumidifierOperationMode.Auto,
            )

        # Round to nearest 10
        humidity = round(humidity / 10) * 10
        await self._try_command(
            "Setting the target humidity of the miio device failed: %s",
            self.coordinator.device.set_target_humidity,
            humidity,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)
        try:
            mode = AirdehumidifierOperationMode[preset_mode]
            await self._try_command(
                "Setting preset mode of the miio device failed: %s",
                self.coordinator.device.set_mode,
                mode,
            )
            await self.coordinator.async_request_refresh()
        except KeyError:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        # Fan mode cannot be changed in DryCloth mode
        if self.preset_mode == AirdehumidifierOperationMode.DryCloth.name:
            return

        _LOGGER.debug("Setting the fan mode to: %s", fan_mode)
        try:
            speed = AirdehumidifierFanSpeed[fan_mode]
            await self._try_command(
                "Setting fan mode of the miio device failed: %s",
                self.coordinator.device.set_fan_speed,
                speed,
            )
            await self.coordinator.async_request_refresh()
        except KeyError:
            _LOGGER.error("Invalid fan mode: %s", fan_mode)

    async def async_turn_on(self) -> None:
        """Turn the device on."""
        await self.async_set_hvac_mode(HVACMode.DRY)

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    # Service methods with feature flag checks

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
