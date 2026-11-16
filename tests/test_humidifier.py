"""Tests for humidifier.py — XiaomiAirHumidifier."""

from __future__ import annotations

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_V1,
)
from custom_components.xiaomi_miio_airpurifier_ng.humidifier import (
    XiaomiAirHumidifier,
)


def _make_coordinator(model="zhimi.humidifier.v1", data=None):
    """Use real orchestration with a bounded driver mock."""
    from tests.device_helpers import make_coordinator

    return make_coordinator(model=model, data=data)


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
        assert entity.mode == "auto"

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
        coord.device.set_target_humidity.assert_called_once_with(60)

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
        with pytest.raises(ServiceValidationError):
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
