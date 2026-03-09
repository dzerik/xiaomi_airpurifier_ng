"""Tests for fans/humidifier.py — XiaomiAirHumidifierFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_V1,
    FEATURE_FLAGS_AIRHUMIDIFIER,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA4,
    FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQS,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ,
    FEATURE_SET_LED,
    FEATURE_SET_WET_PROTECTION,
    FEATURE_SET_MOTOR_SPEED,
    FEATURE_SET_LED_BRIGHTNESS,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.humidifier import (
    XiaomiAirHumidifierFan,
)


def _make_coordinator(model="zhimi.humidifier.v1", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Humidifier"
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator._device_info = MagicMock()
    coordinator._device_info.mac_address = "AA:BB:CC:DD:EE:FF"
    coordinator._device_info.firmware_version = "1.0.0"
    coordinator._device_info.hardware_version = "ESP32"
    coordinator.available = True
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator.hass = hass
    return coordinator


class TestInit:
    """Tests for __init__ with different humidifier models."""

    def test_init_default_model(self):
        """Default humidifier (v1) sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER
        assert fan._is_miot is False
        assert fan._is_mjjsq is False
        assert fan._is_jsqs is False
        assert fan._is_jsq is False

    def test_init_ca1_model(self):
        """CA1 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA1)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_cb1_model(self):
        """CB1 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CB1)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_cb2_model(self):
        """CB2 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CB2)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_ca4_model(self):
        """CA4 model sets MIOT features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA4
        assert fan._is_miot is True

    def test_init_mjjsq_model(self):
        """MJJSQ model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
        assert fan._is_mjjsq is True

    def test_init_jsq1_model(self):
        """JSQ1 model sets correct features with wet protection."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ1)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
        assert fan._is_mjjsq is True

    def test_init_jsq2w_model(self):
        """JSQ2W model is JSQS type."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ2W)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
        assert fan._is_jsqs is True

    def test_init_jsq3_model(self):
        """JSQ3 model is JSQ5 type."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ3)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5

    def test_init_jsq5_model(self):
        """JSQ5 model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ5)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5

    def test_init_jsqs_model(self):
        """JSQS model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
        assert fan._is_jsqs is True

    def test_init_jsq001_model(self):
        """JSQ001 model (shuii) sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001)
        fan = XiaomiAirHumidifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
        assert fan._is_jsq is True


class TestPresetMode:
    """Tests for preset mode properties."""

    def test_preset_modes_not_empty(self):
        """preset_modes returns non-empty list."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        assert len(fan.preset_modes) > 0

    def test_preset_mode_from_data(self):
        """preset_mode returns mode from coordinator data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        fan = XiaomiAirHumidifierFan(coord)
        assert fan.preset_mode == "Auto"

    def test_preset_mode_none_when_no_data(self):
        """preset_mode returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiAirHumidifierFan(coord)
        assert fan.preset_mode is None

    def test_preset_mode_none_when_empty_mode(self):
        """preset_mode returns None when mode is empty."""
        coord = _make_coordinator(data={"mode": ""})
        fan = XiaomiAirHumidifierFan(coord)
        assert fan.preset_mode is None


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_miot(self):
        """MIOT model uses AirhumidifierMiotOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_mjjsq(self):
        """MJJSQ model uses AirhumidifierMjjsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        # MJJSQ modes: Low, Medium, High, Humidity, WetAndProtect
        await fan.async_set_preset_mode("Low")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_jsqs(self):
        """JSQS model uses AirhumidifierJsqsOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        # Use first available mode
        mode = fan.preset_modes[0]
        await fan.async_set_preset_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_jsq(self):
        """JSQ001 model uses AirhumidifierJsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        mode = fan.preset_modes[0]
        await fan.async_set_preset_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_legacy(self):
        """Legacy model uses AirhumidifierOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        mode = fan.preset_modes[0]
        await fan.async_set_preset_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("NonexistentMode")
        coord.device.set_mode.assert_not_called()


class TestLedOnOff:
    """Tests for LED on/off methods (JSQS uses set_light)."""

    @pytest.mark.asyncio
    async def test_led_on_jsqs_uses_set_light(self):
        """JSQS model uses set_light instead of set_led."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_on()
        coord.device.set_light.assert_called_once_with(True)
        coord.device.set_led.assert_not_called()

    @pytest.mark.asyncio
    async def test_led_off_jsqs_uses_set_light(self):
        """JSQS model uses set_light for led_off."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_off()
        coord.device.set_light.assert_called_once_with(False)
        coord.device.set_led.assert_not_called()

    @pytest.mark.asyncio
    async def test_led_on_non_jsqs_uses_set_led(self):
        """Non-JSQS model uses set_led."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_on()
        coord.device.set_led.assert_called_once_with(True)
        coord.device.set_light.assert_not_called()

    @pytest.mark.asyncio
    async def test_led_off_non_jsqs_uses_set_led(self):
        """Non-JSQS model uses set_led for led_off."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_off()
        coord.device.set_led.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_led_on_no_feature(self):
        """LED on is no-op when feature disabled."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        # CA4 doesn't have FEATURE_SET_LED
        assert not (fan._device_features & FEATURE_SET_LED)
        await fan.async_set_led_on()
        coord.device.set_led.assert_not_called()
        coord.device.set_light.assert_not_called()


class TestLedBrightness:
    """Tests for async_set_led_brightness."""

    @pytest.mark.asyncio
    async def test_led_brightness_miot(self):
        """MIOT uses AirhumidifierMiotLedBrightness enum."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_brightness(0)
        coord.device.set_led_brightness.assert_called_once()

    @pytest.mark.asyncio
    async def test_led_brightness_jsq(self):
        """JSQ001 uses AirhumidifierJsqLedBrightness enum."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_brightness(0)
        coord.device.set_led_brightness.assert_called_once()

    @pytest.mark.asyncio
    async def test_led_brightness_legacy(self):
        """Legacy uses AirhumidifierLedBrightness enum."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_led_brightness(0)
        coord.device.set_led_brightness.assert_called_once()

    @pytest.mark.asyncio
    async def test_led_brightness_no_feature(self):
        """No-op when LED brightness feature not available."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_LED_BRIGHTNESS)
        await fan.async_set_led_brightness(0)
        coord.device.set_led_brightness.assert_not_called()


class TestMotorSpeed:
    """Tests for async_set_motor_speed."""

    @pytest.mark.asyncio
    async def test_motor_speed_miot(self):
        """MIOT model calls set_speed."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_motor_speed(600)
        coord.device.set_speed.assert_called_once_with(600)

    @pytest.mark.asyncio
    async def test_motor_speed_no_feature(self):
        """No-op when motor speed feature not available."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_MOTOR_SPEED)
        await fan.async_set_motor_speed(600)
        coord.device.set_speed.assert_not_called()


class TestWetProtection:
    """Tests for wet protection methods (JSQS uses set_overwet_protect)."""

    @pytest.mark.asyncio
    async def test_wet_protection_on_jsqs(self):
        """JSQS uses set_overwet_protect."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_wet_protection_on()
        coord.device.set_overwet_protect.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_wet_protection_off_jsqs(self):
        """JSQS uses set_overwet_protect for off."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_wet_protection_off()
        coord.device.set_overwet_protect.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_wet_protection_on_non_jsqs(self):
        """Non-JSQS uses set_wet_protection."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ1)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_wet_protection_on()
        coord.device.set_wet_protection.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_wet_protection_no_feature(self):
        """No-op when wet protection feature not available."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        fan = XiaomiAirHumidifierFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_WET_PROTECTION)
        await fan.async_set_wet_protection_on()
        coord.device.set_wet_protection.assert_not_called()
        coord.device.set_overwet_protect.assert_not_called()
