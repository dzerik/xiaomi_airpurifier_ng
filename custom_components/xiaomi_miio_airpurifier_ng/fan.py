"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""

from __future__ import annotations

import logging

from homeassistant.components.fan import FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    HUMIDIFIER_MIOT,
    PURIFIER_MIOT,
)
from .coordinator import XiaomiMiioDataUpdateCoordinator
from .fans import (
    XiaomiAirFreshFan,
    XiaomiAirHumidifierFan,
    XiaomiAirPurifierFan,
    XiaomiGenericFan,
    XiaomiStandingFan,
)

_LOGGER = logging.getLogger(__name__)


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

    # Create fan entity based on model type
    if model:
        if model in PURIFIER_MIOT or model.startswith("zhimi.airpurifier."):
            entities.append(XiaomiAirPurifierFan(coordinator))
        elif model in HUMIDIFIER_MIOT or model.startswith("zhimi.humidifier."):
            entities.append(XiaomiAirHumidifierFan(coordinator))
        elif model.startswith("deerma.humidifier.") or model.startswith("shuii.humidifier."):
            entities.append(XiaomiAirHumidifierFan(coordinator))
        elif model.startswith("zhimi.airfresh.") or model.startswith("dmaker.airfresh."):
            entities.append(XiaomiAirFreshFan(coordinator))
        elif model.startswith("zhimi.fan.") or model.startswith("dmaker.fan.") or model.startswith("leshow.fan."):
            entities.append(XiaomiStandingFan(coordinator))
        elif model.startswith("airdog.airpurifier."):
            entities.append(XiaomiAirPurifierFan(coordinator))
        else:
            _LOGGER.warning("Unknown model %s, creating generic fan entity", model)
            entities.append(XiaomiGenericFan(coordinator))

    async_add_entities(entities)
