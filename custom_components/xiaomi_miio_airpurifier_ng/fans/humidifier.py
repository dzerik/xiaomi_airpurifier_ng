"""Air Humidifier fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from miio.integrations.humidifier.deerma.airhumidifier_jsqs import (
    OperationMode as AirhumidifierJsqsOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_mjjsq import (
    OperationMode as AirhumidifierMjjsqOperationMode,
)
from miio.integrations.humidifier.shuii.airhumidifier_jsq import (
    OperationMode as AirhumidifierJsqOperationMode,
)
from miio.integrations.humidifier.zhimi.airhumidifier import (
    OperationMode as AirhumidifierOperationMode,
)
from miio.integrations.humidifier.zhimi.airhumidifier_miot import (
    OperationMode as AirhumidifierMiotOperationMode,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS,
    AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ,
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
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiAirHumidifierFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Air Humidifiers."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the air humidifier fan entity."""
        model = coordinator.model

        # Determine device type for later use
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

        # Set device features and available attributes based on model
        if model in [
            MODEL_AIRHUMIDIFIER_CA1,
            MODEL_AIRHUMIDIFIER_CB1,
            MODEL_AIRHUMIDIFIER_CB2,
        ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Strong
            ]
        elif model == MODEL_AIRHUMIDIFIER_CA4:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._preset_modes = [mode.name for mode in AirhumidifierMiotOperationMode]
        elif model == MODEL_AIRHUMIDIFIER_JSQ1:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_MJJSQ, MODEL_AIRHUMIDIFIER_JSQ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierMjjsqOperationMode
                if self._device_features & FEATURE_SET_WET_PROTECTION != 0
                or mode != AirhumidifierMjjsqOperationMode.WetAndProtect
            ]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ3, MODEL_AIRHUMIDIFIER_JSQ5]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5
            self._preset_modes = [mode.name for mode in AirhumidifierJsqsOperationMode]
        elif model in [MODEL_AIRHUMIDIFIER_JSQ2W, MODEL_AIRHUMIDIFIER_JSQS]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS
            self._preset_modes = [mode.name for mode in AirhumidifierJsqsOperationMode]
        elif model == MODEL_AIRHUMIDIFIER_JSQ001:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ
            self._preset_modes = [mode.name for mode in AirhumidifierJsqOperationMode]
        elif self._is_miot:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._preset_modes = [mode.name for mode in AirhumidifierMiotOperationMode]
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Auto
            ]

        # Initialize base class after setting attributes
        super().__init__(coordinator)

    @property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.coordinator.data:
            # Use mode name directly (already extracted in coordinator)
            mode = self.coordinator.data.get("mode")
            if mode:
                return mode
        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        try:
            if self._is_miot:
                mode_enum = AirhumidifierMiotOperationMode[preset_mode.title()]
            elif self._is_mjjsq:
                mode_enum = AirhumidifierMjjsqOperationMode[preset_mode.title()]
            elif self._is_jsqs:
                mode_enum = AirhumidifierJsqsOperationMode[preset_mode.title()]
            elif self._is_jsq:
                mode_enum = AirhumidifierJsqOperationMode[preset_mode.title()]
            else:
                mode_enum = AirhumidifierOperationMode[preset_mode.title()]
        except KeyError:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        await self._try_command(
            "Setting preset mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()

