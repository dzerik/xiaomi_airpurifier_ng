"""Tests for select.py — XiaomiMiioSelect and XiaomiMiioModeSelect."""

from __future__ import annotations

import pytest
from homeassistant.exceptions import ServiceValidationError
from miio.integrations.airpurifier.dmaker.airfresh_t2017 import DisplayOrientation
from miio.integrations.airpurifier.zhimi.airpurifier import LedBrightness

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
)
from custom_components.xiaomi_miio_airpurifier_ng.select import (
    LED_BRIGHTNESS_OPTIONS,
    SELECT_DESCRIPTIONS,
    XiaomiMiioModeSelect,
    XiaomiMiioSelect,
    XiaomiMiioSelectEntityDescription,
    _get_led_brightness_option,
    _normalize_option,
)


def _make_coordinator(model="zhimi.airpurifier.mc1", data=None):
    """Use real orchestration with a bounded driver mock."""
    from tests.device_helpers import make_coordinator

    return make_coordinator(model=model, data=data)


def _get_description(key: str) -> XiaomiMiioSelectEntityDescription:
    """Get a select description by key."""
    for desc in SELECT_DESCRIPTIONS:
        if desc.key == key:
            return desc
    raise ValueError(f"No select description with key={key}")


class TestGetLedBrightnessOption:
    """Tests for _get_led_brightness_option helper."""

    def test_none_returns_none(self):
        """None value returns None."""
        assert _get_led_brightness_option(None) is None

    def test_bright_string(self):
        """String with 'Bright' returns 'bright'."""
        assert _get_led_brightness_option("Bright") == "bright"

    def test_dim_string(self):
        """String with 'Dim' returns 'dim'."""
        assert _get_led_brightness_option("Dim") == "dim"

    def test_off_string(self):
        """String with 'Off' returns 'off'."""
        assert _get_led_brightness_option("Off") == "off"

    def test_numeric_0(self):
        """Numeric 0 returns 'bright'."""
        assert _get_led_brightness_option(0) == "bright"

    def test_numeric_1(self):
        """Numeric 1 returns 'dim'."""
        assert _get_led_brightness_option(1) == "dim"

    def test_numeric_2(self):
        """Numeric 2 returns 'off'."""
        assert _get_led_brightness_option(2) == "off"

    def test_invalid_string(self):
        """Invalid string with non-numeric value returns None."""
        assert _get_led_brightness_option("unknown") is None

    def test_numeric_99(self):
        """Invalid numeric returns None."""
        assert _get_led_brightness_option(99) is None


class TestNormalizeOption:
    """Tests for _normalize_option helper."""

    def test_none_returns_none(self):
        """None returns None."""
        assert _normalize_option(None) is None

    def test_string_lowered(self):
        """String is lowercased."""
        assert _normalize_option("Forward") == "forward"

    def test_numeric_to_string(self):
        """Number is converted to string."""
        assert _normalize_option(42) == "42"


class TestXiaomiMiioSelect:
    """Tests for XiaomiMiioSelect entity."""

    def test_current_option_led_brightness(self):
        """Returns LED brightness option from data."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator(data={"led_brightness": 0})
        select = XiaomiMiioSelect(coord, desc)
        assert select.current_option == "bright"

    def test_current_option_none_when_no_data(self):
        """Returns None when no data."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator(data=None)
        coord.data = None
        select = XiaomiMiioSelect(coord, desc)
        assert select.current_option is None

    def test_options_set_from_description(self):
        """Options are set from description."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator()
        select = XiaomiMiioSelect(coord, desc)
        assert select._attr_options == LED_BRIGHTNESS_OPTIONS

    @pytest.mark.asyncio
    async def test_select_option_led_brightness(self):
        """Selecting LED brightness calls set_led_brightness with mapped value."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator(data={"led_brightness": 0})
        select = XiaomiMiioSelect(coord, desc)
        select.hass = coord.hass
        await select.async_select_option("dim")
        coord.device.set_led_brightness.assert_called_once_with(
            LedBrightness.Dim
        )  # LED_BRIGHTNESS_MAP["dim"]
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_select_option_off(self):
        """Selecting 'off' calls with mapped value 2."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator(data={"led_brightness": 0})
        select = XiaomiMiioSelect(coord, desc)
        select.hass = coord.hass
        await select.async_select_option("off")
        coord.device.set_led_brightness.assert_called_once_with(LedBrightness.Off)

    @pytest.mark.asyncio
    async def test_select_option_no_method_name(self):
        """No-op when set_fn is None."""
        desc = XiaomiMiioSelectEntityDescription(
            key="test",
            name="Test",
            set_fn=None,
            options=["a", "b"],
        )
        coord = _make_coordinator()
        select = XiaomiMiioSelect(coord, desc)
        select.hass = coord.hass
        with pytest.raises(ServiceValidationError):
            await select.async_select_option("a")
        # Should not raise

    @pytest.mark.asyncio
    async def test_select_option_method_not_found(self):
        """Logs error when method not found."""
        desc = _get_description("led_brightness")
        coord = _make_coordinator(data={"led_brightness": 0})
        # Remove the method
        delattr(coord.device, "set_led_brightness")
        select = XiaomiMiioSelect(coord, desc)
        select.hass = coord.hass
        with pytest.raises(ServiceValidationError):
            await select.async_select_option("bright")
        # Should not raise

    @pytest.mark.asyncio
    async def test_select_option_without_options_map(self):
        """Option passed directly when no options_map."""
        desc = _get_description("display_orientation")
        coord = _make_coordinator(
            model="dmaker.airfresh.t2017", data={"display_orientation": "forward"}
        )
        select = XiaomiMiioSelect(coord, desc)
        select.hass = coord.hass
        await select.async_select_option("left")
        coord.device.set_display_orientation.assert_called_once_with(
            DisplayOrientation.LandscapeLeft
        )


class TestXiaomiMiioModeSelect:
    """Tests for XiaomiMiioModeSelect entity."""

    def test_init_jsqs_model(self):
        """JSQS model gets JsqsOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None
        assert len(select._attr_options) > 0

    def test_init_ca4_model(self):
        """CA4 model gets MiotOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA4, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None

    def test_init_jsq001_model(self):
        """JSQ001 model gets JsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQ001, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None

    def test_init_mjjsq_model(self):
        """MJJSQ model gets MjjsqOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_MJJSQ, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None

    def test_init_ca1_model(self):
        """CA1 model gets ZhimiOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_CA1, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None

    def test_init_zhimi_humidifier_model(self):
        """Generic zhimi.humidifier model gets ZhimiOperationMode."""
        coord = _make_coordinator(model="zhimi.humidifier.v1", data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select._mode_enum is not None

    def test_current_option(self):
        """Returns current mode from data."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        assert select.current_option == "auto"

    def test_current_option_none(self):
        """Returns None when no data."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS, data=None)
        coord.data = None
        select = XiaomiMiioModeSelect(coord)
        assert select.current_option is None

    @pytest.mark.asyncio
    async def test_select_option_valid(self):
        """Valid option calls set_mode with enum."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        select.hass = coord.hass
        valid_option = select._attr_options[0]
        await select.async_select_option(valid_option)
        coord.device.set_mode.assert_called_once()
        coord.async_request_refresh.assert_awaited()

    @pytest.mark.asyncio
    async def test_select_option_invalid(self):
        """Invalid option does not call set_mode."""
        coord = _make_coordinator(model=MODEL_AIRHUMIDIFIER_JSQS, data={"mode": "Auto"})
        select = XiaomiMiioModeSelect(coord)
        select.hass = coord.hass
        with pytest.raises(ServiceValidationError):
            await select.async_select_option("NonexistentMode")
        coord.device.set_mode.assert_not_called()
