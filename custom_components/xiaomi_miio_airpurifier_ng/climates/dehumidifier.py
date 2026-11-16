"""Air Dehumidifier climate entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import UnitOfTemperature
from miio.airdehumidifier import (
    FanSpeed as AirdehumidifierFanSpeed,
)
from miio.airdehumidifier import (
    OperationMode as AirdehumidifierOperationMode,
)

from ..const import (
    ATTR_MODEL,
    AVAILABLE_ATTRIBUTES_AIRDEHUMIDIFIER,
    DOMAIN,
    FEATURE_FLAGS_AIRDEHUMIDIFIER,
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
        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

        # Set preset and fan modes
        self._attr_preset_modes = [mode.name for mode in AirdehumidifierOperationMode]
        self._attr_fan_modes = [
            mode.name
            for mode in AirdehumidifierFanSpeed
            if mode not in [AirdehumidifierFanSpeed.Sleep, AirdehumidifierFanSpeed.Strong]
        ]

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
                except ValueError, KeyError:
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
        """Return the current preset mode.

        coordinator.data["mode"] is already a string (enum .name) via _parse_mode().
        """
        if self.coordinator.data:
            return self.coordinator.data.get("mode")
        return None

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode.

        coordinator.data["fan_speed"] is already a string (enum .name).
        """
        if self.coordinator.data:
            return self.coordinator.data.get("fan_speed")
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.DRY:
            await self._async_device_on()
        elif hvac_mode == HVACMode.OFF:
            await self._async_device_off()

    async def async_set_humidity(self, humidity: int) -> None:
        """Use the same mode prerequisite and range as the number control."""
        await self.coordinator.async_set_humidity(humidity)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Validate the exposed mode before using the shared command path."""
        from homeassistant.exceptions import ServiceValidationError

        allowed = self.preset_modes or []
        if preset_mode not in allowed:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        await self._async_command("set_mode", AirdehumidifierOperationMode[preset_mode])

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Validate the exposed mode before using the shared command path."""
        from homeassistant.exceptions import ServiceValidationError

        allowed = self.fan_modes or []
        if (
            fan_mode not in allowed
            or self.preset_mode == AirdehumidifierOperationMode.DryCloth.name
        ):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        await self._async_command("set_fan_speed", AirdehumidifierFanSpeed[fan_mode])

    async def async_turn_on(self) -> None:
        """Turn the device on."""
        await self.async_set_hvac_mode(HVACMode.DRY)

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
