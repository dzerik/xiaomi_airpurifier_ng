"""Coordinator doubles with real command orchestration and bounded driver mocks."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from custom_components.xiaomi_miio_airpurifier_ng import _create_coordinator
from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import get_device_profile


def make_coordinator(
    model,
    data=None,
    mac="AA:BB:CC:DD:EE:FF",
    firmware="1.0.0",
    hardware="ESP32",
    device_info_obj=None,
):
    profile = get_device_profile(model)
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.unique_id = mac.replace(":", "").replace("-", "").lower() if mac else None
    entry.title = "Test Device"
    entry.data = {"host": "192.0.2.1", "token": "0" * 32, "model": model}
    entry.options = {}
    device = MagicMock(spec=profile.driver)
    for name in profile.commands:
        getattr(device, profile.command_aliases.get(name, name)).return_value = ["ok"]
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    coordinator = _create_coordinator(hass, entry, device, model)
    coordinator.data = data
    coordinator._device_info = (
        device_info_obj
        if device_info_obj is not None
        else SimpleNamespace(
            mac_address=mac, firmware_version=firmware, hardware_version=hardware, model=model
        )
    )
    coordinator.async_request_refresh = AsyncMock()
    return coordinator
