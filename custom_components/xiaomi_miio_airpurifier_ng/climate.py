"""Support for Xiaomi Mi Air Dehumidifier."""

from __future__ import annotations

import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)

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

    # Register climate entity services
    platform = async_get_current_platform()

    climate_services = {
        "xiaomi_miio_set_buzzer_on": "async_set_buzzer_on",
        "xiaomi_miio_set_buzzer_off": "async_set_buzzer_off",
        "xiaomi_miio_set_led_on": "async_set_led_on",
        "xiaomi_miio_set_led_off": "async_set_led_off",
        "xiaomi_miio_set_child_lock_on": "async_set_child_lock_on",
        "xiaomi_miio_set_child_lock_off": "async_set_child_lock_off",
    }
    for service_name, method_name in climate_services.items():
        platform.async_register_entity_service(service_name, {}, method_name)
