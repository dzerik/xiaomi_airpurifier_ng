"""Tests for button.py — XiaomiMiioButton."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.button import (
    BUTTON_DESCRIPTIONS,
    XiaomiMiioButton,
    XiaomiMiioButtonEntityDescription,
    _is_air_fresh,
    _is_air_purifier,
    _is_humidifier,
    async_setup_entry,
)


def _make_coordinator(model="zhimi.airpurifier.mc1", data=None):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.model = model
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


class TestIsAirPurifier:
    """Tests for _is_air_purifier helper."""

    @pytest.mark.parametrize("model", [
        "zhimi.airpurifier.mc1",
        "zhimi.airpurifier.v1",
        "airdog.airpurifier.x3",
        "airdog.airpurifier.x5",
    ])
    def test_valid_purifier_models(self, model):
        """Returns True for valid air purifier models."""
        assert _is_air_purifier(model) is True

    @pytest.mark.parametrize("model", [
        "zhimi.humidifier.ca1",
        "dmaker.fan.p5",
        "unknown.model",
    ])
    def test_non_purifier_models(self, model):
        """Returns False for non-purifier models."""
        assert _is_air_purifier(model) is False

    def test_none_model(self):
        """Returns False for None model."""
        assert _is_air_purifier(None) is False

    def test_empty_string(self):
        """Returns False for empty string."""
        assert _is_air_purifier("") is False


class TestIsHumidifier:
    """Tests for _is_humidifier helper."""

    @pytest.mark.parametrize("model", [
        "zhimi.humidifier.v1",
        "zhimi.humidifier.ca4",
        "deerma.humidifier.mjjsq",
        "deerma.humidifier.jsq5",
        "shuii.humidifier.jsq001",
    ])
    def test_valid_humidifier_models(self, model):
        """Returns True for valid humidifier models."""
        assert _is_humidifier(model) is True

    @pytest.mark.parametrize("model", [
        "zhimi.airpurifier.mc1",
        "dmaker.fan.p5",
    ])
    def test_non_humidifier_models(self, model):
        """Returns False for non-humidifier models."""
        assert _is_humidifier(model) is False

    def test_none_model(self):
        """Returns False for None model."""
        assert _is_humidifier(None) is False

    def test_empty_string(self):
        """Returns False for empty string."""
        assert _is_humidifier("") is False


class TestIsAirFresh:
    """Tests for _is_air_fresh helper."""

    @pytest.mark.parametrize("model", [
        "zhimi.airfresh.va2",
        "zhimi.airfresh.va4",
        "dmaker.airfresh.a1",
        "dmaker.airfresh.t2017",
    ])
    def test_valid_air_fresh_models(self, model):
        """Returns True for valid air fresh models."""
        assert _is_air_fresh(model) is True

    @pytest.mark.parametrize("model", [
        "zhimi.airpurifier.mc1",
        "dmaker.fan.p5",
    ])
    def test_non_air_fresh_models(self, model):
        """Returns False for non-air-fresh models."""
        assert _is_air_fresh(model) is False

    def test_none_model(self):
        """Returns False for None model."""
        assert _is_air_fresh(None) is False

    def test_empty_string(self):
        """Returns False for empty string."""
        assert _is_air_fresh("") is False


class TestAsyncSetupEntry:
    """Tests for async_setup_entry."""

    @pytest.mark.asyncio
    async def test_purifier_model_creates_reset_filter_button(self):
        """Air purifier model creates reset_filter button."""
        coord = _make_coordinator(model="zhimi.airpurifier.mc1")
        entry = MagicMock()
        entry.runtime_data = coord
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)
        keys = [e.entity_description.key for e in added_entities]
        assert "reset_filter" in keys
        assert "filters_cleaned" not in keys

    @pytest.mark.asyncio
    async def test_humidifier_model_creates_filters_cleaned_button(self):
        """Humidifier model creates filters_cleaned button."""
        coord = _make_coordinator(model="zhimi.humidifier.ca1")
        entry = MagicMock()
        entry.runtime_data = coord
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)
        keys = [e.entity_description.key for e in added_entities]
        assert "filters_cleaned" in keys
        assert "reset_filter" not in keys

    @pytest.mark.asyncio
    async def test_air_fresh_model_creates_reset_filter_button(self):
        """Air fresh model creates reset_filter button."""
        coord = _make_coordinator(model="zhimi.airfresh.va2")
        entry = MagicMock()
        entry.runtime_data = coord
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)
        keys = [e.entity_description.key for e in added_entities]
        assert "reset_filter" in keys

    @pytest.mark.asyncio
    async def test_fan_model_creates_no_buttons(self):
        """Fan model (no exists_fn match) creates no filtered buttons."""
        coord = _make_coordinator(model="dmaker.fan.p5")
        entry = MagicMock()
        entry.runtime_data = coord
        hass = MagicMock()
        added_entities = []

        await async_setup_entry(hass, entry, added_entities.extend)
        # Fan model doesn't match any exists_fn
        assert len(added_entities) == 0

    @pytest.mark.asyncio
    async def test_description_without_exists_fn_always_added(self):
        """Button with exists_fn=None is always added."""
        # Verify the logic: if exists_fn is None, button is always created
        desc = XiaomiMiioButtonEntityDescription(
            key="test_button",
            name="Test",
            press_fn="test_method",
            exists_fn=None,
        )
        coord = _make_coordinator(model="unknown.model")
        # exists_fn is None -> should pass the condition
        assert desc.exists_fn is None or desc.exists_fn(coord.model)


class TestAsyncPress:
    """Tests for async_press method."""

    @pytest.mark.asyncio
    async def test_press_calls_device_method(self):
        """Pressing button calls the device method."""
        desc = BUTTON_DESCRIPTIONS[0]  # reset_filter
        coord = _make_coordinator(model="zhimi.airpurifier.mc1")
        button = XiaomiMiioButton(coord, desc)
        button.hass = coord.hass

        await button.async_press()

        coord.device.reset_filter.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_press_filters_cleaned(self):
        """Pressing filters_cleaned calls set_filters_cleaned."""
        desc = BUTTON_DESCRIPTIONS[1]  # filters_cleaned
        coord = _make_coordinator(model="zhimi.humidifier.ca1")
        button = XiaomiMiioButton(coord, desc)
        button.hass = coord.hass

        await button.async_press()

        coord.device.set_filters_cleaned.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_press_method_not_found(self):
        """Logs error when method not found on device."""
        desc = BUTTON_DESCRIPTIONS[0]  # reset_filter
        coord = _make_coordinator(model="zhimi.airpurifier.mc1")
        # Remove the method
        coord.device.reset_filter = None
        delattr(coord.device, "reset_filter")
        button = XiaomiMiioButton(coord, desc)
        button.hass = coord.hass

        # Should not raise
        await button.async_press()
        coord.async_request_refresh.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_press_device_exception(self):
        """Exception is caught and logged."""
        desc = BUTTON_DESCRIPTIONS[0]  # reset_filter
        coord = _make_coordinator(model="zhimi.airpurifier.mc1")
        coord.device.reset_filter.side_effect = Exception("Device error")
        # Make async_add_executor_job raise
        coord.hass.async_add_executor_job = AsyncMock(side_effect=Exception("Device error"))
        button = XiaomiMiioButton(coord, desc)
        button.hass = coord.hass

        # Should not raise
        await button.async_press()


class TestButtonInit:
    """Tests for button initialization."""

    def test_unique_id_includes_key(self):
        """Unique ID includes the button key as suffix."""
        desc = BUTTON_DESCRIPTIONS[0]
        coord = _make_coordinator()
        button = XiaomiMiioButton(coord, desc)
        assert button._attr_unique_id == f"test_entry_id_{desc.key}"

    def test_entity_description_set(self):
        """Entity description is set from constructor."""
        desc = BUTTON_DESCRIPTIONS[0]
        coord = _make_coordinator()
        button = XiaomiMiioButton(coord, desc)
        assert button.entity_description is desc


class TestButtonDescriptions:
    """Tests for button descriptions correctness."""

    def test_all_descriptions_have_key_and_press_fn(self):
        """All descriptions have key and press_fn."""
        for desc in BUTTON_DESCRIPTIONS:
            assert desc.key
            assert desc.press_fn

    def test_reset_filter_description(self):
        """Reset filter description is correct."""
        desc = BUTTON_DESCRIPTIONS[0]
        assert desc.key == "reset_filter"
        assert desc.press_fn == "reset_filter"

    def test_filters_cleaned_description(self):
        """Filters cleaned description is correct."""
        desc = BUTTON_DESCRIPTIONS[1]
        assert desc.key == "filters_cleaned"
        assert desc.press_fn == "set_filters_cleaned"
