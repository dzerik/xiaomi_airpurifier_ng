"""Tests for fans/base.py — XiaomiMiioBaseFan and XiaomiGenericFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.fan import FanEntityFeature

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    ATTR_MODEL,
    FEATURE_SET_BUZZER,
    FEATURE_SET_CHILD_LOCK,
    FEATURE_SET_LED,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_FAVORITE_LEVEL,
    FEATURE_SET_FAN_LEVEL,
    FEATURE_SET_AUTO_DETECT,
    FEATURE_SET_LEARN_MODE,
    FEATURE_SET_VOLUME,
    FEATURE_SET_EXTRA_FEATURES,
    FEATURE_RESET_FILTER,
    FEATURE_SET_TARGET_HUMIDITY,
    FEATURE_SET_DRY,
    FEATURE_SET_CLEAN_MODE,
    FEATURE_SET_WET_PROTECTION,
    FEATURE_SET_MOTOR_SPEED,
    FEATURE_SET_FAVORITE_SPEED,
    FEATURE_SET_OSCILLATION_ANGLE,
    FEATURE_SET_NATURAL_MODE,
    FEATURE_SET_PTC,
    FEATURE_SET_PTC_LEVEL,
    FEATURE_SET_DISPLAY_ORIENTATION,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.base import (
    XiaomiMiioBaseFan,
    XiaomiGenericFan,
)


def _make_coordinator(model="zhimi.airpurifier.mc1", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Device"
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator._device_info = MagicMock()
    coordinator._device_info.mac_address = "AA:BB:CC:DD:EE:FF"
    coordinator._device_info.firmware_version = "1.0.0"
    coordinator._device_info.hardware_version = "ESP32"
    coordinator.available = True
    # _try_command uses hass.async_add_executor_job
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator.hass = hass
    return coordinator


class TestIsOn:
    """Tests for XiaomiMiioBaseFan.is_on property."""

    def test_is_on_power_on_string(self):
        """Power='on' returns True."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        assert fan.is_on is True

    def test_is_on_power_off_string(self):
        """Power='off' returns False (not truthy check)."""
        coord = _make_coordinator(data={"power": "off"})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is False

    def test_is_on_power_bool_true(self):
        """Power=True returns True."""
        coord = _make_coordinator(data={"power": True})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is True

    def test_is_on_power_bool_false(self):
        """Power=False returns False."""
        coord = _make_coordinator(data={"power": False})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is False

    def test_is_on_no_power_key_uses_is_on(self):
        """Falls back to is_on key."""
        coord = _make_coordinator(data={"is_on": True})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is True

    def test_is_on_is_on_false(self):
        """is_on=False returns False."""
        coord = _make_coordinator(data={"is_on": False})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is False

    def test_is_on_no_data(self):
        """Empty coordinator data returns None."""
        coord = _make_coordinator(data={})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is None

    def test_is_on_none_data(self):
        """None coordinator data returns None."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is None

    def test_is_on_power_none(self):
        """Power=None without is_on returns None."""
        coord = _make_coordinator(data={"something_else": 1})
        fan = XiaomiGenericFan(coord)
        assert fan.is_on is None


class TestSupportedFeatures:
    """Tests for supported_features property."""

    def test_base_features_always_present(self):
        """TURN_ON and TURN_OFF always returned."""
        coord = _make_coordinator(data={})
        fan = XiaomiGenericFan(coord)
        features = fan.supported_features
        assert features & FanEntityFeature.TURN_ON
        assert features & FanEntityFeature.TURN_OFF

    def test_preset_mode_when_mode_in_data(self):
        """PRESET_MODE when 'mode' in data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        fan = XiaomiGenericFan(coord)
        assert fan.supported_features & FanEntityFeature.PRESET_MODE

    def test_set_speed_when_speed_in_data(self):
        """SET_SPEED when 'speed' in data."""
        coord = _make_coordinator(data={"speed": 50})
        fan = XiaomiGenericFan(coord)
        assert fan.supported_features & FanEntityFeature.SET_SPEED

    def test_set_speed_when_fan_level_in_data(self):
        """SET_SPEED when 'fan_level' in data."""
        coord = _make_coordinator(data={"fan_level": 2})
        fan = XiaomiGenericFan(coord)
        assert fan.supported_features & FanEntityFeature.SET_SPEED

    def test_no_preset_mode_without_mode(self):
        """No PRESET_MODE when 'mode' not in data."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiGenericFan(coord)
        assert not (fan.supported_features & FanEntityFeature.PRESET_MODE)


class TestExtraStateAttributes:
    """Tests for extra_state_attributes property."""

    def test_model_always_in_attrs(self):
        """Model is always present in state attributes."""
        coord = _make_coordinator(model="test.model")
        fan = XiaomiGenericFan(coord)
        attrs = fan.extra_state_attributes
        assert attrs[ATTR_MODEL] == "test.model"

    def test_empty_data_returns_defaults(self):
        """No data still returns model."""
        coord = _make_coordinator(data={})
        fan = XiaomiGenericFan(coord)
        attrs = fan.extra_state_attributes
        assert ATTR_MODEL in attrs


class TestServiceMethodsWithFeatureFlags:
    """Tests for service methods checking feature flags."""

    @pytest.mark.asyncio
    async def test_set_buzzer_on_with_flag(self):
        """Buzzer on called when feature enabled."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_BUZZER
        fan.hass = coord.hass
        await fan.async_set_buzzer_on()
        coord.device.set_buzzer.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_buzzer_on_without_flag(self):
        """Buzzer on is no-op when feature disabled."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_buzzer_on()
        coord.device.set_buzzer.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_buzzer_off_with_flag(self):
        """Buzzer off called when feature enabled."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_BUZZER
        fan.hass = coord.hass
        await fan.async_set_buzzer_off()
        coord.device.set_buzzer.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_set_child_lock_on_with_flag(self):
        """Child lock on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_CHILD_LOCK
        fan.hass = coord.hass
        await fan.async_set_child_lock_on()
        coord.device.set_child_lock.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_child_lock_off_without_flag(self):
        """Child lock off is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_child_lock_off()
        coord.device.set_child_lock.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_led_on_with_flag(self):
        """LED on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_LED
        fan.hass = coord.hass
        await fan.async_set_led_on()
        coord.device.set_led.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_led_off_without_flag(self):
        """LED off is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_led_off()
        coord.device.set_led.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_led_brightness_with_flag(self):
        """LED brightness called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_LED_BRIGHTNESS
        fan.hass = coord.hass
        await fan.async_set_led_brightness(1)
        coord.device.set_led_brightness.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_set_led_brightness_without_flag(self):
        """LED brightness is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_led_brightness(1)
        coord.device.set_led_brightness.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_favorite_level_with_flag(self):
        """Favorite level called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_FAVORITE_LEVEL
        fan.hass = coord.hass
        await fan.async_set_favorite_level(5)
        coord.device.set_favorite_level.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_set_fan_level_with_flag(self):
        """Fan level called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_FAN_LEVEL
        fan.hass = coord.hass
        await fan.async_set_fan_level(2)
        coord.device.set_fan_level.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_set_auto_detect_on_without_flag(self):
        """Auto detect on is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_auto_detect_on()
        coord.device.set_auto_detect.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_auto_detect_on_with_flag(self):
        """Auto detect on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_AUTO_DETECT
        fan.hass = coord.hass
        await fan.async_set_auto_detect_on()
        coord.device.set_auto_detect.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_learn_mode_on_with_flag(self):
        """Learn mode on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_LEARN_MODE
        fan.hass = coord.hass
        await fan.async_set_learn_mode_on()
        coord.device.set_learn_mode.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_learn_mode_off_without_flag(self):
        """Learn mode off is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_learn_mode_off()
        coord.device.set_learn_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_volume_with_flag(self):
        """Volume called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_VOLUME
        fan.hass = coord.hass
        await fan.async_set_volume(75)
        coord.device.set_volume.assert_called_once_with(75)

    @pytest.mark.asyncio
    async def test_set_extra_features_with_flag(self):
        """Extra features called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_EXTRA_FEATURES
        fan.hass = coord.hass
        await fan.async_set_extra_features(3)
        coord.device.set_extra_features.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_reset_filter_with_flag(self):
        """Reset filter called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_RESET_FILTER
        fan.hass = coord.hass
        await fan.async_reset_filter()
        coord.device.reset_filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_target_humidity_with_flag(self):
        """Target humidity called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_TARGET_HUMIDITY
        fan.hass = coord.hass
        await fan.async_set_target_humidity(60)
        coord.device.set_target_humidity.assert_called_once_with(60)

    @pytest.mark.asyncio
    async def test_set_dry_on_with_flag(self):
        """Dry on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_DRY
        fan.hass = coord.hass
        await fan.async_set_dry_on()
        coord.device.set_dry.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_dry_off_without_flag(self):
        """Dry off is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_dry_off()
        coord.device.set_dry.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_clean_mode_on_with_flag(self):
        """Clean mode on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_CLEAN_MODE
        fan.hass = coord.hass
        await fan.async_set_clean_mode_on()
        coord.device.set_clean_mode.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_wet_protection_on_with_flag(self):
        """Wet protection on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_WET_PROTECTION
        fan.hass = coord.hass
        await fan.async_set_wet_protection_on()
        coord.device.set_wet_protection.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_motor_speed_with_flag(self):
        """Motor speed called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_MOTOR_SPEED
        fan.hass = coord.hass
        await fan.async_set_motor_speed(1200)
        coord.device.set_motor_speed.assert_called_once_with(1200)

    @pytest.mark.asyncio
    async def test_set_favorite_speed_with_flag(self):
        """Favorite speed called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_FAVORITE_SPEED
        fan.hass = coord.hass
        await fan.async_set_favorite_speed(100)
        coord.device.set_favorite_speed.assert_called_once_with(100)

    @pytest.mark.asyncio
    async def test_set_oscillation_angle_with_flag(self):
        """Oscillation angle called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_OSCILLATION_ANGLE
        fan.hass = coord.hass
        await fan.async_set_oscillation_angle(90)
        coord.device.set_angle.assert_called_once_with(90)

    @pytest.mark.asyncio
    async def test_set_natural_mode_on_with_flag(self):
        """Natural mode on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_NATURAL_MODE
        fan.hass = coord.hass
        await fan.async_set_natural_mode_on()
        coord.device.set_natural_mode.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_ptc_on_with_flag(self):
        """PTC on called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_PTC
        fan.hass = coord.hass
        await fan.async_set_ptc_on()
        coord.device.set_ptc.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_ptc_level_with_flag(self):
        """PTC level called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_PTC_LEVEL
        fan.hass = coord.hass
        await fan.async_set_ptc_level("High")
        coord.device.set_ptc_level.assert_called_once_with("High")

    @pytest.mark.asyncio
    async def test_set_display_orientation_with_flag(self):
        """Display orientation called when feature enabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = FEATURE_SET_DISPLAY_ORIENTATION
        fan.hass = coord.hass
        await fan.async_set_display_orientation("left")
        coord.device.set_display_orientation.assert_called_once_with("left")

    @pytest.mark.asyncio
    async def test_set_display_orientation_without_flag(self):
        """Display orientation is no-op when feature disabled."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan._device_features = 0
        fan.hass = coord.hass
        await fan.async_set_display_orientation("left")
        coord.device.set_display_orientation.assert_not_called()


class TestTurnOnOff:
    """Tests for turn on/off methods."""

    @pytest.mark.asyncio
    async def test_turn_on_no_preset(self):
        """Turn on calls device.on."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        await fan.async_turn_on()
        coord.device.on.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_turn_off(self):
        """Turn off calls device.off."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        await fan.async_turn_off()
        coord.device.off.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_set_delay_off(self):
        """Delay off calls device.delay_off (no feature check)."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        await fan.async_set_delay_off(120)
        coord.device.delay_off.assert_called_once_with(120)

    @pytest.mark.asyncio
    async def test_set_display_on(self):
        """Display on calls device.set_display (no feature check)."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        await fan.async_set_display_on()
        coord.device.set_display.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_filters_cleaned(self):
        """Filters cleaned calls device.reset_dust_filter (no feature check)."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        fan.hass = coord.hass
        await fan.async_set_filters_cleaned()
        coord.device.reset_dust_filter.assert_called_once()


class TestGenericFan:
    """Tests for XiaomiGenericFan."""

    def test_preset_modes_none(self):
        """Generic fan has no preset modes."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        assert fan.preset_modes is None

    def test_preset_mode_none(self):
        """Generic fan current preset mode is None."""
        coord = _make_coordinator()
        fan = XiaomiGenericFan(coord)
        assert fan.preset_mode is None
