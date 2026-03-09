"""Tests for fans/base.py — XiaomiMiioBaseFan and XiaomiGenericFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.fan import FanEntityFeature

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    ATTR_MODEL,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.base import (
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
