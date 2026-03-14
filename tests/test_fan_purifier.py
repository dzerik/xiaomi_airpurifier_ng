"""Tests for fans/purifier.py — XiaomiAirPurifierFan."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FEATURE_FLAGS_AIRPURIFIER,
    FEATURE_FLAGS_AIRPURIFIER_3,
    FEATURE_FLAGS_AIRPURIFIER_AIRDOG,
    FEATURE_FLAGS_AIRPURIFIER_PRO,
    MODEL_AIRPURIFIER_3,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_AIRDOG_X5,
    MODEL_AIRPURIFIER_AIRDOG_X7SM,
    MODEL_AIRPURIFIER_PRO,
    OPERATION_MODES_AIRPURIFIER,
    OPERATION_MODES_AIRPURIFIER_3,
    OPERATION_MODES_AIRPURIFIER_PRO,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.purifier import (
    LEGACY_PERCENT_PER_LEVEL,
    LEGACY_SPEED_LEVELS,
    MIOT_PERCENT_PER_LEVEL,
    MIOT_SPEED_LEVELS,
    XiaomiAirPurifierFan,
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
    """Tests for __init__ with different model types."""

    def test_init_default_model(self):
        """Default (legacy) model sets correct features."""
        coord = _make_coordinator(model="zhimi.airpurifier.v2")
        fan = XiaomiAirPurifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRPURIFIER
        assert fan._preset_modes == list(OPERATION_MODES_AIRPURIFIER)
        assert fan._is_miot is False
        assert fan._is_airdog is False

    def test_init_pro_model(self):
        """Pro model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_PRO)
        fan = XiaomiAirPurifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRPURIFIER_PRO
        assert fan._preset_modes == list(OPERATION_MODES_AIRPURIFIER_PRO)

    def test_init_miot_model(self):
        """MIOT model (ma4) sets correct features and is_miot flag."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRPURIFIER_3
        assert fan._preset_modes == list(OPERATION_MODES_AIRPURIFIER_3)
        assert fan._is_miot is True

    def test_init_airdog_x3(self):
        """AirDog X3 sets correct features and is_airdog flag."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_AIRDOG_X3)
        fan = XiaomiAirPurifierFan(coord)
        assert fan._device_features == FEATURE_FLAGS_AIRPURIFIER_AIRDOG
        assert fan._is_airdog is True
        assert len(fan._preset_modes) > 0

    def test_init_airdog_x5(self):
        """AirDog X5 sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_AIRDOG_X5)
        fan = XiaomiAirPurifierFan(coord)
        assert fan._is_airdog is True

    def test_init_airdog_x7sm(self):
        """AirDog X7SM sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_AIRDOG_X7SM)
        fan = XiaomiAirPurifierFan(coord)
        assert fan._is_airdog is True


class TestPresetMode:
    """Tests for preset mode properties."""

    def test_preset_modes_returns_list(self):
        """preset_modes returns the list from init."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        assert fan.preset_modes == list(OPERATION_MODES_AIRPURIFIER_3)

    def test_preset_mode_from_data(self):
        """preset_mode returns mode from coordinator data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.preset_mode == "Auto"

    def test_preset_mode_no_data(self):
        """preset_mode returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiAirPurifierFan(coord)
        assert fan.preset_mode is None

    def test_preset_mode_empty_mode(self):
        """preset_mode returns None when mode is empty string."""
        coord = _make_coordinator(data={"mode": ""})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.preset_mode is None


class TestPercentage:
    """Tests for percentage property."""

    def test_percentage_miot_fan_level(self):
        """MIOT: percentage from fan_level."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3, data={"fan_level": 2})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.percentage == int(2 * MIOT_PERCENT_PER_LEVEL)

    def test_percentage_legacy_fav_level(self):
        """Legacy: percentage from favorite_level."""
        coord = _make_coordinator(data={"favorite_level": 8})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.percentage == int(8 * LEGACY_PERCENT_PER_LEVEL)

    def test_percentage_fan_level_zero(self):
        """fan_level=0 returns 0%."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3, data={"fan_level": 0})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.percentage == 0

    def test_percentage_no_data(self):
        """No data returns None."""
        coord = _make_coordinator(data={})
        fan = XiaomiAirPurifierFan(coord)
        assert fan.percentage is None

    def test_percentage_none_data(self):
        """None data returns None."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiAirPurifierFan(coord)
        assert fan.percentage is None


class TestSpeedCount:
    """Tests for speed_count property."""

    def test_speed_count_miot(self):
        """MIOT returns 3 speed levels."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        assert fan.speed_count == MIOT_SPEED_LEVELS

    def test_speed_count_legacy(self):
        """Legacy returns 16 speed levels."""
        coord = _make_coordinator(model="zhimi.airpurifier.v2")
        fan = XiaomiAirPurifierFan(coord)
        assert fan.speed_count == LEGACY_SPEED_LEVELS


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_miot(self):
        """MIOT model uses AirpurifierMiotOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_airdog(self):
        """AirDog model uses AirDogOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_AIRDOG_X3)
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_legacy(self):
        """Legacy model uses AirpurifierOperationMode."""
        coord = _make_coordinator(model="zhimi.airpurifier.v2")
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator(model="zhimi.airpurifier.v2")
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("InvalidMode")
        coord.device.set_mode.assert_not_called()


class TestSetPercentage:
    """Tests for async_set_percentage."""

    @pytest.mark.asyncio
    async def test_set_percentage_miot(self):
        """MIOT converts percentage to fan_level."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(66)
        coord.device.set_fan_level.assert_called_once()
        level = coord.device.set_fan_level.call_args[0][0]
        assert 1 <= level <= 3

    @pytest.mark.asyncio
    async def test_set_percentage_legacy(self):
        """Legacy converts percentage to favorite_level."""
        coord = _make_coordinator(model="zhimi.airpurifier.v2")
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(50)
        coord.device.set_favorite_level.assert_called_once()
        level = coord.device.set_favorite_level.call_args[0][0]
        assert 0 <= level <= 16

    @pytest.mark.asyncio
    async def test_set_percentage_miot_100(self):
        """100% maps to fan_level 3 (max)."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(100)
        level = coord.device.set_fan_level.call_args[0][0]
        assert level == 3

    @pytest.mark.asyncio
    async def test_set_percentage_miot_1(self):
        """1% maps to fan_level 1 (min)."""
        coord = _make_coordinator(model=MODEL_AIRPURIFIER_3)
        fan = XiaomiAirPurifierFan(coord)
        fan.hass = coord.hass
        await fan.async_set_percentage(1)
        level = coord.device.set_fan_level.call_args[0][0]
        assert level >= 1
