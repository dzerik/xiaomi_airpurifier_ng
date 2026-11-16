"""Button platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XiaomiMiioDataUpdateCoordinator
from .entity import XiaomiMiioEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class XiaomiMiioButtonEntityDescription(ButtonEntityDescription):
    """Describes Xiaomi Miio button entity."""

    press_fn: str  # Method name to call on device
    exists_fn: Callable[[str | None], bool] | None = None  # Check if button should exist for model


def _is_air_purifier(model: str | None) -> bool:
    """Check if model is an air purifier."""
    if not model:
        return False
    return model.startswith("zhimi.airpurifier") or model.startswith("airdog.airpurifier")


def _is_humidifier(model: str | None) -> bool:
    """Check if model is a humidifier."""
    if not model:
        return False
    return (
        model.startswith("zhimi.humidifier")
        or model.startswith("deerma.humidifier")
        or model.startswith("shuii.humidifier")
    )


def _is_air_fresh(model: str | None) -> bool:
    """Check if model is an air fresh device."""
    if not model:
        return False
    return model.startswith("zhimi.airfresh") or model.startswith("dmaker.airfresh")


# Button descriptions
BUTTON_DESCRIPTIONS: tuple[XiaomiMiioButtonEntityDescription, ...] = (
    XiaomiMiioButtonEntityDescription(
        key="reset_filter",
        translation_key="reset_filter",
        name="Reset Filter",
        icon="mdi:air-filter",
        press_fn="reset_filter",
        exists_fn=lambda model: _is_air_purifier(model) or _is_air_fresh(model),
    ),
    XiaomiMiioButtonEntityDescription(
        key="filters_cleaned",
        translation_key="filters_cleaned",
        name="Mark Filters Cleaned",
        icon="mdi:check-circle",
        press_fn="set_filters_cleaned",
        exists_fn=_is_humidifier,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create only maintenance commands implemented by this model."""
    from .device_profiles import get_device_profile

    coordinator = entry.runtime_data
    profile = get_device_profile(coordinator.model)
    entities = []
    seen = set()
    for description in BUTTON_DESCRIPTIONS:
        command = description.press_fn
        target = profile.command_aliases.get(command, command)
        if command in profile.commands and target not in seen:
            seen.add(target)
            entities.append(XiaomiMiioButton(coordinator, description))
    async_add_entities(entities)


class XiaomiMiioButton(XiaomiMiioEntity, ButtonEntity):
    """Representation of a Xiaomi Miio button."""

    entity_description: XiaomiMiioButtonEntityDescription

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        description: XiaomiMiioButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, unique_id_suffix=description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Execute a supported maintenance command."""
        await self._async_command(self.entity_description.press_fn)
