"""Commands must report failures and serialize access to the shared device."""

import asyncio
from threading import Event
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from miio import DeviceException

from custom_components.xiaomi_miio_airpurifier_ng.const import DOMAIN
from custom_components.xiaomi_miio_airpurifier_ng.coordinator import XiaomiAirPurifierCoordinator
from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import create_device
from tests.ha_helpers import MockConfigEntry


@pytest.fixture
def command_coordinator(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="aabbccddeeff",
        data={"host": "192.0.2.1", "token": "0" * 32, "model": "zhimi.airpurifier.v2"},
    )
    device = create_device("192.0.2.1", "0" * 32, "zhimi.airpurifier.v2")
    device.send = Mock(return_value=["ok"])
    device.status = Mock(return_value=SimpleNamespace(power="on"))
    coordinator = XiaomiAirPurifierCoordinator(hass, entry, device)
    coordinator.async_request_refresh = AsyncMock()
    coordinator.data = {"power": "off"}
    coordinator._device_info = SimpleNamespace(
        mac_address="AA:BB:CC:DD:EE:FF", firmware_version="1", hardware_version="1"
    )
    return coordinator


@pytest.mark.parametrize("response", [["ok"], [{"did": "power", "code": 0}]])
def test_success_response(response):
    from custom_components.xiaomi_miio_airpurifier_ng.coordinator import validate_command_result

    validate_command_result(response)


@pytest.mark.parametrize(
    "response",
    [[], None, ["error"], [{"code": -4004}], [{"code": 0}, {"code": -1}], [{"code": False}]],
)
def test_rejected_response(response):
    from custom_components.xiaomi_miio_airpurifier_ng.coordinator import validate_command_result

    with pytest.raises(HomeAssistantError):
        validate_command_result(response)


async def test_command_error_reaches_caller(command_coordinator):
    command_coordinator.device.send.side_effect = DeviceException("unreachable")
    with pytest.raises(HomeAssistantError):
        await command_coordinator.async_execute_command("on")
    assert command_coordinator.data["power"] == "off"


async def test_missing_command_rejected_before_io(command_coordinator):
    with pytest.raises(ServiceValidationError):
        await command_coordinator.async_execute_command("set_arbitrary_property", 1)
    assert command_coordinator.data["power"] == "off"


async def test_success_notifies_all_entities(command_coordinator):
    changes = []
    unsubscribe = command_coordinator.async_add_listener(
        lambda: changes.append(dict(command_coordinator.data))
    )
    try:
        await command_coordinator.async_execute_command("on")
        assert changes == [{"power": "on"}]
    finally:
        unsubscribe()


@pytest.mark.parametrize("cancel_first", [False, True])
async def test_commands_do_not_overlap_even_after_cancellation(
    hass, command_coordinator, cancel_first
):
    started, release, second_entered = Event(), Event(), Event()
    calls = []

    def network(method, params):
        calls.append(method)
        if len(calls) == 1:
            started.set()
            if not release.wait(3):
                raise RuntimeError("test did not release network operation")
        else:
            second_entered.set()
        return ["ok"]

    command_coordinator.device.send.side_effect = network
    first = asyncio.create_task(command_coordinator.async_execute_command("on"))
    second = None
    try:
        assert await hass.async_add_executor_job(started.wait, 2)
        if cancel_first:
            first.cancel()
        second = asyncio.create_task(command_coordinator.async_execute_command("off"))
        await asyncio.sleep(0.03)
        assert not second_entered.is_set()
    finally:
        release.set()
        await asyncio.gather(first, *([second] if second else []), return_exceptions=True)
    assert calls == ["set_power", "set_power"]
    assert command_coordinator.data["power"] == "off"


async def test_polling_waits_for_command(hass, command_coordinator):
    started, release = Event(), Event()
    calls = []

    def network(method, params):
        calls.append("command")
        started.set()
        release.wait(3)
        return ["ok"]

    def status():
        calls.append("poll")
        return SimpleNamespace(power="on")

    command_coordinator.device.send.side_effect = network
    command_coordinator.device.status.side_effect = status
    first = asyncio.create_task(command_coordinator.async_execute_command("on"))
    second = None
    try:
        assert await hass.async_add_executor_job(started.wait, 2)
        second = asyncio.create_task(command_coordinator._async_update_data())
        await asyncio.sleep(0.03)
        assert calls == ["command"]
    finally:
        release.set()
        await asyncio.gather(first, *([second] if second else []))
    assert calls == ["command", "poll"]
