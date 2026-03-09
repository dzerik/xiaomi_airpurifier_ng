"""Support for Xiaomi Air Humidifier as humidifier platform."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from miio.integrations.humidifier.shuii.airhumidifier_jsq import (
    OperationMode as AirhumidifierJsqOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_jsqs import (
    OperationMode as AirhumidifierJsqsOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_mjjsq import (
    OperationMode as AirhumidifierMjjsqOperationMode,
)
from miio.integrations.humidifier.zhimi.airhumidifier import (
    OperationMode as AirhumidifierOperationMode,
)
from miio.integrations.humidifier.zhimi.airhumidifier_miot import (
    OperationMode as AirhumidifierMiotOperationMode,
)

from .const import (
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ,
    DeviceCategory,
    FEATURE_FLAGS_AIRHUMIDIFIER,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA4,
    FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5,
    FEATURE_FLAGS_AIRHUMIDIFIER_JSQS,
    FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ,
    FEATURE_SET_WET_PROTECTION,
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
    classify_model,
)
from .entity import XiaomiMiioEntity

if TYPE_CHECKING:
    from .coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

MIN_HUMIDITY = 30
MAX_HUMIDITY = 80


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Miio humidifier from a config entry."""
    coordinator: XiaomiMiioDataUpdateCoordinator = entry.runtime_data

    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    model = coordinator.model
    category = classify_model(model)

    if category == DeviceCategory.HUMIDIFIER:
        async_add_entities([XiaomiAirHumidifier(coordinator)])


class XiaomiAirHumidifier(XiaomiMiioEntity, HumidifierEntity):
    """Humidifier entity for Xiaomi Air Humidifier devices."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_min_humidity = MIN_HUMIDITY
    _attr_max_humidity = MAX_HUMIDITY
    _attr_supported_features = HumidifierEntityFeature.MODES

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the humidifier entity."""
        model = coordinator.model

        self._is_miot = model in HUMIDIFIER_MIOT
        self._is_mjjsq = model in [
            MODEL_AIRHUMIDIFIER_MJJSQ,
            MODEL_AIRHUMIDIFIER_JSQ,
            MODEL_AIRHUMIDIFIER_JSQ1,
        ]
        self._is_jsqs = model in [
            MODEL_AIRHUMIDIFIER_JSQ2W,
            MODEL_AIRHUMIDIFIER_JSQ3,
            MODEL_AIRHUMIDIFIER_JSQ5,
            MODEL_AIRHUMIDIFIER_JSQS,
        ]
        self._is_jsq = model == MODEL_AIRHUMIDIFIER_JSQ001

        if model in [
            MODEL_AIRHUMIDIFIER_CA1,
            MODEL_AIRHUMIDIFIER_CB1,
            MODEL_AIRHUMIDIFIER_CB2,
        ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
            self._attr_available_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Strong
            ]
        elif model == MODEL_AIRHUMIDIFIER_CA4:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._attr_available_modes = [
                mode.name for mode in AirhumidifierMiotOperationMode
            ]
        elif model == MODEL_AIRHUMIDIFIER_JSQ1:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1
            self._attr_available_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_MJJSQ, MODEL_AIRHUMIDIFIER_JSQ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ
            self._attr_available_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ3, MODEL_AIRHUMIDIFIER_JSQ5]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5
            self._attr_available_modes = [
                mode.name for mode in AirhumidifierJsqsOperationMode
            ]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ2W, MODEL_AIRHUMIDIFIER_JSQS]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS
            self._attr_available_modes = [
                mode.name for mode in AirhumidifierJsqsOperationMode
            ]
        elif model == MODEL_AIRHUMIDIFIER_JSQ001:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ
            self._attr_available_modes = [
                mode.name for mode in AirhumidifierJsqOperationMode
            ]
        elif self._is_miot:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._attr_available_modes = [
                mode.name for mode in AirhumidifierMiotOperationMode
            ]
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER
            self._attr_available_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Auto
            ]

        super().__init__(coordinator)
        self._state_attrs = {attribute: None for attribute in self._available_attributes}

    @property
    def target_humidity(self) -> int | None:
        """Return the target humidity."""
        if self.coordinator.data:
            return self.coordinator.data.get("target_humidity")
        return None

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        if self.coordinator.data:
            return self.coordinator.data.get("humidity")
        return None

    @property
    def mode(self) -> str | None:
        """Return the current mode."""
        if self.coordinator.data:
            mode = self.coordinator.data.get("mode")
            if mode:
                return mode
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self._async_device_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self._async_device_off()

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidity."""
        await self._try_command(
            "Setting target humidity of the miio device failed: %s",
            self.coordinator.device.set_target_humidity,
            humidity,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        _LOGGER.debug("Setting the operation mode to: %s", mode)

        try:
            if self._is_miot:
                mode_enum = AirhumidifierMiotOperationMode[mode.title()]
            elif self._is_mjjsq:
                mode_enum = AirhumidifierMjjsqOperationMode[mode.title()]
            elif self._is_jsqs:
                mode_enum = AirhumidifierJsqsOperationMode[mode.title()]
            elif self._is_jsq:
                mode_enum = AirhumidifierJsqOperationMode[mode.title()]
            else:
                mode_enum = AirhumidifierOperationMode[mode.title()]
        except KeyError:
            _LOGGER.error("Invalid operation mode: %s", mode)
            return

        await self._try_command(
            "Setting operation mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()
