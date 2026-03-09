"""Tests for Xiaomi Air Purifier NG integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Air Purifier",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "zhimi.airpurifier.mc1",
        },
        unique_id="aabbccddeeff",
    )


def _create_mock_coordinator(mock_device_info_data=None):
    """Create a mock coordinator."""
    from tests.conftest import MockDeviceInfo

    mock_coordinator = MagicMock()
    mock_coordinator.data = {"power": "on", "aqi": 42}
    mock_coordinator.last_update_success = True
    mock_coordinator.model = "zhimi.airpurifier.mc1"
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()
    mock_coordinator._device_info = MockDeviceInfo(
        mock_device_info_data
        or {
            "model": "zhimi.airpurifier.mc1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "firmware": "1.2.3",
            "hardware": "ESP32",
        }
    )
    return mock_coordinator


async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test successful setup of config entry."""
    # Mock device
    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.aqi = 42
    mock_device.status = MagicMock(return_value=mock_status)

    mock_coordinator = _create_mock_coordinator()
    mock_coordinator.config_entry = mock_config_entry

    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_device",
        return_value=mock_device,
    ), patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_coordinator",
        return_value=mock_coordinator,
    ):
        mock_config_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED


async def test_setup_entry_device_not_ready(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup entry when device is not ready."""
    from homeassistant.exceptions import ConfigEntryNotReady

    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_device"
    ) as mock_create, patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_coordinator"
    ) as mock_coord:
        mock_coord.side_effect = ConfigEntryNotReady("Device offline")

        mock_config_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test unloading config entry."""
    # Mock device
    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.aqi = 42
    mock_device.status = MagicMock(return_value=mock_status)

    mock_coordinator = _create_mock_coordinator()
    mock_coordinator.config_entry = mock_config_entry

    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_device",
        return_value=mock_device,
    ), patch(
        "custom_components.xiaomi_miio_airpurifier_ng._create_coordinator",
        return_value=mock_coordinator,
    ):
        mock_config_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED

        # Unload
        await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_entry_unsupported_model(
    hass: HomeAssistant,
) -> None:
    """Test setup entry with unsupported model."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Unsupported Device",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: "unsupported.model.xxx",
        },
        unique_id="aabbccddeeff",
    )

    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Should fail setup for unsupported model
    assert entry.state is ConfigEntryState.SETUP_ERROR
