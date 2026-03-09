"""Tests for climates/dehumidifier.py — XiaomiAirDehumidifierClimate."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from miio.airdehumidifier import (
    FanSpeed as AirdehumidifierFanSpeed,
)
from miio.airdehumidifier import (
    OperationMode as AirdehumidifierOperationMode,
)

from custom_components.xiaomi_miio_airpurifier_ng.climates.dehumidifier import (
    XiaomiAirDehumidifierClimate,
)
from custom_components.xiaomi_miio_airpurifier_ng.const import (
    ATTR_MODEL,
)


def _make_coordinator(model="nwt.derh.wdh318efw1", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Dehumidifier"
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
    """Tests for __init__."""

    def test_init_sets_attributes(self):
        """Init sets correct attributes."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity._attr_min_humidity == 40
        assert entity._attr_max_humidity == 60
        assert HVACMode.OFF in entity._attr_hvac_modes
        assert HVACMode.DRY in entity._attr_hvac_modes

    def test_init_sets_preset_modes(self):
        """Init sets preset and fan modes."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        assert len(entity._attr_preset_modes) > 0
        assert len(entity._attr_fan_modes) > 0

    def test_init_model_in_state_attrs(self):
        """Model is in state attributes."""
        coord = _make_coordinator(model="nwt.derh.wdh318efw1")
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity._state_attrs[ATTR_MODEL] == "nwt.derh.wdh318efw1"


class TestHvacMode:
    """Tests for hvac_mode property."""

    def test_hvac_mode_on(self):
        """Power='on' returns DRY."""
        coord = _make_coordinator(data={"power": "on"})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.DRY

    def test_hvac_mode_off(self):
        """Power='off' returns OFF."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.OFF

    def test_hvac_mode_bool_true(self):
        """Power=True returns DRY."""
        coord = _make_coordinator(data={"power": True})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.DRY

    def test_hvac_mode_bool_false(self):
        """Power=False returns OFF."""
        coord = _make_coordinator(data={"power": False})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.OFF

    def test_hvac_mode_no_power(self):
        """No power key returns OFF."""
        coord = _make_coordinator(data={"humidity": 50})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.OFF

    def test_hvac_mode_no_data(self):
        """No data returns OFF."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.hvac_mode == HVACMode.OFF


class TestCurrentHumidity:
    """Tests for current_humidity property."""

    def test_current_humidity(self):
        """Returns humidity from data."""
        coord = _make_coordinator(data={"humidity": 55})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.current_humidity == 55

    def test_current_humidity_none(self):
        """Returns None when no humidity."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.current_humidity is None

    def test_current_humidity_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.current_humidity is None


class TestTargetHumidity:
    """Tests for target_humidity property."""

    def test_target_humidity(self):
        """Returns target humidity from data."""
        coord = _make_coordinator(data={"target_humidity": 50})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.target_humidity == 50

    def test_target_humidity_none(self):
        """Returns None when no target humidity."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.target_humidity is None


class TestPresetMode:
    """Tests for preset_mode property."""

    def test_preset_mode_valid(self):
        """Returns mode name for valid enum value."""
        mode = AirdehumidifierOperationMode.Auto
        coord = _make_coordinator(data={"mode": mode.value})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.preset_mode == "Auto"

    def test_preset_mode_none(self):
        """Returns None when no mode data."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.preset_mode is None

    def test_preset_mode_invalid_value(self):
        """Returns None for invalid mode value."""
        coord = _make_coordinator(data={"mode": 999})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.preset_mode is None


class TestFanMode:
    """Tests for fan_mode property."""

    def test_fan_mode_valid(self):
        """Returns fan speed name for valid value."""
        speed = AirdehumidifierFanSpeed.Low
        coord = _make_coordinator(data={"fan_speed": speed.value})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.fan_mode == "Low"

    def test_fan_mode_none(self):
        """Returns None when no fan speed data."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.fan_mode is None

    def test_fan_mode_invalid_value(self):
        """Returns None for invalid fan speed value."""
        coord = _make_coordinator(data={"fan_speed": 999})
        entity = XiaomiAirDehumidifierClimate(coord)
        assert entity.fan_mode is None


class TestSupportedFeatures:
    """Tests for supported_features property."""

    def test_features_when_off(self):
        """When OFF, only TURN_ON and TURN_OFF."""
        coord = _make_coordinator(data={"power": "off"})
        entity = XiaomiAirDehumidifierClimate(coord)
        features = entity.supported_features
        assert features & ClimateEntityFeature.TURN_OFF
        assert features & ClimateEntityFeature.TURN_ON
        assert not (features & ClimateEntityFeature.PRESET_MODE)

    def test_features_when_on_auto_mode(self):
        """When ON in Auto mode, supports TARGET_HUMIDITY and FAN_MODE."""
        mode = AirdehumidifierOperationMode.Auto
        coord = _make_coordinator(data={"power": "on", "mode": mode.name})
        entity = XiaomiAirDehumidifierClimate(coord)
        features = entity.supported_features
        assert features & ClimateEntityFeature.PRESET_MODE
        assert features & ClimateEntityFeature.TARGET_HUMIDITY
        assert features & ClimateEntityFeature.FAN_MODE

    def test_features_when_on_drycloth_mode(self):
        """When ON in DryCloth mode, no FAN_MODE."""
        mode = AirdehumidifierOperationMode.DryCloth
        coord = _make_coordinator(data={"power": "on", "mode": mode.name})
        entity = XiaomiAirDehumidifierClimate(coord)
        features = entity.supported_features
        assert features & ClimateEntityFeature.PRESET_MODE
        assert not (features & ClimateEntityFeature.FAN_MODE)


class TestSetHvacMode:
    """Tests for async_set_hvac_mode."""

    @pytest.mark.asyncio
    async def test_set_hvac_mode_dry(self):
        """Setting DRY turns device on."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_hvac_mode(HVACMode.DRY)
        coord.device.on.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_hvac_mode_off(self):
        """Setting OFF turns device off."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_hvac_mode(HVACMode.OFF)
        coord.device.off.assert_called_once()


class TestSetHumidity:
    """Tests for async_set_humidity."""

    @pytest.mark.asyncio
    async def test_set_humidity_rounds_to_10(self):
        """Humidity rounded to nearest 10."""
        mode = AirdehumidifierOperationMode.Auto
        coord = _make_coordinator(data={"power": "on", "mode": mode.value})
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_humidity(47)
        coord.device.set_target_humidity.assert_called_once_with(50)

    @pytest.mark.asyncio
    async def test_set_humidity_43_rounds_to_40(self):
        """43 rounds to 40."""
        mode = AirdehumidifierOperationMode.Auto
        coord = _make_coordinator(data={"power": "on", "mode": mode.value})
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_humidity(43)
        coord.device.set_target_humidity.assert_called_once_with(40)

    @pytest.mark.asyncio
    async def test_set_humidity_switches_to_auto(self):
        """Switches to Auto mode if not in Auto."""
        mode = AirdehumidifierOperationMode.DryCloth
        coord = _make_coordinator(data={"power": "on", "mode": mode.value})
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_humidity(50)
        # set_mode should be called for switching to Auto
        coord.device.set_mode.assert_called_once_with(AirdehumidifierOperationMode.Auto)
        coord.device.set_target_humidity.assert_called_once_with(50)


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_valid(self):
        """Valid mode calls set_mode."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once_with(AirdehumidifierOperationMode.Auto)

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_preset_mode("InvalidMode")
        coord.device.set_mode.assert_not_called()


class TestSetFanMode:
    """Tests for async_set_fan_mode."""

    @pytest.mark.asyncio
    async def test_set_fan_mode_valid(self):
        """Valid fan mode calls set_fan_speed."""
        coord = _make_coordinator(
            data={"power": "on", "mode": AirdehumidifierOperationMode.Auto.value}
        )
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_fan_mode("Low")
        coord.device.set_fan_speed.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_fan_mode_drycloth_noop(self):
        """Fan mode cannot be changed in DryCloth mode."""
        coord = _make_coordinator(
            data={"power": "on", "mode": AirdehumidifierOperationMode.DryCloth.value}
        )
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_fan_mode("Low")
        coord.device.set_fan_speed.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_fan_mode_invalid(self):
        """Invalid fan mode does not call device."""
        coord = _make_coordinator(
            data={"power": "on", "mode": AirdehumidifierOperationMode.Auto.value}
        )
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_fan_mode("InvalidFanMode")
        coord.device.set_fan_speed.assert_not_called()


class TestTurnOnOff:
    """Tests for turn on/off."""

    @pytest.mark.asyncio
    async def test_turn_on(self):
        """Turn on calls set_hvac_mode(DRY)."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_turn_on()
        coord.device.on.assert_called_once()

    @pytest.mark.asyncio
    async def test_turn_off(self):
        """Turn off calls set_hvac_mode(OFF)."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_turn_off()
        coord.device.off.assert_called_once()


class TestServiceMethods:
    """Tests for service methods (buzzer, LED, child lock)."""

    @pytest.mark.asyncio
    async def test_set_buzzer_on(self):
        """Buzzer on called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_buzzer_on()
        coord.device.set_buzzer.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_buzzer_off(self):
        """Buzzer off called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_buzzer_off()
        coord.device.set_buzzer.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_set_led_on(self):
        """LED on called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_led_on()
        coord.device.set_led.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_led_off(self):
        """LED off called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_led_off()
        coord.device.set_led.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_set_child_lock_on(self):
        """Child lock on called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_child_lock_on()
        coord.device.set_child_lock.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_set_child_lock_off(self):
        """Child lock off called."""
        coord = _make_coordinator()
        entity = XiaomiAirDehumidifierClimate(coord)
        entity.hass = coord.hass
        await entity.async_set_child_lock_off()
        coord.device.set_child_lock.assert_called_once_with(False)


class TestExtraStateAttributes:
    """Tests for extra_state_attributes."""

    def test_extra_state_attributes_with_data(self):
        """Returns state attrs with data."""
        coord = _make_coordinator(data={"humidity": 55, "temperature": 25})
        entity = XiaomiAirDehumidifierClimate(coord)
        attrs = entity.extra_state_attributes
        assert ATTR_MODEL in attrs

    def test_extra_state_attributes_empty_data(self):
        """Returns state attrs with empty data."""
        coord = _make_coordinator(data={})
        entity = XiaomiAirDehumidifierClimate(coord)
        attrs = entity.extra_state_attributes
        assert ATTR_MODEL in attrs
