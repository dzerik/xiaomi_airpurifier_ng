"""Select platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XiaomiMiioDataUpdateCoordinator
from .device_profiles import get_device_profile
from .entity import XiaomiMiioEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioSelectEntityDescription(SelectEntityDescription):
    """Describes Xiaomi Miio select entity."""

    value_fn: Callable[[dict[str, Any]], str | None] | None = None
    exists_fn: Callable[[dict[str, Any]], bool] | None = None
    set_fn: str | None = None  # Method name to call on device
    options_map: dict[str, Any] | None = None  # Map display option to device value


# LED Brightness options
LED_BRIGHTNESS_OPTIONS = ["bright", "dim", "off"]
LED_BRIGHTNESS_MAP = {"bright": 0, "dim": 1, "off": 2}

# Display Orientation options (for Air Fresh T2017)
DISPLAY_ORIENTATION_OPTIONS = ["forward", "left", "right"]

# PTC Level options (for Air Fresh T2017)
PTC_LEVEL_OPTIONS = ["low", "medium", "high"]


# Select descriptions
SELECT_DESCRIPTIONS: tuple[XiaomiMiioSelectEntityDescription, ...] = (
    XiaomiMiioSelectEntityDescription(
        key="led_brightness",
        translation_key="led_brightness",
        name="LED Brightness",
        icon="mdi:brightness-6",
        options=LED_BRIGHTNESS_OPTIONS,
        value_fn=lambda data: _get_led_brightness_option(data.get("led_brightness")),
        exists_fn=lambda data: "led_brightness" in data,
        set_fn="set_led_brightness",
        options_map=LED_BRIGHTNESS_MAP,
    ),
    XiaomiMiioSelectEntityDescription(
        key="display_orientation",
        translation_key="display_orientation",
        name="Display Orientation",
        icon="mdi:rotate-3d-variant",
        options=DISPLAY_ORIENTATION_OPTIONS,
        value_fn=lambda data: _normalize_option(data.get("display_orientation")),
        exists_fn=lambda data: "display_orientation" in data,
        set_fn="set_display_orientation",
    ),
    XiaomiMiioSelectEntityDescription(
        key="ptc_level",
        translation_key="ptc_level",
        name="PTC Level",
        icon="mdi:radiator",
        options=PTC_LEVEL_OPTIONS,
        value_fn=lambda data: _normalize_option(data.get("ptc_level")),
        exists_fn=lambda data: "ptc_level" in data,
        set_fn="set_ptc_level",
    ),
)


def _get_led_brightness_option(value: Any) -> str | None:
    """Convert LED brightness value to option string."""
    if value is None:
        return None
    # Handle enum or string value
    value_str = str(value).lower()
    if "bright" in value_str and "dim" not in value_str:
        return "bright"
    if "dim" in value_str:
        return "dim"
    if "off" in value_str:
        return "off"
    # Handle numeric value
    try:
        numeric = int(value)
        return {0: "bright", 1: "dim", 2: "off"}.get(numeric)
    except ValueError, TypeError:
        return None


def _normalize_option(value: Any) -> str | None:
    """Normalize option value to lowercase string."""
    if value is None:
        return None
    return str(value).lower()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio select entities from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    # Wait for first data
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    known_keys: set[str] = set()

    @callback
    def _async_discover_selects() -> None:
        """Discover select entities based on coordinator data."""
        new_entities: list[SelectEntity] = []
        for description in SELECT_DESCRIPTIONS:
            if description.key in known_keys:
                continue
            if description.exists_fn and coordinator.data:
                if (
                    description.exists_fn(coordinator.data)
                    and description.set_fn in get_device_profile(coordinator.model).commands
                ):
                    known_keys.add(description.key)
                    new_entities.append(XiaomiMiioSelect(coordinator, description))

        # Mode select (special case — not description-based)
        if "mode_select" not in known_keys and coordinator.data and "mode" in coordinator.data:
            mode_select = XiaomiMiioModeSelect(coordinator)
            if mode_select._attr_options:
                known_keys.add("mode_select")
                new_entities.append(mode_select)

        if new_entities:
            async_add_entities(new_entities)

    _async_discover_selects()
    entry.async_on_unload(coordinator.async_add_listener(_async_discover_selects))


class XiaomiMiioSelect(XiaomiMiioEntity, SelectEntity):
    """Representation of a Xiaomi Miio select entity."""

    entity_description: XiaomiMiioSelectEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description
        self._attr_options = list(description.options) if description.options else []

    @property
    def current_option(self) -> str | None:
        """Decode the actual driver's enum, including reversed LED scales."""
        key = self.entity_description.key
        value = (self.coordinator.data or {}).get(key)
        enum = self.profile.select_enums.get(key)
        if value is None or enum is None:
            return None
        if isinstance(value, enum):
            selected = value
        else:
            raw = str(value).rsplit(".", 1)[-1]
            selected = next(
                (
                    item
                    for item in enum
                    if item.name.lower() == raw.lower() or str(item.value) == raw
                ),
                None,
            )
        if selected is None:
            return None
        if key == "led_brightness":
            return {
                "Bright": "bright",
                "High": "bright",
                "Dim": "dim",
                "Low": "dim",
                "Off": "off",
            }.get(selected.name)
        if key == "display_orientation":
            return {"Portrait": "forward", "LandscapeLeft": "left", "LandscapeRight": "right"}.get(
                selected.name
            )
        return selected.name.lower()

    async def async_select_option(self, option: str) -> None:
        """Encode options into the enum required by this driver."""
        from homeassistant.exceptions import ServiceValidationError

        key = self.entity_description.key
        enum = self.profile.select_enums.get(key)
        if option not in self.options or enum is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        aliases = {
            "led_brightness": {
                "bright": ("Bright", "High"),
                "dim": ("Dim", "Low"),
                "off": ("Off",),
            },
            "display_orientation": {
                "forward": ("Portrait",),
                "left": ("LandscapeLeft",),
                "right": ("LandscapeRight",),
            },
        }
        names = aliases.get(key, {}).get(option, (option.title(),))
        selected = next((enum[name] for name in names if name in enum.__members__), None)
        if selected is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        await self._async_command(self.entity_description.set_fn or "", selected)


class XiaomiMiioModeSelect(XiaomiMiioEntity, SelectEntity):
    """Optional humidifier mode control using the same profile as its main entity."""

    _attr_translation_key = "mode"
    _attr_icon = "mdi:tune"

    def __init__(self, coordinator: XiaomiMiioDataUpdateCoordinator) -> None:
        super().__init__(coordinator, unique_id_suffix="mode_select")
        self._mode_enum = self._get_mode_enum()
        self._attr_options = self._get_mode_options()

    def _get_mode_enum(self) -> type[Enum] | None:
        from .const import DeviceCategory

        return (
            self.profile.mode_enum if self.profile.category is DeviceCategory.HUMIDIFIER else None
        )

    def _get_mode_options(self) -> list[str]:
        return [name.lower() for name in self.profile.preset_modes] if self._mode_enum else []

    @property
    def current_option(self) -> str | None:
        mode = (self.coordinator.data or {}).get("mode")
        return mode.lower() if isinstance(mode, str) and mode.lower() in self.options else None

    async def async_select_option(self, option: str) -> None:
        from homeassistant.exceptions import ServiceValidationError

        if option not in self.options or self._mode_enum is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_value")
        selected = next(mode for mode in self._mode_enum if mode.name.lower() == option)
        await self._async_command("set_mode", selected)
