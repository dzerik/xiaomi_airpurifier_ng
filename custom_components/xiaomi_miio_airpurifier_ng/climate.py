"""Support for Xiaomi Mi Air Dehumidifier."""

from __future__ import annotations

import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .climates import XiaomiAirDehumidifierClimate
from .coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio climate from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data if not available
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    model = coordinator.model
    entities: list[ClimateEntity] = []

    # Create climate entity for dehumidifier models
    if model and model.startswith("nwt.derh."):
        entities.append(XiaomiAirDehumidifierClimate(coordinator))

    async_add_entities(entities)
