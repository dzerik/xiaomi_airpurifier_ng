"""Tests for fans/air_fresh.py — XiaomiAirFreshFan."""

from __future__ import annotations

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA2,
)
from custom_components.xiaomi_miio_airpurifier_ng.fans.air_fresh import (
    XiaomiAirFreshFan,
)


def _make_coordinator(model="zhimi.airfresh.va2", data=None):
    """Use real orchestration with a bounded driver mock."""
    from tests.device_helpers import make_coordinator

    return make_coordinator(model=model, data=data)


class TestPresetMode:
    """Tests for preset mode properties."""

    def test_preset_modes(self):
        """Returns preset modes list."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_modes == ["Auto", "Sleep"]

    def test_preset_mode_from_data(self):
        """Returns current mode from data."""
        coord = _make_coordinator(data={"mode": "Auto"})
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode == "Auto"

    def test_preset_mode_none_when_no_data(self):
        """Returns None when no data."""
        coord = _make_coordinator(data=None)
        coord.data = None
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode is None

    def test_preset_mode_none_when_empty(self):
        """Returns None when mode is empty."""
        coord = _make_coordinator(data={"mode": ""})
        fan = XiaomiAirFreshFan(coord)
        assert fan.preset_mode is None


class TestSetPresetMode:
    """Tests for async_set_preset_mode."""

    @pytest.mark.asyncio
    async def test_set_preset_mode_t2017(self):
        """T2017 uses AirfreshT2017OperationMode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_T2017)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_va2(self):
        """VA2 uses AirfreshOperationMode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        await fan.async_set_preset_mode("Auto")
        coord.device.set_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Invalid mode does not call set_mode."""
        coord = _make_coordinator(model=MODEL_AIRFRESH_VA2)
        fan = XiaomiAirFreshFan(coord)
        fan.hass = coord.hass
        with pytest.raises(ServiceValidationError):
            await fan.async_set_preset_mode("NonexistentMode")
        coord.device.set_mode.assert_not_called()
