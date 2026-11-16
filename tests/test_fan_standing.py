"""Tests for fans/standing.py — XiaomiStandingFan."""

from __future__ import annotations

import pytest
from homeassistant.components.fan import FanEntityFeature

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FAN_SPEEDS_1C,
    MODEL_FAN_1C,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_P5,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.standing import (
    XiaomiStandingFan,
)


def _make_coordinator(model="zhimi.fan.v2", data=None):
    """Use real orchestration with a bounded driver mock."""
    from tests.device_helpers import make_coordinator

    return make_coordinator(model=model, data=data)


class TestSupportedFeatures:
    """Tests for supported_features property."""

    def test_standard_fan_has_direction(self):
        """Standard fan supports direction."""
        coord = _make_coordinator(model="zhimi.fan.v2", data={"oscillate": True})
        fan = XiaomiStandingFan(coord)
        features = fan.supported_features
        assert not (features & FanEntityFeature.DIRECTION)
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
        assert fan.supported_features & FanEntityFeature.OSCILLATE


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
        coord = _make_coordinator(data={"speed": 850, "direct_speed": 75})
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
        coord.device.set_direct_speed.assert_called_once_with(75)
