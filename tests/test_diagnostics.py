"""Tests for diagnostics."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN
from custom_components.xiaomi_miio_airpurifier_ng.diagnostics import (
    async_get_config_entry_diagnostics,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Air Purifier",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "secret_token_12345678901234567890",
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


async def test_diagnostics_redacts_token(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test diagnostics redacts sensitive data."""
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

        diagnostics = await async_get_config_entry_diagnostics(
            hass, mock_config_entry
        )

        # Token should be redacted
        assert diagnostics["entry"]["data"][CONF_TOKEN] == "**REDACTED**"

        # Host and model should not be redacted
        assert diagnostics["entry"]["data"][CONF_HOST] == "192.168.1.100"

        # Device info should be present
        assert "device_info" in diagnostics
        assert diagnostics["device_info"]["model"] == "zhimi.airpurifier.mc1"


async def test_diagnostics_includes_coordinator_data(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test diagnostics includes coordinator data."""
    # Mock device
    mock_device = MagicMock()
    mock_status = MagicMock()
    mock_status.power = "on"
    mock_status.aqi = 42
    mock_status.humidity = 55
    mock_device.status = MagicMock(return_value=mock_status)

    mock_coordinator = _create_mock_coordinator()
    mock_coordinator.config_entry = mock_config_entry
    mock_coordinator.data = {"power": "on", "aqi": 42, "humidity": 55}

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

        diagnostics = await async_get_config_entry_diagnostics(
            hass, mock_config_entry
        )

        assert "data" in diagnostics
