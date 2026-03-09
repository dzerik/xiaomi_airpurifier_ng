"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""

from __future__ import annotations

import logging

from homeassistant.components.fan import FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DeviceCategory, classify_model
from .coordinator import XiaomiMiioDataUpdateCoordinator
from .fans import (
    XiaomiAirFreshFan,
    XiaomiAirHumidifierFan,
    XiaomiAirPurifierFan,
    XiaomiGenericFan,
    XiaomiStandingFan,
)

_LOGGER = logging.getLogger(__name__)

_FAN_ENTITY_MAP = {
    DeviceCategory.PURIFIER: XiaomiAirPurifierFan,
    DeviceCategory.HUMIDIFIER: XiaomiAirHumidifierFan,
    DeviceCategory.AIR_FRESH: XiaomiAirFreshFan,
    DeviceCategory.FAN: XiaomiStandingFan,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio fan from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data if not available
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    model = coordinator.model
    entities: list[FanEntity] = []

    if model:
        category = classify_model(model)
        fan_cls = _FAN_ENTITY_MAP.get(category)
        if fan_cls:
            entities.append(fan_cls(coordinator))
        elif category == DeviceCategory.UNKNOWN:
            _LOGGER.warning("Unknown model %s, creating generic fan entity", model)
            entities.append(XiaomiGenericFan(coordinator))
        # DEHUMIDIFIER category uses climate platform, no fan entity

    async_add_entities(entities)
