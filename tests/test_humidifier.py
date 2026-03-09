"""Tests for humidifier.py — XiaomiAirHumidifier."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.humidifier import HumidifierDeviceClass, HumidifierEntityFeature

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FEATURE_FLAGS_AIRHUMIDIFIER,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA4,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQS,
    FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_V1,
)
from custom_components.xiaomi_miio_airpurifier_ng.humidifier import (
    XiaomiAirHumidifier,
)


def _make_coordinator(model="zhimi.humidifier.v1", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Humidifier"
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


class TestInit:
    """Tests for __init__ with different humidifier models."""

    def test_device_class(self):
        """Device class is HUMIDIFIER."""
        coord = _make_coordinator()
        entity = XiaomiAirHumidifier(coord)
        assert entity.device_class == HumidifierDeviceClass.HUMIDIFIER

    def test_supported_features(self):
        """Supports MODES."""
        coord = _make_coordinator()
        entity = XiaomiAirHumidifier(coord)
        assert entity.supported_features & HumidifierEntityFeature.MODES

    def test_min_max_humidity(self):
        """Min/max humidity are set."""
        coord = _make_coordinator()
        entity = XiaomiAirHumidifier(coord)
        assert entity.min_humidity == 30
        assert entity.max_humidity == 80

    def test_init_default_model(self):
        """Default humidifier (v1) sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER
        assert entity._is_miot is False
        assert entity._is_mjjsq is False
        assert entity._is_jsqs is False
        assert entity._is_jsq is False

    def test_init_ca1_model(self):
        """CA1 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA1)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_cb1_model(self):
        """CB1 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CB1)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_cb2_model(self):
        """CB2 model sets CA_AND_CB features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CB2)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB

    def test_init_ca4_model(self):
        """CA4 model sets MIOT features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_CA4
        assert entity._is_miot is True

    def test_init_mjjsq_model(self):
        """MJJSQ model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
        assert entity._is_mjjsq is True

    def test_init_jsq1_model(self):
        """JSQ1 model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ1)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
        assert entity._is_mjjsq is True

    def test_init_jsq2w_model(self):
        """JSQ2W model is JSQS type."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ2W)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
        assert entity._is_jsqs is True

    def test_init_jsq3_model(self):
        """JSQ3 model is JSQ5 type."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ3)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5

    def test_init_jsq5_model(self):
        """JSQ5 model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ5)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5

    def test_init_jsqs_model(self):
        """JSQS model sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
        assert entity._is_jsqs is True

    def test_init_jsq001_model(self):
        """JSQ001 model (shuii) sets correct features."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001)
        entity = XiaomiAirHumidifier(coord)
        assert entity._device_features == FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
        assert entity._is_jsq is True

    def test_available_modes_not_empty(self):
        """Available modes are populated."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        entity = XiaomiAirHumidifier(coord)
        assert len(entity.available_modes) > 0


class TestProperties:
    """Tests for state properties."""

    def test_is_on_power_on(self):
        """Returns True when power is 'on'."""
        coord = _make_coordinator(data={"power": "on"})
        entity = XiaomiAirHumidifier(coord)
        assert entity.is_on is True

    def test_is_on_power_off(self):
        """Returns False when power is 'off'."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiAirHumidifier(coord)
        assert entity.is_on is False

    def test_is_on_bool(self):
        """Handles boolean power values."""
        coord = _make_coordinator(data={"is_on": True})
        entity = XiaomiAirHumidifier(coord)
        assert entity.is_on is True

    def test_is_on_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        entity = XiaomiAirHumidifier(coord)
        assert entity.is_on is None

    def test_target_humidity(self):
        """Returns target humidity from data."""
        coord = _make_coordinator(data={"target_humidity": 60})
        entity = XiaomiAirHumidifier(coord)
        assert entity.target_humidity == 60

    def test_target_humidity_none(self):
        """Returns None when no target_humidity."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirHumidifier(coord)
        assert entity.target_humidity is None

    def test_target_humidity_none_no_data(self):
        """Returns None when data is None."""
        coord = _make_coordinator(data=None)
        coord.data = None
        entity = XiaomiAirHumidifier(coord)
        assert entity.target_humidity is None

    def test_current_humidity(self):
        """Returns current humidity from data."""
        coord = _make_coordinator(data={"humidity": 45})
        entity = XiaomiAirHumidifier(coord)
        assert entity.current_humidity == 45

    def test_current_humidity_none(self):
        """Returns None when no humidity."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirHumidifier(coord)
        assert entity.current_humidity is None

    def test_mode_from_data(self):
        """Returns mode from coordinator data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        entity = XiaomiAirHumidifier(coord)
        assert entity.mode == "Auto"

    def test_mode_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        entity = XiaomiAirHumidifier(coord)
        assert entity.mode is None

    def test_mode_none_when_empty(self):
        """Returns None when mode is empty."""
        coord = _make_coordinator(data={"mode": ""})
        entity = XiaomiAirHumidifier(coord)
        assert entity.mode is None


class TestTurnOnOff:
    """Tests for async_turn_on / async_turn_off."""

    @pytest.mark.asyncio
    async def test_turn_on(self):
        """Turn on calls device.on()."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_turn_on()
        coord.device.on.assert_called_once()
        coord.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_turn_off(self):
        """Turn off calls device.off()."""
        coord = _make_coordinator(data={"power": "on"})
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_turn_off()
        coord.device.off.assert_called_once()
        coord.async_request_refresh.assert_awaited_once()


class TestSetHumidity:
    """Tests for async_set_humidity."""

    @pytest.mark.asyncio
    async def test_set_humidity(self):
        """Sets target humidity on device."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_humidity(55)
        coord.device.set_target_humidity.assert_called_once_with(55)

    @pytest.mark.asyncio
    async def test_set_humidity_refreshes(self):
        """Refreshes coordinator after setting humidity."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_humidity(60)
        coord.async_request_refresh.assert_awaited_once()


class TestSetMode:
    """Tests for async_set_mode."""

    @pytest.mark.asyncio
    async def test_set_mode_miot(self):
        """MIOT model uses AirhumidifierMiotOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_mode_mjjsq(self):
        """MJJSQ model uses AirhumidifierMjjsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_mode("Low")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_mode_jsqs(self):
        """JSQS model uses AirhumidifierJsqsOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        mode = entity.available_modes[0]
        await entity.async_set_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_mode_jsq(self):
        """JSQ001 model uses AirhumidifierJsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        mode = entity.available_modes[0]
        await entity.async_set_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_mode_legacy(self):
        """Legacy model uses AirhumidifierOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_V1)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        mode = entity.available_modes[0]
        await entity.async_set_mode(mode)
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_mode("NonexistentMode")
        coord.device.set_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_mode_refreshes(self):
        """Refreshes coordinator after setting mode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4)
        entity = XiaomiAirHumidifier(coord)
        entity.hass = coord.hass
        await entity.async_set_mode("Auto")
        coord.async_request_refresh.assert_awaited()


class TestExtraStateAttributes:
    """Tests for extra_state_attributes."""

    def test_extra_attrs_from_data(self):
        """Returns attributes matching available_attributes."""
        coord = _make_coordinator(
            model=MODEL_AIRHUMIDIFIER_CA4,
            data={"humidity": 45, "target_humidity": 60, "temperature": 22.5, "buzzer": False},
        )
        entity = XiaomiAirHumidifier(coord)
        attrs = entity.extra_state_attributes
        assert "humidity" in attrs
        assert "temperature" in attrs

    def test_extra_attrs_none_values_when_no_data(self):
        """Returns attrs with None values when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        entity = XiaomiAirHumidifier(coord)
        attrs = entity.extra_state_attributes
        assert all(v is None for v in attrs.values())
