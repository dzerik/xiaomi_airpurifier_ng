"""Tests for entity.py — XiaomiMiioEntity."""

from __future__ import annotations

from enum import Enum
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from miio import DeviceException

from custom_components.xiaomi_miio_airpurifier_ng.const import DOMAIN, SUCCESS
from custom_components.xiaomi_miio_airpurifier_ng.entity import XiaomiMiioEntity

from tests.conftest import MockDeviceInfo


def _make_coordinator(
    model="zhimi.airpurifier.mc1",
    data=None,
    mac="AA:BB:CC:DD:EE:FF",
    firmware="1.2.3",
    hardware="ESP32",
    device_info_obj=None,
):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Device"
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.available = True

    if device_info_obj is not None:
        coordinator._device_info = device_info_obj
    else:
        coordinator._device_info = MockDeviceInfo({
            "model": model,
            "mac": mac,
            "firmware": firmware,
            "hardware": hardware,
        })

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator.hass = hass
    return coordinator


class TestBuildDeviceInfo:
    """Tests for _build_device_info method."""

    def test_uses_mac_as_identifier(self):
        """Uses MAC address as primary device identifier."""
        coord = _make_coordinator(mac="AA:BB:CC:DD:EE:FF")
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert (DOMAIN, "aabbccddeeff") in info["identifiers"]

    def test_mac_fallback_to_entry_id(self):
        """Falls back to entry_id when MAC is not available."""
        device_info = MagicMock()
        device_info.mac_address = None
        device_info.firmware_version = "1.0.0"
        device_info.hardware_version = "ESP32"
        coord = _make_coordinator(device_info_obj=device_info)
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert (DOMAIN, "test_entry_id") in info["identifiers"]

    def test_mac_fallback_when_empty_mac(self):
        """Falls back to entry_id when MAC is empty string."""
        device_info = MagicMock()
        device_info.mac_address = ""
        device_info.firmware_version = "1.0.0"
        device_info.hardware_version = "ESP32"
        coord = _make_coordinator(device_info_obj=device_info)
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        # Empty MAC produces empty string identifier, which won't match entry_id
        # The mac.replace(":", "").lower() == "" which is added
        # Then identifiers has one item, so `if not identifiers` is False
        # Actually empty string MAC: identifiers = {(DOMAIN, "")} which is truthy
        # so it won't fall back. Let's check the actual behavior.
        # If mac_address is "" => bool("") is False in Python but
        # info.mac_address evaluates to "" which is falsy.
        # The code checks `if info and info.mac_address:` — empty string is falsy
        assert (DOMAIN, "test_entry_id") in info["identifiers"]

    def test_mac_fallback_when_no_device_info(self):
        """Falls back to entry_id when _device_info is None."""
        coord = _make_coordinator(device_info_obj=None)
        coord._device_info = None
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert (DOMAIN, "test_entry_id") in info["identifiers"]

    def test_model_display_name(self):
        """Uses human-readable model name when available."""
        coord = _make_coordinator(model="zhimi.airpurifier.v1")
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert info["model"] == "Mi Air Purifier"

    def test_unknown_model_uses_model_string(self):
        """Uses model string for unknown models."""
        coord = _make_coordinator(model="custom.device.v1")
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert info["model"] == "custom.device.v1"

    def test_none_model_shows_unknown(self):
        """Shows 'Unknown Model' when model is None."""
        coord = _make_coordinator(model=None)
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert info["model"] == "Unknown Model"

    def test_entry_title_used_as_name(self):
        """Uses entry title as device name."""
        coord = _make_coordinator()
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert info["name"] == "Test Device"

    def test_manufacturer_is_xiaomi(self):
        """Manufacturer is always Xiaomi."""
        coord = _make_coordinator()
        entity = XiaomiMiioEntity(coord)
        info = entity._attr_device_info
        assert info["manufacturer"] == "Xiaomi"


class TestGetFirmwareVersion:
    """Tests for _get_firmware_version method."""

    def test_returns_firmware_version(self):
        """Returns firmware version from device info."""
        coord = _make_coordinator(firmware="2.0.1")
        entity = XiaomiMiioEntity(coord)
        assert entity._get_firmware_version() == "2.0.1"

    def test_returns_none_when_no_device_info(self):
        """Returns None when _device_info is None."""
        coord = _make_coordinator()
        coord._device_info = None
        entity = XiaomiMiioEntity(coord)
        assert entity._get_firmware_version() is None


class TestGetHardwareVersion:
    """Tests for _get_hardware_version method."""

    def test_returns_hardware_version(self):
        """Returns hardware version from device info."""
        coord = _make_coordinator(hardware="ESP32-S3")
        entity = XiaomiMiioEntity(coord)
        assert entity._get_hardware_version() == "ESP32-S3"

    def test_returns_none_when_no_device_info(self):
        """Returns None when _device_info is None."""
        coord = _make_coordinator()
        coord._device_info = None
        entity = XiaomiMiioEntity(coord)
        assert entity._get_hardware_version() is None


class TestUniqueId:
    """Tests for unique ID generation."""

    def test_unique_id_with_suffix(self):
        """Unique ID includes suffix when provided."""
        coord = _make_coordinator()
        entity = XiaomiMiioEntity(coord, unique_id_suffix="aqi")
        assert entity._attr_unique_id == "test_entry_id_aqi"

    def test_unique_id_without_suffix(self):
        """Unique ID is entry_id when no suffix provided."""
        coord = _make_coordinator()
        entity = XiaomiMiioEntity(coord)
        assert entity._attr_unique_id == "test_entry_id"

    def test_unique_id_with_none_suffix(self):
        """Unique ID is entry_id when suffix is None."""
        coord = _make_coordinator()
        entity = XiaomiMiioEntity(coord, unique_id_suffix=None)
        assert entity._attr_unique_id == "test_entry_id"


class TestIsOn:
    """Tests for is_on property."""

    def test_is_on_true_when_power_on(self):
        """Returns True when power is 'on'."""
        coord = _make_coordinator(data={"power": "on"})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is True

    def test_is_on_false_when_power_off(self):
        """Returns False when power is 'off'."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is False

    def test_is_on_none_when_no_data(self):
        """Returns None when data is None."""
        coord = _make_coordinator(data=None)
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is None

    def test_is_on_none_when_no_power_key(self):
        """Returns None when power key is absent and is_on key is absent."""
        coord = _make_coordinator(data={"aqi": 42})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is None

    def test_is_on_true_when_power_is_bool_true(self):
        """Returns True when power is boolean True."""
        coord = _make_coordinator(data={"power": True})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is True

    def test_is_on_false_when_power_is_bool_false(self):
        """Returns False when power is boolean False."""
        coord = _make_coordinator(data={"power": False})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is False

    def test_is_on_from_is_on_key(self):
        """Returns True when 'is_on' key is True."""
        coord = _make_coordinator(data={"is_on": True})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is True

    def test_is_on_false_from_is_on_key(self):
        """Returns False when 'is_on' key is False."""
        coord = _make_coordinator(data={"is_on": False})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is False

    def test_power_takes_precedence_over_is_on(self):
        """Power key takes precedence over is_on key."""
        coord = _make_coordinator(data={"power": "off", "is_on": True})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is False

    def test_is_on_string_off_is_false(self):
        """Verifies that string 'off' returns False (not True via bool('off'))."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiMiioEntity(coord)
        assert entity.is_on is False


class TestExtraStateAttributes:
    """Tests for extra_state_attributes property."""

    def test_returns_empty_when_no_available_attributes(self):
        """Returns empty dict when _available_attributes is empty."""
        coord = _make_coordinator(data={"power": "on"})
        entity = XiaomiMiioEntity(coord)
        assert entity.extra_state_attributes == {}

    def test_returns_attributes_from_data(self):
        """Returns mapped attributes from coordinator data."""
        coord = _make_coordinator(data={"aqi": 42, "humidity": 55})
        entity = XiaomiMiioEntity(coord)
        entity._available_attributes = {"Air Quality": "aqi", "Humidity": "humidity"}
        entity._state_attrs = {}
        attrs = entity.extra_state_attributes
        assert attrs["Air Quality"] == 42
        assert attrs["Humidity"] == 55

    def test_skips_none_values(self):
        """Does not include attributes with None values."""
        coord = _make_coordinator(data={"aqi": 42})
        entity = XiaomiMiioEntity(coord)
        entity._available_attributes = {"Air Quality": "aqi", "Humidity": "humidity"}
        entity._state_attrs = {}
        attrs = entity.extra_state_attributes
        assert "Air Quality" in attrs
        assert "Humidity" not in attrs

    def test_handles_enum_values(self):
        """Extracts .value from Enum instances."""

        class TestMode(Enum):
            AUTO = "auto"
            MANUAL = "manual"

        coord = _make_coordinator(data={"mode": TestMode.AUTO})
        entity = XiaomiMiioEntity(coord)
        entity._available_attributes = {"Mode": "mode"}
        entity._state_attrs = {}
        attrs = entity.extra_state_attributes
        assert attrs["Mode"] == "auto"

    def test_returns_empty_when_no_data(self):
        """Returns empty attrs when coordinator data is None."""
        coord = _make_coordinator(data=None)
        entity = XiaomiMiioEntity(coord)
        entity._available_attributes = {"Air Quality": "aqi"}
        entity._state_attrs = {}
        assert entity.extra_state_attributes == {}


class TestExtractValueFromAttribute:
    """Tests for _extract_value_from_attribute static method."""

    def test_extracts_enum_value(self):
        """Returns .value for Enum instances."""

        class TestEnum(Enum):
            A = 1

        assert XiaomiMiioEntity._extract_value_from_attribute(TestEnum.A) == 1

    def test_returns_plain_value(self):
        """Returns value as-is for non-Enum types."""
        assert XiaomiMiioEntity._extract_value_from_attribute(42) == 42
        assert XiaomiMiioEntity._extract_value_from_attribute("test") == "test"
        assert XiaomiMiioEntity._extract_value_from_attribute(None) is None


class TestTryCommand:
    """Tests for _try_command method."""

    @pytest.mark.asyncio
    async def test_returns_true_on_success(self):
        """Returns True when command returns SUCCESS."""
        coord = _make_coordinator(data={})
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass

        mock_func = MagicMock(return_value=SUCCESS)
        result = await entity._try_command("Error: %s", mock_func)
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_on_non_success(self):
        """Returns False when command does not return SUCCESS."""
        coord = _make_coordinator(data={})
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass

        mock_func = MagicMock(return_value=["error"])
        result = await entity._try_command("Error: %s", mock_func)
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_device_exception(self):
        """Returns False and logs error on DeviceException."""
        coord = _make_coordinator(data={})
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass

        coord.hass.async_add_executor_job = AsyncMock(
            side_effect=DeviceException("Connection failed")
        )
        mock_func = MagicMock()
        result = await entity._try_command("Error: %s", mock_func)
        assert result is False


class TestAsyncDeviceOnOff:
    """Tests for _async_device_on and _async_device_off."""

    @pytest.mark.asyncio
    async def test_device_on_success(self):
        """Turns device on and updates state optimistically."""
        coord = _make_coordinator(data={"power": "off"})
        coord.device.on = MagicMock(return_value=SUCCESS)
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_on()

        assert coord.data["power"] == "on"
        entity.async_write_ha_state.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_device_off_success(self):
        """Turns device off and updates state optimistically."""
        coord = _make_coordinator(data={"power": "on"})
        coord.device.off = MagicMock(return_value=SUCCESS)
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_off()

        assert coord.data["power"] == "off"
        entity.async_write_ha_state.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_device_on_failure_no_state_update(self):
        """Does not update state when device.on fails."""
        coord = _make_coordinator(data={"power": "off"})
        coord.device.on = MagicMock(return_value=["error"])
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_on()

        assert coord.data["power"] == "off"  # unchanged
        entity.async_write_ha_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_device_off_failure_no_state_update(self):
        """Does not update state when device.off fails."""
        coord = _make_coordinator(data={"power": "on"})
        coord.device.off = MagicMock(return_value=["error"])
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_off()

        assert coord.data["power"] == "on"  # unchanged
        entity.async_write_ha_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_device_on_with_none_data(self):
        """Does not crash when data is None even on success."""
        coord = _make_coordinator(data=None)
        coord.device.on = MagicMock(return_value=SUCCESS)
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_on()
        # Should not crash, and should not call write_ha_state
        entity.async_write_ha_state.assert_not_called()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_device_off_with_none_data(self):
        """Does not crash when data is None even on success."""
        coord = _make_coordinator(data=None)
        coord.device.off = MagicMock(return_value=SUCCESS)
        entity = XiaomiMiioEntity(coord)
        entity.hass = coord.hass
        entity.async_write_ha_state = MagicMock()

        await entity._async_device_off()
        entity.async_write_ha_state.assert_not_called()
        coord.async_request_refresh.assert_awaited()


class TestCheckFeature:
    """Tests for _check_feature method."""

    def test_feature_supported(self):
        """Returns True when feature flag is set."""
        coord = _make_coordinator(data={})
        entity = XiaomiMiioEntity(coord)
        entity._device_features = 0b0011
        assert entity._check_feature(0b0001, "test_feature") is True

    def test_feature_not_supported(self):
        """Returns False when feature flag is not set."""
        coord = _make_coordinator(data={})
        entity = XiaomiMiioEntity(coord)
        entity._device_features = 0b0010
        assert entity._check_feature(0b0001, "test_feature") is False


class TestAvailable:
    """Tests for available property."""

    def test_available_true(self):
        """Returns True when coordinator is available and parent is available."""
        coord = _make_coordinator(data={})
        coord.available = True
        entity = XiaomiMiioEntity(coord)
        # Parent CoordinatorEntity.available checks coordinator.last_update_success
        coord.last_update_success = True
        # We mock super().available
        with patch.object(type(entity).__mro__[2], "available", new_callable=lambda: property(lambda self: True)):
            assert entity.available is True

    def test_available_false_when_coordinator_unavailable(self):
        """Returns False when coordinator.available is False."""
        coord = _make_coordinator(data={})
        coord.available = False
        entity = XiaomiMiioEntity(coord)
        with patch.object(type(entity).__mro__[2], "available", new_callable=lambda: property(lambda self: True)):
            assert entity.available is False
