"""Tests for Xiaomi Air Purifier NG integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaomi_miio_airpurifier_ng import (
    _create_coordinator,
    _create_device,
)
from custom_components.xiaomi_miio_airpurifier_ng.const import (
    CONF_MODEL,
    DOMAIN,
    MODEL_AIRDEHUMIDIFIER_V1,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA2,
    MODEL_AIRFRESH_VA4,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_V1,
    MODEL_AIRPURIFIER_2S,
    MODEL_AIRPURIFIER_3,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_V1,
    MODEL_FAN_1C,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_P5,
    MODEL_FAN_P9,
    MODEL_FAN_V2,
)


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
    mock_coordinator.device_info_raw = MockDeviceInfo(
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

    with (
        patch(
            "custom_components.xiaomi_miio_airpurifier_ng._create_device",
            return_value=mock_device,
        ),
        patch(
            "custom_components.xiaomi_miio_airpurifier_ng._create_coordinator",
            return_value=mock_coordinator,
        ),
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

    with (
        patch("custom_components.xiaomi_miio_airpurifier_ng._create_device"),
        patch("custom_components.xiaomi_miio_airpurifier_ng._create_coordinator") as mock_coord,
    ):
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

    with (
        patch(
            "custom_components.xiaomi_miio_airpurifier_ng._create_device",
            return_value=mock_device,
        ),
        patch(
            "custom_components.xiaomi_miio_airpurifier_ng._create_coordinator",
            return_value=mock_coordinator,
        ),
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


# ---------------------------------------------------------------------------
# Tests for _create_device — all model branches
# ---------------------------------------------------------------------------


class TestCreateDevice:
    """Tests for _create_device function covering all model branches."""

    def test_purifier_miot_model(self):
        """PURIFIER_MIOT model creates AirPurifierMiot."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRPURIFIER_3
        )
        from miio import AirPurifierMiot

        assert isinstance(device, AirPurifierMiot)

    def test_purifier_legacy_model(self):
        """Legacy purifier model creates AirPurifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRPURIFIER_V1
        )
        from miio import AirPurifier

        assert isinstance(device, AirPurifier)

    def test_purifier_2s_model(self):
        """2S purifier model creates AirPurifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRPURIFIER_2S
        )
        from miio import AirPurifier

        assert isinstance(device, AirPurifier)

    def test_airdog_model(self):
        """AirDog model creates AirDogX3."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRPURIFIER_AIRDOG_X3
        )
        from miio import AirDogX3

        assert isinstance(device, AirDogX3)

    def test_humidifier_miot_model(self):
        """Humidifier MiOT model creates AirHumidifierMiot."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_CA4
        )
        from miio import AirHumidifierMiot

        assert isinstance(device, AirHumidifierMiot)

    def test_humidifier_legacy_model(self):
        """Legacy humidifier model creates AirHumidifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_V1
        )
        from miio import AirHumidifier

        assert isinstance(device, AirHumidifier)

    def test_humidifier_ca1_model(self):
        """CA1 humidifier model creates AirHumidifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_CA1
        )
        from miio import AirHumidifier

        assert isinstance(device, AirHumidifier)

    def test_humidifier_cb1_model(self):
        """CB1 humidifier model creates AirHumidifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_CB1
        )
        from miio import AirHumidifier

        assert isinstance(device, AirHumidifier)

    def test_humidifier_mjjsq_model(self):
        """MJJSQ humidifier model creates AirHumidifierMjjsq."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_MJJSQ
        )
        from miio import AirHumidifierMjjsq

        assert isinstance(device, AirHumidifierMjjsq)

    def test_humidifier_jsq_model(self):
        """JSQ humidifier model creates AirHumidifierMjjsq."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_JSQ
        )
        from miio import AirHumidifierMjjsq

        assert isinstance(device, AirHumidifierMjjsq)

    def test_humidifier_jsqs_model(self):
        """JSQS humidifier model creates AirHumidifierJsqs."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_JSQS
        )
        from miio import AirHumidifierJsqs

        assert isinstance(device, AirHumidifierJsqs)

    def test_humidifier_jsq2w_model(self):
        """JSQ2W humidifier model creates AirHumidifierJsqs."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_JSQ2W
        )
        from miio import AirHumidifierJsqs

        assert isinstance(device, AirHumidifierJsqs)

    def test_humidifier_jsq001_model(self):
        """JSQ001 humidifier model creates AirHumidifierJsq."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRHUMIDIFIER_JSQ001
        )
        from miio import AirHumidifierJsq

        assert isinstance(device, AirHumidifierJsq)

    def test_airfresh_a1_model(self):
        """Air Fresh A1 model creates AirFreshA1."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRFRESH_A1
        )
        from miio import AirFreshA1

        assert isinstance(device, AirFreshA1)

    def test_airfresh_va2_model(self):
        """Air Fresh VA2 model creates AirFresh."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRFRESH_VA2
        )
        from miio import AirFresh

        assert isinstance(device, AirFresh)

    def test_airfresh_va4_model(self):
        """Air Fresh VA4 model creates AirFresh."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRFRESH_VA4
        )
        from miio import AirFresh

        assert isinstance(device, AirFresh)

    def test_airfresh_t2017_model(self):
        """Air Fresh T2017 model creates AirFreshT2017."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRFRESH_T2017
        )
        from miio import AirFreshT2017

        assert isinstance(device, AirFreshT2017)

    def test_fan_1c_model(self):
        """Fan 1C model creates Fan1C."""
        device = _create_device("192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_FAN_1C)
        from miio import Fan1C

        assert isinstance(device, Fan1C)

    def test_fan_p5_model(self):
        """Fan P5 model creates FanP5."""
        device = _create_device("192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_FAN_P5)
        from miio import FanP5

        assert isinstance(device, FanP5)

    def test_fan_p9_miot_model(self):
        """Fan P9 MiOT model creates FanMiot."""
        device = _create_device("192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_FAN_P9)
        from miio import FanMiot

        assert isinstance(device, FanMiot)

    def test_fan_leshow_model(self):
        """Leshow fan model creates FanLeshow."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_FAN_LESHOW_SS4
        )
        from miio import FanLeshow

        assert isinstance(device, FanLeshow)

    def test_fan_legacy_model(self):
        """Legacy fan model creates Fan."""
        device = _create_device("192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_FAN_V2)
        from miio import Fan

        assert isinstance(device, Fan)

    def test_dehumidifier_model(self):
        """Dehumidifier model creates AirDehumidifier."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", MODEL_AIRDEHUMIDIFIER_V1
        )
        from miio import AirDehumidifier

        assert isinstance(device, AirDehumidifier)

    def test_unknown_model_creates_generic_device(self):
        """Unknown model falls back to generic Device."""
        device = _create_device(
            "192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", "unknown.model.v1"
        )
        from miio import Device

        assert isinstance(device, Device)

    def test_none_model_creates_generic_device(self):
        """None model falls back to generic Device."""
        device = _create_device("192.168.1.1", "aaaabbbbccccddddaaaabbbbccccdddd", None)
        from miio import Device

        assert isinstance(device, Device)


# ---------------------------------------------------------------------------
# Tests for _create_coordinator — all device categories
# ---------------------------------------------------------------------------


class TestCreateCoordinator:
    """Tests for _create_coordinator function."""

    @staticmethod
    def _make_entry(model="zhimi.airpurifier.mc1"):
        """Create a mock config entry with proper data for coordinator."""
        entry = MagicMock()
        entry.data = {
            CONF_HOST: "192.168.1.100",
            CONF_TOKEN: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            CONF_MODEL: model,
        }
        entry.options = {}
        entry.entry_id = "test_entry_id"
        entry.async_on_unload = MagicMock()
        entry.add_update_listener = MagicMock()
        return entry

    def test_purifier_coordinator(self):
        """Purifier model creates XiaomiAirPurifierCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiAirPurifierCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry("zhimi.airpurifier.mc1")
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, "zhimi.airpurifier.mc1")
        assert isinstance(coord, XiaomiAirPurifierCoordinator)

    def test_humidifier_coordinator(self):
        """Humidifier model creates XiaomiAirHumidifierCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiAirHumidifierCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry("zhimi.humidifier.ca4")
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, "zhimi.humidifier.ca4")
        assert isinstance(coord, XiaomiAirHumidifierCoordinator)

    def test_air_fresh_coordinator(self):
        """Air fresh model creates XiaomiAirFreshCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiAirFreshCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry("zhimi.airfresh.va2")
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, "zhimi.airfresh.va2")
        assert isinstance(coord, XiaomiAirFreshCoordinator)

    def test_fan_coordinator(self):
        """Fan model creates XiaomiFanCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiFanCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry("dmaker.fan.p5")
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, "dmaker.fan.p5")
        assert isinstance(coord, XiaomiFanCoordinator)

    def test_dehumidifier_coordinator(self):
        """Dehumidifier model creates XiaomiAirDehumidifierCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiAirDehumidifierCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry(MODEL_AIRDEHUMIDIFIER_V1)
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, MODEL_AIRDEHUMIDIFIER_V1)
        assert isinstance(coord, XiaomiAirDehumidifierCoordinator)

    def test_unknown_model_coordinator(self):
        """Unknown model creates base XiaomiMiioDataUpdateCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiMiioDataUpdateCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry("unknown.model.v1")
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, "unknown.model.v1")
        assert isinstance(coord, XiaomiMiioDataUpdateCoordinator)

    def test_none_model_coordinator(self):
        """None model creates base XiaomiMiioDataUpdateCoordinator."""
        from custom_components.xiaomi_miio_airpurifier_ng.coordinator import (
            XiaomiMiioDataUpdateCoordinator,
        )

        hass = MagicMock()
        entry = self._make_entry(None)
        device = MagicMock()
        coord = _create_coordinator(hass, entry, device, None)
        assert isinstance(coord, XiaomiMiioDataUpdateCoordinator)
