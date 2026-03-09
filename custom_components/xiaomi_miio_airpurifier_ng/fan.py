"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components.fan import FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)

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

    # Register entity services
    platform = async_get_current_platform()

    # No-argument services
    no_arg_services = {
        "fan_set_buzzer_on": "async_set_buzzer_on",
        "fan_set_buzzer_off": "async_set_buzzer_off",
        "fan_set_led_on": "async_set_led_on",
        "fan_set_led_off": "async_set_led_off",
        "fan_set_child_lock_on": "async_set_child_lock_on",
        "fan_set_child_lock_off": "async_set_child_lock_off",
        "fan_set_auto_detect_on": "async_set_auto_detect_on",
        "fan_set_auto_detect_off": "async_set_auto_detect_off",
        "fan_set_learn_mode_on": "async_set_learn_mode_on",
        "fan_set_learn_mode_off": "async_set_learn_mode_off",
        "fan_reset_filter": "async_reset_filter",
        "fan_set_dry_on": "async_set_dry_on",
        "fan_set_dry_off": "async_set_dry_off",
        "fan_set_filters_cleaned": "async_set_filters_cleaned",
        "fan_set_clean_mode_on": "async_set_clean_mode_on",
        "fan_set_clean_mode_off": "async_set_clean_mode_off",
        "fan_set_wet_protection_on": "async_set_wet_protection_on",
        "fan_set_wet_protection_off": "async_set_wet_protection_off",
        "fan_set_display_on": "async_set_display_on",
        "fan_set_display_off": "async_set_display_off",
        "fan_set_ptc_on": "async_set_ptc_on",
        "fan_set_ptc_off": "async_set_ptc_off",
        "fan_set_natural_mode_on": "async_set_natural_mode_on",
        "fan_set_natural_mode_off": "async_set_natural_mode_off",
    }
    for service_name, method_name in no_arg_services.items():
        platform.async_register_entity_service(service_name, {}, method_name)

    # Parameterized services
    platform.async_register_entity_service(
        "fan_set_favorite_level",
        {vol.Required("level"): vol.All(vol.Coerce(int), vol.Range(min=0, max=16))},
        "async_set_favorite_level",
    )
    platform.async_register_entity_service(
        "fan_set_fan_level",
        {vol.Required("level"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3))},
        "async_set_fan_level",
    )
    platform.async_register_entity_service(
        "fan_set_led_brightness",
        {vol.Required("brightness"): vol.All(vol.Coerce(int), vol.Range(min=0, max=2))},
        "async_set_led_brightness",
    )
    platform.async_register_entity_service(
        "fan_set_volume",
        {vol.Required("volume"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100))},
        "async_set_volume",
    )
    platform.async_register_entity_service(
        "fan_set_extra_features",
        {vol.Required("features"): vol.All(vol.Coerce(int), vol.Range(min=0, max=1))},
        "async_set_extra_features",
    )
    platform.async_register_entity_service(
        "fan_set_target_humidity",
        {vol.Required("humidity"): vol.All(vol.Coerce(int), vol.Range(min=30, max=80))},
        "async_set_target_humidity",
    )
    platform.async_register_entity_service(
        "fan_set_motor_speed",
        {vol.Required("motor_speed"): vol.All(vol.Coerce(int), vol.Range(min=200, max=2000))},
        "async_set_motor_speed",
    )
    platform.async_register_entity_service(
        "fan_set_favorite_speed",
        {vol.Required("speed"): vol.All(vol.Coerce(int), vol.Range(min=60, max=300))},
        "async_set_favorite_speed",
    )
    platform.async_register_entity_service(
        "fan_set_ptc_level",
        {vol.Required("level"): vol.In(["Low", "Medium", "High"])},
        "async_set_ptc_level",
    )
    platform.async_register_entity_service(
        "fan_set_display_orientation",
        {
            vol.Required("display_orientation"): vol.In(
                ["Portrait", "LandscapeLeft", "LandscapeRight"]
            )
        },
        "async_set_display_orientation",
    )
    platform.async_register_entity_service(
        "fan_set_delay_off",
        {vol.Required("delay_off_countdown"): vol.All(vol.Coerce(int), vol.Range(min=0, max=480))},
        "async_set_delay_off",
    )
    platform.async_register_entity_service(
        "fan_set_oscillation_angle",
        {vol.Required("angle"): vol.All(vol.Coerce(int), vol.In([30, 60, 90, 120]))},
        "async_set_oscillation_angle",
    )
