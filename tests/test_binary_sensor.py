"""Tests for binary_sensor.py — XiaomiMiioBinarySensor."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
    XiaomiMiioBinarySensor,
    XiaomiMiioBinarySensorEntityDescription,
    async_setup_entry,
)


def _make_coordinator(data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = "zhimi.humidifier.ca4"
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Device"
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.device_info_raw = MagicMock()
    coordinator.device_info_raw.mac_address = "AA:BB:CC:DD:EE:FF"
    coordinator.device_info_raw.firmware_version = "1.0.0"
    coordinator.device_info_raw.hardware_version = "ESP32"
    coordinator.available = True
    coordinator.async_add_listener = MagicMock(return_value=MagicMock())
    return coordinator


def _get_description(key: str) -> XiaomiMiioBinarySensorEntityDescription:
    """Get a binary sensor description by key."""
    for desc in BINARY_SENSOR_DESCRIPTIONS:
        if desc.key == key:
            return desc
    raise ValueError(f"No binary sensor description with key={key}")


class TestIsOn:
    """Tests for is_on property."""

    def test_is_on_true_when_value_fn_returns_true(self):
        """Returns True when value_fn returns True."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator(data={"tank_filed": True})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is True

    def test_is_on_false_when_value_fn_returns_false(self):
        """Returns False when value_fn returns False."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator(data={"tank_filed": False})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is False

    def test_is_on_none_when_no_data(self):
        """Returns None when coordinator data is None."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator()
        coord.data = None
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is None

    def test_is_on_none_when_no_value_fn(self):
        """Returns None when value_fn is None."""
        desc = XiaomiMiioBinarySensorEntityDescription(
            key="test_sensor",
            name="Test",
            value_fn=None,
        )
        coord = _make_coordinator(data={"test": True})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is None

    def test_is_on_none_when_key_missing_from_data(self):
        """Returns None when key is not in data (value_fn returns None)."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator(data={"other_key": True})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is None

    @pytest.mark.parametrize(
        "key,data_key,value",
        [
            ("water_tank_removed", "water_shortage_fault", True),
            ("water_tank_detached", "water_tank_detached", True),
            ("no_water", "no_water", True),
            ("ac_power", "ac_power", True),
            ("battery_charge", "battery_charge", True),
            ("oscillate", "oscillate", True),
            ("ptc_status", "ptc_status", True),
        ],
    )
    def test_is_on_various_sensors(self, key, data_key, value):
        """Various sensors return correct value from data."""
        desc = _get_description(key)
        coord = _make_coordinator(data={data_key: value})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is True

    @pytest.mark.parametrize(
        "key,data_key",
        [
            ("water_tank_removed", "water_shortage_fault"),
            ("no_water", "no_water"),
            ("ac_power", "ac_power"),
            ("oscillate", "oscillate"),
        ],
    )
    def test_is_on_false_for_various_sensors(self, key, data_key):
        """Various sensors return False when data value is False."""
        desc = _get_description(key)
        coord = _make_coordinator(data={data_key: False})
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.is_on is False


class TestAsyncSetupEntry:
    """Tests for async_setup_entry discovery logic."""

    @pytest.mark.asyncio
    async def test_discovers_sensors_from_data(self):
        """Discovers sensors based on coordinator data keys."""
        coord = _make_coordinator(
            data={
                "tank_filed": True,
                "water_shortage_fault": False,
            }
        )
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)

        keys = [e.entity_description.key for e in added_entities]
        assert "water_level_low" in keys
        assert "water_tank_removed" in keys
        # no_water not in data, should not be discovered
        assert "no_water" not in keys

    @pytest.mark.asyncio
    async def test_no_sensors_when_no_matching_data(self):
        """Creates no sensors when data has no matching keys."""
        coord = _make_coordinator(data={"power": "on", "aqi": 42})
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)
        assert len(added_entities) == 0

    @pytest.mark.asyncio
    async def test_calls_first_refresh_when_no_data(self):
        """Calls async_config_entry_first_refresh when data is None."""
        coord = _make_coordinator()
        coord.data = None
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()

        await async_setup_entry(hass, entry, lambda e: e)
        coord.async_config_entry_first_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_does_not_refresh_when_data_present(self):
        """Does not call first_refresh when data is already present."""
        coord = _make_coordinator(data={"tank_filed": True})
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()

        await async_setup_entry(hass, entry, lambda e: e)
        coord.async_config_entry_first_refresh.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_registers_listener_for_discovery(self):
        """Registers coordinator listener for ongoing discovery."""
        coord = _make_coordinator(data={"tank_filed": True})
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()

        await async_setup_entry(hass, entry, lambda e: e)
        coord.async_add_listener.assert_called_once()
        entry.async_on_unload.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_data_dict_does_not_trigger_refresh(self):
        """Empty dict (truthy) does not trigger first_refresh."""
        coord = _make_coordinator(data={})
        # empty dict is falsy for `not coordinator.data`
        coord.data = {}
        entry = MagicMock()
        entry.runtime_data = coord
        entry.async_on_unload = MagicMock()
        hass = MagicMock()

        await async_setup_entry(hass, entry, lambda e: e)
        # Empty dict is falsy, so first_refresh IS called
        coord.async_config_entry_first_refresh.assert_awaited_once()


class TestBinarySensorInit:
    """Tests for binary sensor initialization."""

    def test_unique_id_includes_key(self):
        """Unique ID includes the sensor key as suffix."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator()
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor._attr_unique_id == f"test_entry_id_{desc.key}"

    def test_entity_description_set(self):
        """Entity description is set from constructor."""
        desc = _get_description("water_level_low")
        coord = _make_coordinator()
        sensor = XiaomiMiioBinarySensor(coord, desc)
        assert sensor.entity_description is desc


class TestBinarySensorDescriptions:
    """Tests for binary sensor descriptions correctness."""

    def test_all_descriptions_have_key(self):
        """All descriptions have a key."""
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            assert desc.key

    def test_all_descriptions_have_value_fn(self):
        """All descriptions have a value_fn."""
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            assert desc.value_fn is not None

    def test_all_descriptions_have_exists_fn(self):
        """All descriptions have an exists_fn."""
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            assert desc.exists_fn is not None

    @pytest.mark.parametrize(
        "key,data_key",
        [
            ("water_level_low", "tank_filed"),
            ("water_tank_removed", "water_shortage_fault"),
            ("water_tank_detached", "water_tank_detached"),
            ("no_water", "no_water"),
            ("ac_power", "ac_power"),
            ("battery_charge", "battery_charge"),
            ("oscillate", "oscillate"),
            ("ptc_status", "ptc_status"),
        ],
    )
    def test_exists_fn_checks_correct_key(self, key, data_key):
        """exists_fn returns True when data has the correct key."""
        desc = _get_description(key)
        assert desc.exists_fn({data_key: True}) is True
        assert desc.exists_fn({"other_key": True}) is False
