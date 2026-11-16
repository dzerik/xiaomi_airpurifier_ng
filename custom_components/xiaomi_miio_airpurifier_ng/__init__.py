"""Support for Xiaomi Air Purifier NG Integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from miio import Device, DeviceException

from .const import CONF_MODEL, DeviceCategory, classify_model
from .const import (
    DOMAIN as DOMAIN,
)
from .coordinator import (
    XiaomiAirDehumidifierCoordinator,
    XiaomiAirFreshCoordinator,
    XiaomiAirHumidifierCoordinator,
    XiaomiAirPurifierCoordinator,
    XiaomiFanCoordinator,
    XiaomiMiioDataUpdateCoordinator,
)
from .device_profiles import UnsupportedModelError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

type XiaomiMiioConfigEntry = ConfigEntry[XiaomiMiioDataUpdateCoordinator]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: XiaomiMiioConfigEntry) -> bool:
    """Set up Xiaomi Miio from a config entry."""
    host = entry.data[CONF_HOST]
    token = entry.data[CONF_TOKEN]
    model = entry.data.get(CONF_MODEL)

    _LOGGER.debug("Setting up Xiaomi Miio device at %s with model %s", host, model)

    # Create the appropriate device instance based on model
    try:
        device = await hass.async_add_executor_job(_create_device, host, token, model)
    except UnsupportedModelError as ex:
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="unsupported_model"
        ) from ex
    except DeviceException as ex:
        raise ConfigEntryNotReady(f"Unable to connect to device: {ex}") from ex

    # Create the appropriate coordinator based on device type
    coordinator = _create_coordinator(hass, entry, device, model)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in runtime_data
    entry.runtime_data = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: XiaomiMiioConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _create_device(host: str, token: str, model: str | None) -> Device:
    """Create a device only from its explicit protocol profile."""
    from .device_profiles import create_device

    return create_device(host, token, model)


_COORDINATOR_MAP = {
    DeviceCategory.PURIFIER: XiaomiAirPurifierCoordinator,
    DeviceCategory.HUMIDIFIER: XiaomiAirHumidifierCoordinator,
    DeviceCategory.AIR_FRESH: XiaomiAirFreshCoordinator,
    DeviceCategory.FAN: XiaomiFanCoordinator,
    DeviceCategory.DEHUMIDIFIER: XiaomiAirDehumidifierCoordinator,
}


def _create_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: Device,
    model: str | None,
) -> XiaomiMiioDataUpdateCoordinator:
    """Create the appropriate coordinator based on device type."""
    category = classify_model(model)
    coordinator_cls = _COORDINATOR_MAP.get(category, XiaomiMiioDataUpdateCoordinator)
    return coordinator_cls(hass, entry, device)
