"""Tests for Xiaomi Air Purifier NG coordinator."""

from __future__ import annotations

from enum import Enum
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from miio import DeviceException

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN
from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
    XiaomiAirFreshCoordinator,
    XiaomiAirHumidifierCoordinator,
    XiaomiAirPurifierCoordinator,
    XiaomiFanCoordinator,
    XiaomiMiioDataUpdateCoordinator,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.conftest import MockDeviceInfo


def _create_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Device",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "zhimi.airpurifier.mc1",
        },
        unique_id="aabbccddeeff",
    )


class MockMode(Enum):
    """Mock operation mode enum."""

    Auto = 0
    Silent = 1
    Favorite = 2


async def test_async_setup_caches_device_info(hass: HomeAssistant) -> None:
    """Test that _async_setup caches device info."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_info = MockDeviceInfo(
        {"model": "zhimi.airpurifier.mc1", "mac": "AA:BB:CC:DD:EE:FF", "firmware": "1.2.3", "hardware": "ESP32"}
    )
    mock_device.info.return_value = mock_info

    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)
    assert coordinator._device_info is None

    await coordinator._async_setup()

    assert coordinator._device_info is mock_info
    assert coordinator._device_info.firmware_version == "1.2.3"


async def test_async_setup_detects_model(hass: HomeAssistant) -> None:
    """Test that _async_setup detects model from device info when not set."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Device",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        },
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_info = MockDeviceInfo({"model": "zhimi.airpurifier.ma4"})
    mock_device.info.return_value = mock_info

    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)
    assert coordinator.model is None

    await coordinator._async_setup()

    assert coordinator.model == "zhimi.airpurifier.ma4"


async def test_async_update_data_device_exception(hass: HomeAssistant) -> None:
    """Test that DeviceException raises UpdateFailed."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_device.status.side_effect = DeviceException("Connection error")

    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)

    with pytest.raises(UpdateFailed, match="Error communicating with device"):
        await coordinator._async_update_data()

    assert coordinator._available is False


async def test_async_update_data_auth_error(hass: HomeAssistant) -> None:
    """Test that token errors raise ConfigEntryAuthFailed."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_device.status.side_effect = DeviceException("Unable to discover the device")

    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)

    with pytest.raises(ConfigEntryAuthFailed, match="Authentication failed"):
        await coordinator._async_update_data()


async def test_async_update_data_success(hass: HomeAssistant) -> None:
    """Test successful data update for air purifier coordinator."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.aqi = 42
    mock_status.humidity = 55
    mock_status.temperature = 24.5
    mock_status.mode = MockMode.Auto
    mock_status.led = True
    mock_status.led_brightness = MagicMock()
    mock_status.led_brightness.__str__ = lambda self: "Bright"
    mock_status.led_brightness.__bool__ = lambda self: True
    mock_status.buzzer = False
    mock_status.child_lock = False
    mock_status.favorite_level = 10
    mock_status.filter_hours_used = 120
    mock_status.filter_life_remaining = 85
    mock_status.motor_speed = 800
    mock_device.status.return_value = mock_status

    coordinator = XiaomiAirPurifierCoordinator(hass, entry, mock_device)
    data = coordinator._get_status()

    assert data["power"] == "on"
    assert data["aqi"] == 42
    assert data["humidity"] == 55
    assert data["mode"] == "Auto"
    assert data["mode_value"] == 0
    assert data["buzzer"] is False


async def test_led_brightness_zero_not_lost(hass: HomeAssistant) -> None:
    """Test that led_brightness=0 is not lost (regression test for C3)."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"

    # Create a mock enum-like brightness with value 0
    class MockBrightness:
        def __init__(self):
            self.value = 0

        def __str__(self):
            return "Bright"

        def __bool__(self):
            return False  # This is the falsy case that was previously broken

    mock_status.led_brightness = MockBrightness()
    mock_status.mode = None
    mock_status.led = True
    mock_status.buzzer = False
    mock_status.child_lock = False
    mock_device.status.return_value = mock_status

    coordinator = XiaomiAirPurifierCoordinator(hass, entry, mock_device)
    data = coordinator._get_status()

    # led_brightness should NOT be None when value is 0 (falsy but valid)
    assert data["led_brightness"] is not None
    assert data["led_brightness"] == "Bright"


async def test_mode_parsing_with_enum(hass: HomeAssistant) -> None:
    """Test _parse_mode correctly extracts name and value from enum."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)

    # Test with enum mode
    mock_status = MagicMock()
    mock_status.mode = MockMode.Silent
    data: dict = {}
    coordinator._parse_mode(mock_status, data)

    assert data["mode"] == "Silent"
    assert data["mode_value"] == 1


async def test_mode_parsing_with_none(hass: HomeAssistant) -> None:
    """Test _parse_mode handles None mode correctly."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)

    mock_status = MagicMock()
    mock_status.mode = None
    data: dict = {}
    coordinator._parse_mode(mock_status, data)

    assert data["mode"] is None
    assert data["mode_value"] is None


async def test_mode_parsing_without_mode_attr(hass: HomeAssistant) -> None:
    """Test _parse_mode does nothing when status has no mode attribute."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    coordinator = XiaomiMiioDataUpdateCoordinator(hass, entry, mock_device)

    mock_status = MagicMock(spec=[])  # No attributes at all
    data: dict = {}
    coordinator._parse_mode(mock_status, data)

    assert "mode" not in data
    assert "mode_value" not in data


async def test_humidifier_coordinator_status(hass: HomeAssistant) -> None:
    """Test humidifier coordinator extracts data correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Humidifier",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "zhimi.humidifier.ca4",
        },
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.humidity = 55
    mock_status.target_humidity = 60
    mock_status.temperature = 22.0
    mock_status.mode = MockMode.Auto
    mock_status.buzzer = True
    mock_status.child_lock = False
    mock_status.motor_speed = 400
    mock_device.status.return_value = mock_status

    coordinator = XiaomiAirHumidifierCoordinator(hass, entry, mock_device)
    data = coordinator._get_status()

    assert data["power"] == "on"
    assert data["humidity"] == 55
    assert data["target_humidity"] == 60
    assert data["mode"] == "Auto"
    assert data["buzzer"] is True


async def test_fan_coordinator_status(hass: HomeAssistant) -> None:
    """Test fan coordinator extracts data correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Fan",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "zhimi.fan.za3",
        },
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.speed = 50
    mock_status.oscillate = True
    mock_status.angle = 90
    mock_status.mode = MockMode.Favorite
    mock_status.led = False
    mock_status.buzzer = True
    mock_status.child_lock = False
    mock_device.status.return_value = mock_status

    coordinator = XiaomiFanCoordinator(hass, entry, mock_device)
    data = coordinator._get_status()

    assert data["power"] == "on"
    assert data["speed"] == 50
    assert data["oscillate"] is True
    assert data["mode"] == "Favorite"


async def test_air_fresh_coordinator_ptc_level_zero(hass: HomeAssistant) -> None:
    """Test that ptc_level=0 is not lost (similar to led_brightness C3 fix)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Air Fresh",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "dmaker.airfresh.t2017",
        },
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.mode = MockMode.Auto

    class MockPtcLevel:
        def __str__(self):
            return "Low"

        def __bool__(self):
            return False  # Falsy but valid

    mock_status.ptc_level = MockPtcLevel()
    mock_status.display_orientation = None
    mock_device.status.return_value = mock_status

    coordinator = XiaomiAirFreshCoordinator(hass, entry, mock_device)
    data = coordinator._get_status()

    assert data["ptc_level"] == "Low"
    assert data["display_orientation"] is None
