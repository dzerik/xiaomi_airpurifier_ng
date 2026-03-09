"""Button platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

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
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio buttons from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    entities: list[XiaomiMiioButton] = []

    # Create buttons based on device model
    model = coordinator.model
    for description in BUTTON_DESCRIPTIONS:
        if description.exists_fn is None or description.exists_fn(model):
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
        """Handle the button press."""
        device = self.coordinator.device
        method_name = self.entity_description.press_fn

        try:
            method = getattr(device, method_name, None)
            if method:
                await self.hass.async_add_executor_job(method)
                await self.coordinator.async_request_refresh()
                _LOGGER.debug(
                    "Successfully pressed button %s", self.entity_description.key
                )
            else:
                _LOGGER.error(
                    "Method %s not found on device for button %s",
                    method_name,
                    self.entity_description.key,
                )
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error(
                "Failed to press button %s: %s",
                self.entity_description.key,
                ex,
            )
