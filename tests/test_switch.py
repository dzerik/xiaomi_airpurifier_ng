"""Tests for switch.py — XiaomiMiioSwitch."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.switch import (
    XiaomiMiioSwitch,
    XiaomiMiioSwitchEntityDescription,
    SWITCH_DESCRIPTIONS,
)


def _make_coordinator(data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = "zhimi.airpurifier.mc1"
    coordinator.data = data or {}
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.title = "Test Device"
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


def _get_description(key: str) -> XiaomiMiioSwitchEntityDescription:
    """Get a switch description by key."""
    for desc in SWITCH_DESCRIPTIONS:
        if desc.key == key:
            return desc
    raise ValueError(f"No switch description with key={key}")


class TestIsOn:
    """Tests for is_on property."""

    def test_is_on_true(self):
        """Returns True when value_fn returns True."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"buzzer": True})
        switch = XiaomiMiioSwitch(coord, desc)
        assert switch.is_on is True

    def test_is_on_false(self):
        """Returns False when value_fn returns False."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"buzzer": False})
        switch = XiaomiMiioSwitch(coord, desc)
        assert switch.is_on is False

    def test_is_on_none_when_no_data(self):
        """Returns None when no coordinator data."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data=None)
        coord.data = None
        switch = XiaomiMiioSwitch(coord, desc)
        assert switch.is_on is None

    def test_is_on_none_when_key_missing(self):
        """Returns None when key not in data."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"led": True})
        switch = XiaomiMiioSwitch(coord, desc)
        assert switch.is_on is None

    @pytest.mark.parametrize("key", ["led", "child_lock", "dry", "ptc", "display", "oscillate"])
    def test_is_on_various_switches(self, key):
        """Various switches return correct value."""
        desc = _get_description(key)
        coord = _make_coordinator(data={key: True})
        switch = XiaomiMiioSwitch(coord, desc)
        assert switch.is_on is True


class TestTurnOnOff:
    """Tests for async_turn_on and async_turn_off."""

    @pytest.mark.asyncio
    async def test_turn_on_buzzer(self):
        """Turn on buzzer calls set_buzzer(True)."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"buzzer": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        coord.device.set_buzzer.assert_called_once_with(True)
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_turn_off_buzzer(self):
        """Turn off buzzer calls set_buzzer(False)."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"buzzer": True})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_off()
        coord.device.set_buzzer.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_turn_on_led(self):
        """Turn on LED calls set_led(True)."""
        desc = _get_description("led")
        coord = _make_coordinator(data={"led": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        coord.device.set_led.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_turn_off_child_lock(self):
        """Turn off child lock calls set_child_lock(False)."""
        desc = _get_description("child_lock")
        coord = _make_coordinator(data={"child_lock": True})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_off()
        coord.device.set_child_lock.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_turn_on_ptc(self):
        """Turn on PTC calls set_ptc(True)."""
        desc = _get_description("ptc")
        coord = _make_coordinator(data={"ptc": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        coord.device.set_ptc.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_turn_on_led_light(self):
        """Turn on LED light calls set_light(True)."""
        desc = _get_description("led_light")
        coord = _make_coordinator(data={"led_light": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        coord.device.set_light.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_turn_on_overwet_protect(self):
        """Turn on overwet protect calls set_overwet_protect(True)."""
        desc = _get_description("overwet_protect")
        coord = _make_coordinator(data={"overwet_protect": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        coord.device.set_overwet_protect.assert_called_once_with(True)


class TestMethodNotFound:
    """Tests for method not found handling."""

    @pytest.mark.asyncio
    async def test_method_not_found_logs_error(self):
        """Logs error when method not found on device."""
        desc = _get_description("buzzer")
        coord = _make_coordinator(data={"buzzer": False})
        # Remove the method from device
        coord.device.set_buzzer = None
        delattr(coord.device, "set_buzzer")
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        # Should not raise, just log
        await switch.async_turn_on()

    @pytest.mark.asyncio
    async def test_no_method_name(self):
        """No-op when method name is None."""
        desc = XiaomiMiioSwitchEntityDescription(
            key="test",
            name="Test",
            turn_on_fn=None,
            turn_off_fn=None,
        )
        coord = _make_coordinator(data={"test": False})
        switch = XiaomiMiioSwitch(coord, desc)
        switch.hass = coord.hass
        await switch.async_turn_on()
        # Should not raise


class TestSwitchDescriptions:
    """Tests for switch descriptions correctness."""

    def test_all_descriptions_have_key(self):
        """All descriptions have a key."""
        for desc in SWITCH_DESCRIPTIONS:
            assert desc.key
            assert desc.turn_on_fn
            assert desc.turn_off_fn

    def test_buzzer_description(self):
        """Buzzer description is correct."""
        desc = _get_description("buzzer")
        assert desc.turn_on_fn == "set_buzzer"
        assert desc.turn_off_fn == "set_buzzer"

    def test_exists_fn_works(self):
        """exists_fn correctly checks data."""
        desc = _get_description("buzzer")
        assert desc.exists_fn({"buzzer": True}) is True
        assert desc.exists_fn({"led": True}) is False
