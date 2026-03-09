"""Binary sensor platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XiaomiMiioDataUpdateCoordinator
from .entity import XiaomiMiioEntity


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Xiaomi Miio binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None] | None = None
    exists_fn: Callable[[dict[str, Any]], bool] | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[XiaomiMiioBinarySensorEntityDescription, ...] = (
    # Water tank installed (Jsqs models - jsqs, jsq2w, jsq5)
    # tank_filed=True means tank is installed
    XiaomiMiioBinarySensorEntityDescription(
        key="water_tank",
        translation_key="water_tank",
        name="Water Tank",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:cup-water",
        value_fn=lambda data: data.get("tank_filed"),
        exists_fn=lambda data: "tank_filed" in data,
    ),
    # Water shortage (Jsqs models)
    # water_shortage_fault=True means no water
    XiaomiMiioBinarySensorEntityDescription(
        key="water_shortage",
        translation_key="water_shortage",
        name="Water Shortage",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:water-off",
        value_fn=lambda data: data.get("water_shortage_fault"),
        exists_fn=lambda data: "water_shortage_fault" in data,
    ),
    # Water tank detached (Mjjsq models)
    # water_tank_detached=True means tank is removed
    XiaomiMiioBinarySensorEntityDescription(
        key="water_tank_detached",
        translation_key="water_tank_detached",
        name="Water Tank Detached",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:cup-off",
        value_fn=lambda data: data.get("water_tank_detached"),
        exists_fn=lambda data: "water_tank_detached" in data,
    ),
    # No water (Mjjsq models)
    # no_water=True means water tank is empty
    XiaomiMiioBinarySensorEntityDescription(
        key="no_water",
        translation_key="no_water",
        name="No Water",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:water-alert",
        value_fn=lambda data: data.get("no_water"),
        exists_fn=lambda data: "no_water" in data,
    ),
    # Fan - AC Power
    XiaomiMiioBinarySensorEntityDescription(
        key="ac_power",
        translation_key="ac_power",
        name="AC Power",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:power-plug",
        value_fn=lambda data: data.get("ac_power"),
        exists_fn=lambda data: "ac_power" in data,
    ),
    # Fan - Battery charging
    XiaomiMiioBinarySensorEntityDescription(
        key="battery_charge",
        translation_key="battery_charge",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: data.get("battery_charge"),
        exists_fn=lambda data: "battery_charge" in data,
    ),
    # Fan - Oscillation
    XiaomiMiioBinarySensorEntityDescription(
        key="oscillate",
        translation_key="oscillate",
        name="Oscillation",
        icon="mdi:rotate-3d-variant",
        value_fn=lambda data: data.get("oscillate"),
        exists_fn=lambda data: "oscillate" in data,
    ),
    # Air Fresh - PTC status (heater working)
    XiaomiMiioBinarySensorEntityDescription(
        key="ptc_status",
        translation_key="ptc_status",
        name="Heater Active",
        device_class=BinarySensorDeviceClass.HEAT,
        icon="mdi:radiator",
        value_fn=lambda data: data.get("ptc_status"),
        exists_fn=lambda data: "ptc_status" in data,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio binary sensors from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    entities: list[XiaomiMiioBinarySensor] = []

    # Create binary sensors based on available data
    for description in BINARY_SENSOR_DESCRIPTIONS:
        if description.exists_fn and coordinator.data:
            if description.exists_fn(coordinator.data):
                entities.append(XiaomiMiioBinarySensor(coordinator, description))

    async_add_entities(entities)


class XiaomiMiioBinarySensor(XiaomiMiioEntity, BinarySensorEntity):
    """Representation of a Xiaomi Miio binary sensor."""

    entity_description: XiaomiMiioBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
