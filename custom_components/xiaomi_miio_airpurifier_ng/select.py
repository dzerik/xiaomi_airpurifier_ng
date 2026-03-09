"""Select platform for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    HUMIDIFIER_MIOT,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_MJJSQ,
)
from .coordinator import XiaomiMiioDataUpdateCoordinator
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
    except (ValueError, TypeError):
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

    entities: list[SelectEntity] = []

    # Create selects based on available data
    for description in SELECT_DESCRIPTIONS:
        if description.exists_fn and coordinator.data:
            if description.exists_fn(coordinator.data):
                entities.append(XiaomiMiioSelect(coordinator, description))

    # Create mode select if mode is available
    if coordinator.data and "mode" in coordinator.data:
        mode_select = XiaomiMiioModeSelect(coordinator)
        # Only add if we have valid mode options
        if mode_select._attr_options:
            entities.append(mode_select)

    async_add_entities(entities)


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
        """Return the current option."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        device = self.coordinator.device
        method_name = self.entity_description.set_fn

        if not method_name:
            _LOGGER.warning(
                "No method defined for setting %s",
                self.entity_description.key,
            )
            return

        try:
            method = getattr(device, method_name, None)
            if method:
                # Convert option to device value if mapping exists
                if self.entity_description.options_map:
                    value = self.entity_description.options_map.get(option, option)
                else:
                    value = option

                await self.hass.async_add_executor_job(method, value)
                await self.coordinator.async_request_refresh()
                _LOGGER.debug(
                    "Successfully set %s to %s",
                    self.entity_description.key,
                    option,
                )
            else:
                _LOGGER.error(
                    "Method %s not found on device for %s",
                    method_name,
                    self.entity_description.key,
                )
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error(
                "Failed to set %s to %s: %s",
                self.entity_description.key,
                option,
                ex,
            )


class XiaomiMiioModeSelect(XiaomiMiioEntity, SelectEntity):
    """Representation of a Xiaomi Miio mode select entity.

    This entity provides a select for operation mode with device-specific options.
    """

    _attr_translation_key = "mode"
    _attr_icon = "mdi:tune"

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the mode select entity."""
        super().__init__(coordinator, unique_id_suffix="mode_select")
        self._attr_name = "Mode"
        self._mode_enum = self._get_mode_enum()
        self._attr_options = self._get_mode_options()

    def _get_mode_enum(self) -> type[Enum] | None:
        """Get the appropriate OperationMode enum for this device."""
        model = self.coordinator.model
        if not model:
            return None

        # Humidifier models
        if model in [
            MODEL_AIRHUMIDIFIER_JSQ2W,
            MODEL_AIRHUMIDIFIER_JSQ3,
            MODEL_AIRHUMIDIFIER_JSQ5,
            MODEL_AIRHUMIDIFIER_JSQS,
        ]:
            from miio.integrations.humidifier.deerma.airhumidifier_jsqs import (
                OperationMode as JsqsOperationMode,
            )

            return JsqsOperationMode
        if model in [
            MODEL_AIRHUMIDIFIER_MJJSQ,
            MODEL_AIRHUMIDIFIER_JSQ,
            MODEL_AIRHUMIDIFIER_JSQ1,
        ]:
            from miio.integrations.humidifier.deerma.airhumidifier_mjjsq import (
                OperationMode as MjjsqOperationMode,
            )

            return MjjsqOperationMode
        if model == MODEL_AIRHUMIDIFIER_JSQ001:
            from miio.integrations.humidifier.shuii.airhumidifier_jsq import (
                OperationMode as JsqOperationMode,
            )

            return JsqOperationMode
        if model == MODEL_AIRHUMIDIFIER_CA4 or model in HUMIDIFIER_MIOT:
            from miio.integrations.humidifier.zhimi.airhumidifier_miot import (
                OperationMode as MiotOperationMode,
            )

            return MiotOperationMode
        if model in [
            MODEL_AIRHUMIDIFIER_CA1,
            MODEL_AIRHUMIDIFIER_CB1,
            MODEL_AIRHUMIDIFIER_CB2,
        ]:
            from miio.integrations.humidifier.zhimi.airhumidifier import (
                OperationMode as ZhimiOperationMode,
            )

            return ZhimiOperationMode
        if model.startswith("zhimi.humidifier."):
            from miio.integrations.humidifier.zhimi.airhumidifier import (
                OperationMode as ZhimiOperationMode,
            )

            return ZhimiOperationMode

        return None

    def _get_mode_options(self) -> list[str]:
        """Get available mode options for this device."""
        if self._mode_enum:
            return [mode.name for mode in self._mode_enum]
        return []

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        if self.coordinator.data:
            return self.coordinator.data.get("mode")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode."""
        if not self._mode_enum:
            _LOGGER.error("No mode enum available for model %s", self.coordinator.model)
            return

        try:
            # Convert option string to enum
            mode_enum = self._mode_enum[option]
            await self.hass.async_add_executor_job(self.coordinator.device.set_mode, mode_enum)
            await self.coordinator.async_request_refresh()
            _LOGGER.debug("Successfully set mode to %s", option)
        except KeyError:
            _LOGGER.error("Invalid mode option: %s", option)
        except Exception as ex:  # noqa: BLE001
            _LOGGER.error("Failed to set mode to %s: %s", option, ex)
