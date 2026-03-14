"""Switch platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XiaomiMiioDataUpdateCoordinator
from .entity import XiaomiMiioEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioSwitchEntityDescription(SwitchEntityDescription):
    """Describes Xiaomi Miio switch entity."""

    value_fn: Callable[[dict[str, Any]], bool | None] | None = None
    exists_fn: Callable[[dict[str, Any]], bool] | None = None
    turn_on_fn: str | None = None  # Method name to call on device
    turn_off_fn: str | None = None  # Method name to call on device


# Switch descriptions
SWITCH_DESCRIPTIONS: tuple[XiaomiMiioSwitchEntityDescription, ...] = (
    XiaomiMiioSwitchEntityDescription(
        key="buzzer",
        translation_key="buzzer",
        name="Buzzer",
        icon="mdi:volume-high",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("buzzer"),
        exists_fn=lambda data: "buzzer" in data,
        turn_on_fn="set_buzzer",
        turn_off_fn="set_buzzer",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="led",
        translation_key="led",
        name="LED",
        icon="mdi:led-on",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("led"),
        exists_fn=lambda data: "led" in data,
        turn_on_fn="set_led",
        turn_off_fn="set_led",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="child_lock",
        translation_key="child_lock",
        name="Child Lock",
        icon="mdi:lock",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("child_lock"),
        exists_fn=lambda data: "child_lock" in data,
        turn_on_fn="set_child_lock",
        turn_off_fn="set_child_lock",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="dry",
        translation_key="dry",
        name="Dry Mode",
        icon="mdi:water-off",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("dry"),
        exists_fn=lambda data: "dry" in data,
        turn_on_fn="set_dry",
        turn_off_fn="set_dry",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="learn_mode",
        translation_key="learn_mode",
        name="Learn Mode",
        icon="mdi:school",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("learn_mode"),
        exists_fn=lambda data: "learn_mode" in data,
        turn_on_fn="set_learn_mode",
        turn_off_fn="set_learn_mode",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="auto_detect",
        translation_key="auto_detect",
        name="Auto Detect",
        icon="mdi:auto-fix",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("auto_detect"),
        exists_fn=lambda data: "auto_detect" in data,
        turn_on_fn="set_auto_detect",
        turn_off_fn="set_auto_detect",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="oscillate",
        translation_key="oscillate",
        name="Oscillation",
        icon="mdi:rotate-3d-variant",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("oscillate"),
        exists_fn=lambda data: "oscillate" in data,
        turn_on_fn="set_oscillate",
        turn_off_fn="set_oscillate",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="ptc",
        translation_key="ptc",
        name="PTC Heater",
        icon="mdi:radiator",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("ptc"),
        exists_fn=lambda data: "ptc" in data,
        turn_on_fn="set_ptc",
        turn_off_fn="set_ptc",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="led_light",
        translation_key="led_light",
        name="LED Light",
        icon="mdi:led-on",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("led_light"),
        exists_fn=lambda data: "led_light" in data,
        turn_on_fn="set_light",
        turn_off_fn="set_light",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="overwet_protect",
        translation_key="overwet_protect",
        name="Overwet Protection",
        icon="mdi:water-alert",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("overwet_protect"),
        exists_fn=lambda data: "overwet_protect" in data,
        turn_on_fn="set_overwet_protect",
        turn_off_fn="set_overwet_protect",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="display",
        translation_key="display",
        name="Display",
        icon="mdi:monitor",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("display"),
        exists_fn=lambda data: "display" in data,
        turn_on_fn="set_display",
        turn_off_fn="set_display",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="anion",
        translation_key="anion",
        name="Ionizer",
        icon="mdi:atom",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("anion"),
        exists_fn=lambda data: "anion" in data,
        turn_on_fn="set_anion",
        turn_off_fn="set_anion",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="gestures",
        translation_key="gestures",
        name="Gesture Control",
        icon="mdi:gesture-tap",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("gestures"),
        exists_fn=lambda data: "gestures" in data,
        turn_on_fn="set_gestures",
        turn_off_fn="set_gestures",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="clean_mode",
        translation_key="clean_mode",
        name="Clean Mode",
        icon="mdi:shimmer",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("clean_mode"),
        exists_fn=lambda data: "clean_mode" in data,
        turn_on_fn="set_clean_mode",
        turn_off_fn="set_clean_mode",
    ),
    XiaomiMiioSwitchEntityDescription(
        key="extra_features",
        translation_key="extra_features",
        name="Extra Features",
        icon="mdi:feature-search",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.get("extra_features"),
        exists_fn=lambda data: "extra_features" in data,
        turn_on_fn="set_extra_features",
        turn_off_fn="set_extra_features",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio switches from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    known_keys: set[str] = set()

    @callback
    def _async_discover_switches() -> None:
        """Discover switches based on coordinator data."""
        new_entities: list[XiaomiMiioSwitch] = []
        for description in SWITCH_DESCRIPTIONS:
            if description.key in known_keys:
                continue
            if description.exists_fn and coordinator.data:
                if description.exists_fn(coordinator.data):
                    known_keys.add(description.key)
                    new_entities.append(XiaomiMiioSwitch(coordinator, description))
        if new_entities:
            async_add_entities(new_entities)

    _async_discover_switches()
    entry.async_on_unload(coordinator.async_add_listener(_async_discover_switches))


class XiaomiMiioSwitch(XiaomiMiioEntity, SwitchEntity):
    """Representation of a Xiaomi Miio switch."""

    entity_description: XiaomiMiioSwitchEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return True if switch is on."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_set_state(False)

    async def _async_set_state(self, state: bool) -> None:
        """Set the switch state."""
        method_name = (
            self.entity_description.turn_on_fn if state else self.entity_description.turn_off_fn
        )

        if not method_name:
            _LOGGER.warning(
                "No method defined for %s switch %s",
                "on" if state else "off",
                self.entity_description.key,
            )
            return

        method = getattr(self.coordinator.device, method_name, None)
        if not method:
            _LOGGER.error(
                "Method %s not found on device for switch %s",
                method_name,
                self.entity_description.key,
            )
            return

        await self._try_command(
            f"Setting {self.entity_description.key} of the miio device failed: %s",
            method,
            state,
        )
        await self.coordinator.async_request_refresh()
