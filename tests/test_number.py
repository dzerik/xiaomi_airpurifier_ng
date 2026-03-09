"""Tests for number.py — XiaomiMiioNumber."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.number import (
    NUMBER_DESCRIPTIONS,
    XiaomiMiioNumber,
    XiaomiMiioNumberEntityDescription,
)


def _make_coordinator(data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = "zhimi.airpurifier.mc1"
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
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator.hass = hass
    return coordinator


def _get_description(key: str) -> XiaomiMiioNumberEntityDescription:
    """Get a number description by key."""
    for desc in NUMBER_DESCRIPTIONS:
        if desc.key == key:
            return desc
    raise ValueError(f"No number description with key={key}")


class TestNativeValue:
    """Tests for native_value property."""

    def test_native_value_favorite_level(self):
        """Returns float value for favorite_level."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 10})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value == 10.0

    def test_native_value_fan_level(self):
        """Returns float value for fan_level."""
        desc = _get_description("fan_level")
        coord = _make_coordinator(data={"fan_level": 2})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value == 2.0

    def test_native_value_volume(self):
        """Returns float value for volume."""
        desc = _get_description("volume")
        coord = _make_coordinator(data={"volume": 75})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value == 75.0

    def test_native_value_target_humidity(self):
        """Returns float value for target_humidity."""
        desc = _get_description("target_humidity")
        coord = _make_coordinator(data={"target_humidity": 50})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value == 50.0

    def test_native_value_none_when_no_data(self):
        """Returns None when no data."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data=None)
        coord.data = None
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value is None

    def test_native_value_none_when_key_missing(self):
        """Returns None when key not in data."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"led": True})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value is None

    def test_native_value_zero(self):
        """Returns 0.0 for zero value."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 0})
        number = XiaomiMiioNumber(coord, desc)
        assert number.native_value == 0.0

    def test_native_value_returns_float(self):
        """Always returns float type."""
        desc = _get_description("fan_level")
        coord = _make_coordinator(data={"fan_level": 3})
        number = XiaomiMiioNumber(coord, desc)
        assert isinstance(number.native_value, float)


class TestSetNativeValue:
    """Tests for async_set_native_value."""

    @pytest.mark.asyncio
    async def test_set_favorite_level(self):
        """Sets favorite_level as int."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 5})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(10.0)
        coord.device.set_favorite_level.assert_called_once_with(10)
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_set_fan_level(self):
        """Sets fan_level as int."""
        desc = _get_description("fan_level")
        coord = _make_coordinator(data={"fan_level": 1})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(3.0)
        coord.device.set_fan_level.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_set_volume(self):
        """Sets volume as int."""
        desc = _get_description("volume")
        coord = _make_coordinator(data={"volume": 50})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(75.0)
        coord.device.set_volume.assert_called_once_with(75)

    @pytest.mark.asyncio
    async def test_set_target_humidity(self):
        """Sets target_humidity as int."""
        desc = _get_description("target_humidity")
        coord = _make_coordinator(data={"target_humidity": 50})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(60.0)
        coord.device.set_target_humidity.assert_called_once_with(60)

    @pytest.mark.asyncio
    async def test_set_angle(self):
        """Sets angle as int."""
        desc = _get_description("angle")
        coord = _make_coordinator(data={"angle": 60})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(90.0)
        coord.device.set_angle.assert_called_once_with(90)

    @pytest.mark.asyncio
    async def test_set_delay_off(self):
        """Sets delay_off as int."""
        desc = _get_description("delay_off_countdown")
        coord = _make_coordinator(data={"delay_off_countdown": 0})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(120.0)
        coord.device.delay_off.assert_called_once_with(120)

    @pytest.mark.asyncio
    async def test_set_value_converts_float_to_int(self):
        """Float value 7.9 is converted to int 7."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 5})
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(7.9)
        coord.device.set_favorite_level.assert_called_once_with(7)

    @pytest.mark.asyncio
    async def test_set_value_no_method_name(self):
        """No-op when set_fn is None."""
        desc = XiaomiMiioNumberEntityDescription(
            key="test",
            name="Test",
            set_fn=None,
            native_min_value=0,
            native_max_value=100,
        )
        coord = _make_coordinator()
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(5.0)
        # Should not raise

    @pytest.mark.asyncio
    async def test_set_value_method_not_found(self):
        """Logs error when method not found."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 5})
        delattr(coord.device, "set_favorite_level")
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        await number.async_set_native_value(10.0)
        # Should not raise

    @pytest.mark.asyncio
    async def test_set_value_exception_handling(self):
        """Exception is caught and logged."""
        desc = _get_description("favorite_level")
        coord = _make_coordinator(data={"favorite_level": 5})
        coord.device.set_favorite_level.side_effect = Exception("Device error")
        number = XiaomiMiioNumber(coord, desc)
        number.hass = coord.hass
        coord.hass.async_add_executor_job = AsyncMock(side_effect=Exception("Device error"))
        # Should not raise
        await number.async_set_native_value(10.0)


class TestNumberDescriptions:
    """Tests for number descriptions correctness."""

    def test_all_descriptions_have_key(self):
        """All descriptions have key and set_fn."""
        for desc in NUMBER_DESCRIPTIONS:
            assert desc.key
            assert desc.set_fn

    def test_favorite_level_range(self):
        """Favorite level has correct range."""
        desc = _get_description("favorite_level")
        assert desc.native_min_value == 0
        assert desc.native_max_value == 16

    def test_fan_level_range(self):
        """Fan level has correct range."""
        desc = _get_description("fan_level")
        assert desc.native_min_value == 1
        assert desc.native_max_value == 3

    def test_exists_fn_works(self):
        """exists_fn correctly checks data."""
        desc = _get_description("favorite_level")
        assert desc.exists_fn({"favorite_level": 10}) is True
        assert desc.exists_fn({"led": True}) is False
