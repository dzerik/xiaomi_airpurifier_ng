"""Fixtures for Xiaomi Air Purifier NG tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_TOKEN

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture
def mock_config_entry_data() -> dict:
    """Return mock config entry data."""
    return {
        CONF_HOST: "192.168.1.100",
        CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        CONF_MODEL: "zhimi.airpurifier.mc1",
    }


@pytest.fixture
def mock_device_info() -> dict:
    """Return mock device info."""
    return {
        "model": "zhimi.airpurifier.mc1",
        "mac": "AA:BB:CC:DD:EE:FF",
        "firmware": "1.2.3",
        "hardware": "ESP32",
    }


class MockDeviceInfo:
    """Mock device info object."""

    def __init__(self, data: dict) -> None:
        """Initialize mock device info."""
        self._data = data

    @property
    def model(self) -> str:
        """Return model."""
        return self._data.get("model", "zhimi.airpurifier.mc1")

    @property
    def mac_address(self) -> str:
        """Return MAC address."""
        return self._data.get("mac", "AA:BB:CC:DD:EE:FF")

    @property
    def firmware_version(self) -> str:
        """Return firmware version."""
        return self._data.get("firmware", "1.2.3")

    @property
    def hardware_version(self) -> str:
        """Return hardware version."""
        return self._data.get("hardware", "ESP32")


@pytest.fixture
def mock_device(mock_device_info: dict) -> Generator[MagicMock, None, None]:
    """Return a mocked Device."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device"
    ) as mock:
        device = mock.return_value
        device.info.return_value = MockDeviceInfo(mock_device_info)
        yield mock


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.async_setup_entry",
        return_value=True,
    ) as mock:
        yield mock


@pytest.fixture
def mock_air_purifier() -> Generator[MagicMock, None, None]:
    """Return a mocked AirPurifier device."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.coordinator.AirPurifier"
    ) as mock:
        device = mock.return_value
        device.status.return_value = MagicMock(
            power="on",
            aqi=42,
            average_aqi=40,
            humidity=55,
            temperature=24.5,
            mode="auto",
            favorite_level=10,
            filter_life_remaining=85,
            filter_hours_used=120,
            led=True,
            led_brightness="bright",
            buzzer=False,
            child_lock=False,
            motor_speed=800,
        )
        yield mock


@pytest.fixture
def mock_air_purifier_miot() -> Generator[MagicMock, None, None]:
    """Return a mocked AirPurifierMiot device."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.coordinator.AirPurifierMiot"
    ) as mock:
        device = mock.return_value
        device.status.return_value = MagicMock(
            power="on",
            aqi=35,
            humidity=50,
            temperature=23.0,
            mode="auto",
            favorite_level=8,
            filter_life_remaining=90,
            filter_hours_used=80,
            led=True,
            led_brightness="bright",
            buzzer=True,
            child_lock=False,
            motor_speed=650,
            fan_level=2,
        )
        yield mock
