"""Tests for fans/air_fresh.py — XiaomiAirFreshFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FEATURE_FLAGS_AIRFRESH,
    FEATURE_FLAGS_AIRFRESH_A1,
    FEATURE_FLAGS_AIRFRESH_T2017,
    FEATURE_FLAGS_AIRFRESH_VA4,
    FEATURE_RESET_FILTER,
    FEATURE_SET_DISPLAY_ORIENTATION,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_PTC,
    FEATURE_SET_PTC_LEVEL,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA2,
    MODEL_AIRFRESH_VA4,
    OPERATION_MODES_AIRFRESH,
    OPERATION_MODES_AIRFRESH_T2017,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.air_fresh import (
    XiaomiAirFreshFan,
)


def _make_coordinator(model="zhimi.airfresh.va2", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Air Fresh"
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
    """Tests for __init__ with different air fresh models."""

    def test_init_t2017(self):
        """T2017 sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRFRESH_T2017
        assert fan._is_t2017 is True
        assert fan._preset_modes == list(OPERATION_MODES_AIRFRESH_T2017)

    def test_init_a1(self):
        """A1 sets correct features and is_t2017 flag."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_A1)
        fan = XiaomiAirFreshFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRFRESH_A1
        assert fan._is_t2017 is True

    def test_init_va4(self):
        """VA4 sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA4)
        fan = XiaomiAirFreshFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRFRESH_VA4
        assert fan._is_t2017 is False
        assert fan._preset_modes == list(OPERATION_MODES_AIRFRESH)

    def test_init_va2_default(self):
        """VA2 (default) sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRFRESH
        assert fan._is_t2017 is False


class TestPresetMode:
    """Tests for preset mode properties."""

    def test_preset_modes(self):
        """Returns preset modes list."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_modes == list(OPERATION_MODES_AIRFRESH_T2017)

    def test_preset_mode_from_data(self):
        """Returns current mode from data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode == "Auto"

    def test_preset_mode_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode is None

    def test_preset_mode_none_when_empty(self):
        """Returns None when mode is empty."""
        coord = _make_coordinator(data={"mode": ""})
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode is None


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_t2017(self):
        """T2017 uses AirfreshT2017OperationMode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_va2(self):
        """VA2 uses AirfreshOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("NonexistentMode")
        coord.device.set_mode.assert_not_called()


class TestPtc:
    """Tests for PTC on/off."""

    @pytest.mark.asyncio
    async def test_ptc_on_with_feature(self):
        """PTC on called when feature enabled."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_SET_PTC
        await fan.async_set_ptc_on()
        coord.device.set_ptc.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_ptc_off_with_feature(self):
        """PTC off called when feature enabled."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_ptc_off()
        coord.device.set_ptc.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_ptc_on_no_feature(self):
        """PTC on is no-op when feature disabled."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_PTC)
        await fan.async_set_ptc_on()
        coord.device.set_ptc.assert_not_called()


class TestPtcLevel:
    """Tests for PTC level."""

    @pytest.mark.asyncio
    async def test_set_ptc_level_valid(self):
        """Valid PTC level calls set_ptc_level with enum."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_SET_PTC_LEVEL
        await fan.async_set_ptc_level("Low")
        coord.device.set_ptc_level.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_ptc_level_invalid(self):
        """Invalid PTC level does not call device."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_ptc_level("InvalidLevel")
        coord.device.set_ptc_level.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_ptc_level_no_feature(self):
        """No-op when PTC level feature not available."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_PTC_LEVEL)
        await fan.async_set_ptc_level("Low")
        coord.device.set_ptc_level.assert_not_called()


class TestDisplayOrientation:
    """Tests for display orientation."""

    @pytest.mark.asyncio
    async def test_set_display_orientation_valid(self):
        """Valid orientation calls device method."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_SET_DISPLAY_ORIENTATION
        await fan.async_set_display_orientation("Portrait")
        coord.device.set_display_orientation.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_display_orientation_invalid(self):
        """Invalid orientation does not call device."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_display_orientation("InvalidOrientation")
        coord.device.set_display_orientation.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_display_orientation_no_feature(self):
        """No-op when display orientation feature not available."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_DISPLAY_ORIENTATION)
        await fan.async_set_display_orientation("Portrait")
        coord.device.set_display_orientation.assert_not_called()


class TestResetFilter:
    """Tests for filter reset."""

    @pytest.mark.asyncio
    async def test_reset_filter_t2017_dual(self):
        """T2017 resets both upper and dust filters."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_RESET_FILTER
        await fan.async_reset_filter()
        coord.device.reset_upper_filter.assert_called_once()
        coord.device.reset_dust_filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_filter_a1_single(self):
        """A1 resets single filter only."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_A1)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_RESET_FILTER
        await fan.async_reset_filter()
        coord.device.reset_filter.assert_called_once()
        coord.device.reset_upper_filter.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_filter_va2(self):
        """VA2 resets single filter."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_RESET_FILTER
        await fan.async_reset_filter()
        coord.device.reset_filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_filter_no_feature(self):
        """No-op when reset filter feature not available."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan._device_features = 0  # Remove all features
        fan.hass = coord.hass
        await fan.async_reset_filter()
        coord.device.reset_filter.assert_not_called()


class TestLedBrightness:
    """Tests for LED brightness."""

    @pytest.mark.asyncio
    async def test_led_brightness_with_feature(self):
        """LED brightness called when feature enabled."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert fan._device_features & FEATURE_SET_LED_BRIGHTNESS
        await fan.async_set_led_brightness(1)
        coord.device.set_led_brightness.assert_called_once()

    @pytest.mark.asyncio
    async def test_led_brightness_no_feature(self):
        """No-op when LED brightness feature not available."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        assert not (fan._device_features & FEATURE_SET_LED_BRIGHTNESS)
        await fan.async_set_led_brightness(1)
        coord.device.set_led_brightness.assert_not_called()
