"""Tests for fans/standing.py — XiaomiStandingFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.fan import FanEntityFeature

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FAN_PRESET_MODES_1C,
    FAN_SPEEDS_1C,
    FEATURE_FLAGS_FAN,
    FEATURE_FLAGS_FAN_1C,
    FEATURE_FLAGS_FAN_LESHOW_SS4,
    FEATURE_FLAGS_FAN_P5,
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
from custom_components.xiaomi_miio_airpurifier_ng.fans.standing import (
    XiaomiStandingFan,
)


def _make_coordinator(model="zhimi.fan.v2", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Fan"
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.device_info_raw = MagicMock()
    coordinator.device_info_raw.mac_address = "AA:BB:CC:DD:EE:FF"
    coordinator.device_info_raw.firmware_version = "1.0.0"
    coordinator.device_info_raw.hardware_version = "ESP32"
    coordinator.available = True
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator.hass = hass
    return coordinator


class TestInit:
    """Tests for __init__ with different fan models."""

    def test_init_standard_fan(self):
        """Standard fan (zhimi.fan.v2) sets correct features."""
        coord = _make_coordinator(model="zhimi.fan.v2")
        fan = XiaomiStandingFan(coord)
        assert fan._device_features == FEATURE_FLAGS_FAN
        assert fan._is_1c is False
        assert fan._is_leshow is False
        assert fan._is_p5_style is False

    def test_init_p5_fan(self):
        """P5 fan sets correct features."""
        coord = _make_coordinator(model=MODEL_FAN_P5)
        fan = XiaomiStandingFan(coord)
        assert fan._device_features == FEATURE_FLAGS_FAN_P5
        assert fan._is_p5_style is True

    def test_init_p8_fan_is_1c(self):
        """P8 fan uses 1C protocol."""
        coord = _make_coordinator(model=MODEL_FAN_P8)
        fan = XiaomiStandingFan(coord)
        assert fan._is_1c is True
        assert fan._device_features == FEATURE_FLAGS_FAN_1C

    def test_init_1c_fan(self):
        """1C fan sets correct features."""
        coord = _make_coordinator(model=MODEL_FAN_1C)
        fan = XiaomiStandingFan(coord)
        assert fan._is_1c is True
        assert fan._preset_modes == list(FAN_PRESET_MODES_1C.keys())

    def test_init_leshow_fan(self):
        """Leshow fan sets correct features."""
        coord = _make_coordinator(model=MODEL_FAN_LESHOW_SS4)
        fan = XiaomiStandingFan(coord)
        assert fan._is_leshow is True
        assert fan._device_features == FEATURE_FLAGS_FAN_LESHOW_SS4

    @pytest.mark.parametrize("model", [MODEL_FAN_P9, MODEL_FAN_P10, MODEL_FAN_P11, MODEL_FAN_P18])
    def test_init_p5_style_models(self, model):
        """P9/P10/P11/P18 are P5-style."""
        coord = _make_coordinator(model=model)
        fan = XiaomiStandingFan(coord)
        assert fan._is_p5_style is True


class TestSupportedFeatures:
    """Tests for supported_features property."""

    def test_standard_fan_has_direction(self):
        """Standard fan supports direction."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": True})
        fan = XiaomiStandingFan(coord)
        features = fan.supported_features
        assert features & FanEntityFeature.DIRECTION
        assert features & FanEntityFeature.OSCILLATE

    def test_leshow_no_direction(self):
        """Leshow fan does NOT support direction."""
        coord = _make_coordinator(model=MODEL_FAN_LESHOW_SS4, data={})
        fan = XiaomiStandingFan(coord)
        assert not (fan.supported_features & FanEntityFeature.DIRECTION)

    def test_1c_no_direction(self):
        """1C fan does NOT support direction."""
        coord = _make_coordinator(model=MODEL_FAN_1C, data={})
        fan = XiaomiStandingFan(coord)
        assert not (fan.supported_features & FanEntityFeature.DIRECTION)

    def test_oscillate_when_in_data(self):
        """Oscillate feature when 'oscillate' in data."""
        coord = _make_coordinator(data={"oscillate": False})
        fan = XiaomiStandingFan(coord)
        assert fan.supported_features & FanEntityFeature.OSCILLATE

    def test_no_oscillate_when_not_in_data(self):
        """No oscillate feature when 'oscillate' not in data."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiStandingFan(coord)
        assert not (fan.supported_features & FanEntityFeature.OSCILLATE)


class TestPresetMode:
    """Tests for preset mode properties."""

    def test_preset_mode_returns_mode_from_data(self):
        """Returns mode from coordinator data."""
        coord = _make_coordinator(data={"mode": "Nature"})
        fan = XiaomiStandingFan(coord)
        assert fan.preset_mode == "Nature"

    def test_preset_mode_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiStandingFan(coord)
        assert fan.preset_mode is None


class TestOscillating:
    """Tests for oscillating property."""

    def test_oscillating_true(self):
        """Returns True when oscillate is True."""
        coord = _make_coordinator(data={"oscillate": True})
        fan = XiaomiStandingFan(coord)
        assert fan.oscillating is True

    def test_oscillating_false(self):
        """Returns False when oscillate is False."""
        coord = _make_coordinator(data={"oscillate": False})
        fan = XiaomiStandingFan(coord)
        assert fan.oscillating is False

    def test_oscillating_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiStandingFan(coord)
        assert fan.oscillating is None


class TestPercentage:
    """Tests for percentage property."""

    def test_percentage_from_speed(self):
        """Returns speed as int percentage."""
        coord = _make_coordinator(data={"speed": 75})
        fan = XiaomiStandingFan(coord)
        assert fan.percentage == 75

    def test_percentage_none_when_no_speed(self):
        """Returns None when no speed data."""
        coord = _make_coordinator(data={"power": "on"})
        fan = XiaomiStandingFan(coord)
        assert fan.percentage is None


class TestSpeedCount:
    """Tests for speed_count property."""

    def test_speed_count_1c(self):
        """1C returns number of FAN_SPEEDS_1C."""
        coord = _make_coordinator(model=MODEL_FAN_1C)
        fan = XiaomiStandingFan(coord)
        assert fan.speed_count == len(FAN_SPEEDS_1C)

    def test_speed_count_standard(self):
        """Standard fan returns 100."""
        coord = _make_coordinator(model="zhimi.fan.v2")
        fan = XiaomiStandingFan(coord)
        assert fan.speed_count == 100


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_speed_off(self):
        """Setting mode to 'off' turns off the device."""
        coord = _make_coordinator()
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode(SPEED_OFF)
        coord.device.off.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_leshow(self):
        """Leshow mode uses set_mode with enum."""
        coord = _make_coordinator(model=MODEL_FAN_LESHOW_SS4)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        # Use a valid leshow mode
        from miio.integrations.fan.leshow.fan_leshow import (
            OperationMode as FanLeshowOperationMode,
        )

        valid_mode = list(FanLeshowOperationMode)[0].name
        await fan.async_set_preset_mode(valid_mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_leshow_invalid(self):
        """Leshow invalid mode does not call set_mode."""
        coord = _make_coordinator(model=MODEL_FAN_LESHOW_SS4)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("InvalidMode")
        coord.device.set_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_preset_mode_1c(self):
        """1C mode uses set_speed."""
        coord = _make_coordinator(model=MODEL_FAN_1C)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Level 1")
        coord.device.set_speed.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_p5(self):
        """P5-style mode uses set_speed."""
        coord = _make_coordinator(model=MODEL_FAN_P5)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Level 2")
        coord.device.set_speed.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_standard_natural(self):
        """Standard fan in natural mode uses set_natural_speed."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"natural_speed": 50})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Level 2")
        coord.device.set_natural_speed.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_standard_direct(self):
        """Standard fan in direct mode uses set_direct_speed."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"natural_speed": 0})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Level 2")
        coord.device.set_direct_speed.assert_called_once()


class TestOscillate:
    """Tests for async_oscillate."""

    @pytest.mark.asyncio
    async def test_oscillate_on(self):
        """Oscillate on calls set_oscillate."""
        coord = _make_coordinator()
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_oscillate(True)
        coord.device.set_oscillate.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_oscillate_off(self):
        """Oscillate off calls set_oscillate."""
        coord = _make_coordinator()
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_oscillate(False)
        coord.device.set_oscillate.assert_called_once_with(False)


class TestSetPercentage:
    """Tests for async_set_percentage."""

    @pytest.mark.asyncio
    async def test_set_percentage_zero_turns_off(self):
        """0% turns off the fan."""
        coord = _make_coordinator()
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(0)
        coord.device.off.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_percentage_p5(self):
        """P5 calls set_speed directly."""
        coord = _make_coordinator(model=MODEL_FAN_P5)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(50)
        coord.device.set_speed.assert_called_once_with(50)

    @pytest.mark.asyncio
    async def test_set_percentage_standard_direct(self):
        """Standard fan in direct mode calls set_direct_speed."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"natural_speed": 0})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(75)
        coord.device.set_direct_speed.assert_called_once_with(75)

    @pytest.mark.asyncio
    async def test_set_percentage_standard_natural(self):
        """Standard fan in natural mode calls set_natural_speed."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"natural_speed": 50})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(75)
        coord.device.set_natural_speed.assert_called_once_with(75)


class TestSetDirection:
    """Tests for async_set_direction."""

    @pytest.mark.asyncio
    async def test_set_direction_forward(self):
        """Forward maps to 'right' direction."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": False})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("forward")
        coord.device.set_rotate.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_direction_reverse(self):
        """Reverse maps to 'left' direction."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": False})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("reverse")
        coord.device.set_rotate.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_direction_invalid(self):
        """Invalid direction does not call set_rotate."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": False})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("invalid_dir")
        coord.device.set_rotate.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_direction_leshow_noop(self):
        """Leshow fan ignores set_direction."""
        coord = _make_coordinator(model=MODEL_FAN_LESHOW_SS4)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("forward")
        coord.device.set_rotate.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_direction_1c_noop(self):
        """1C fan ignores set_direction."""
        coord = _make_coordinator(model=MODEL_FAN_1C)
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("forward")
        coord.device.set_rotate.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_direction_turns_off_oscillation(self):
        """Turns off oscillation before rotating when oscillating."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": True})
        fan = XiaomiStandingFan(coord)
        fan.hass = coord.hass
        await fan.async_set_direction("forward")
        # Should have called set_oscillate(False) first
        coord.device.set_oscillate.assert_called_once_with(False)
        coord.device.set_rotate.assert_called_once()
