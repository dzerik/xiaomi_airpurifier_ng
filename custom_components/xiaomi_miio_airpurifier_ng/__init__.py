"""Support for Xiaomi Air Purifier NG Integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from miio import (
    AirDogX3,
    AirFresh,
    AirFreshA1,
    AirFreshT2017,
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierJsqs,
    AirHumidifierMiot,
    AirHumidifierMjjsq,
    AirPurifier,
    AirPurifierMiot,
    Device,
    DeviceException,
    Fan,
    Fan1C,
    FanLeshow,
    FanMiot,
    FanP5,
)

from .const import (
    CONF_MODEL,
    HUMIDIFIER_MIOT,
    MODEL_AIRDEHUMIDIFIER_V1,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA2,
    MODEL_AIRFRESH_VA4,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_V1,
    MODEL_AIRPURIFIER_2H,
    MODEL_AIRPURIFIER_2S,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_AIRDOG_X5,
    MODEL_AIRPURIFIER_AIRDOG_X7SM,
    MODEL_AIRPURIFIER_M1,
    MODEL_AIRPURIFIER_M2,
    MODEL_AIRPURIFIER_MA1,
    MODEL_AIRPURIFIER_MA2,
    MODEL_AIRPURIFIER_PRO,
    MODEL_AIRPURIFIER_PRO_V7,
    MODEL_AIRPURIFIER_SA1,
    MODEL_AIRPURIFIER_SA2,
    MODEL_AIRPURIFIER_V1,
    MODEL_AIRPURIFIER_V2,
    MODEL_AIRPURIFIER_V3,
    MODEL_AIRPURIFIER_V5,
    MODEL_FAN_1C,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_P5,
    MODEL_FAN_P8,
    MODEL_FAN_P9,
    MODEL_FAN_P10,
    MODEL_FAN_P11,
    MODEL_FAN_P18,
    MODEL_FAN_SA1,
    MODEL_FAN_V2,
    MODEL_FAN_V3,
    MODEL_FAN_ZA1,
    MODEL_FAN_ZA3,
    MODEL_FAN_ZA4,
    PURIFIER_MIOT,
    DeviceCategory,
    classify_model,
)
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

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Xiaomi Miio component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: XiaomiMiioConfigEntry) -> bool:
    """Set up Xiaomi Miio from a config entry."""
    host = entry.data[CONF_HOST]
    token = entry.data[CONF_TOKEN]
    model = entry.data.get(CONF_MODEL)

    _LOGGER.debug("Setting up Xiaomi Miio device at %s with model %s", host, model)

    # Create the appropriate device instance based on model
    try:
        device = await hass.async_add_executor_job(_create_device, host, token, model)
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
    """Create the appropriate device instance based on model."""
    # Air Purifier models
    if model in PURIFIER_MIOT:
        return AirPurifierMiot(ip=host, token=token, model=model)
    if model in (
        MODEL_AIRPURIFIER_V1,
        MODEL_AIRPURIFIER_V2,
        MODEL_AIRPURIFIER_V3,
        MODEL_AIRPURIFIER_V5,
        MODEL_AIRPURIFIER_PRO,
        MODEL_AIRPURIFIER_PRO_V7,
        MODEL_AIRPURIFIER_M1,
        MODEL_AIRPURIFIER_M2,
        MODEL_AIRPURIFIER_MA1,
        MODEL_AIRPURIFIER_MA2,
        MODEL_AIRPURIFIER_SA1,
        MODEL_AIRPURIFIER_SA2,
        MODEL_AIRPURIFIER_2S,
        MODEL_AIRPURIFIER_2H,
    ):
        return AirPurifier(ip=host, token=token, model=model)

    # AirDog models
    if model in (
        MODEL_AIRPURIFIER_AIRDOG_X3,
        MODEL_AIRPURIFIER_AIRDOG_X5,
        MODEL_AIRPURIFIER_AIRDOG_X7SM,
    ):
        return AirDogX3(ip=host, token=token, model=model)

    # Air Humidifier models
    if model in HUMIDIFIER_MIOT:
        return AirHumidifierMiot(ip=host, token=token, model=model)
    if model in (
        MODEL_AIRHUMIDIFIER_V1,
        MODEL_AIRHUMIDIFIER_CA1,
        MODEL_AIRHUMIDIFIER_CB1,
        MODEL_AIRHUMIDIFIER_CB2,
    ):
        return AirHumidifier(ip=host, token=token, model=model)
    if model in (
        MODEL_AIRHUMIDIFIER_MJJSQ,
        MODEL_AIRHUMIDIFIER_JSQ,
        MODEL_AIRHUMIDIFIER_JSQ1,
    ):
        return AirHumidifierMjjsq(ip=host, token=token, model=model)
    if model in (
        MODEL_AIRHUMIDIFIER_JSQ2W,
        MODEL_AIRHUMIDIFIER_JSQ3,
        MODEL_AIRHUMIDIFIER_JSQ5,
        MODEL_AIRHUMIDIFIER_JSQS,
    ):
        return AirHumidifierJsqs(ip=host, token=token, model=model)
    if model == MODEL_AIRHUMIDIFIER_JSQ001:
        return AirHumidifierJsq(ip=host, token=token, model=model)

    # Air Fresh models
    if model == MODEL_AIRFRESH_A1:
        return AirFreshA1(ip=host, token=token, model=model)
    if model in (MODEL_AIRFRESH_VA2, MODEL_AIRFRESH_VA4):
        return AirFresh(ip=host, token=token, model=model)
    if model == MODEL_AIRFRESH_T2017:
        return AirFreshT2017(ip=host, token=token, model=model)

    # Fan models
    if model in (MODEL_FAN_1C, MODEL_FAN_P8):
        return Fan1C(ip=host, token=token, model=model)
    if model == MODEL_FAN_P5:
        return FanP5(ip=host, token=token, model=model)
    if model in (
        MODEL_FAN_P9,
        MODEL_FAN_P10,
        MODEL_FAN_P11,
        MODEL_FAN_P18,
    ):
        return FanMiot(ip=host, token=token, model=model)
    if model == MODEL_FAN_LESHOW_SS4:
        return FanLeshow(ip=host, token=token, model=model)
    if model in (
        MODEL_FAN_V2,
        MODEL_FAN_V3,
        MODEL_FAN_SA1,
        MODEL_FAN_ZA1,
        MODEL_FAN_ZA3,
        MODEL_FAN_ZA4,
    ):
        return Fan(ip=host, token=token, model=model)

    # Air Dehumidifier
    if model == MODEL_AIRDEHUMIDIFIER_V1:
        from miio import AirDehumidifier

        return AirDehumidifier(ip=host, token=token, model=model)

    # Default: Try generic device, let it auto-detect
    return Device(ip=host, token=token, model=model)


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
