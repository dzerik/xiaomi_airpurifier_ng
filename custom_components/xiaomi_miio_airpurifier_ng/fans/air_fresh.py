"""Air Fresh fan entity for Xiaomi Miio devices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from miio.integrations.airpurifier.dmaker.airfresh_t2017 import (
    OperationMode as AirfreshT2017OperationMode,
)
from miio.integrations.airpurifier.zhimi.airfresh import (
    OperationMode as AirfreshOperationMode,
)

from ..const import (
    AVAILABLE_ATTRIBUTES_AIRFRESH,
    AVAILABLE_ATTRIBUTES_AIRFRESH_A1,
    AVAILABLE_ATTRIBUTES_AIRFRESH_T2017,
    AVAILABLE_ATTRIBUTES_AIRFRESH_VA4,
    FEATURE_FLAGS_AIRFRESH,
    FEATURE_FLAGS_AIRFRESH_A1,
    FEATURE_FLAGS_AIRFRESH_T2017,
    FEATURE_FLAGS_AIRFRESH_VA4,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA4,
    OPERATION_MODES_AIRFRESH,
    OPERATION_MODES_AIRFRESH_T2017,
    ModelConfig,
)
from .base import XiaomiMiioBaseFan

if TYPE_CHECKING:
    from ..coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Default config for unknown air fresh models
_DEFAULT_AIRFRESH_CONFIG = ModelConfig(
    features=FEATURE_FLAGS_AIRFRESH,
    attributes=AVAILABLE_ATTRIBUTES_AIRFRESH,
    preset_modes=list(OPERATION_MODES_AIRFRESH),
)

# Model → config lookup (replaces if/elif chain)
_AIRFRESH_MODEL_CONFIGS: dict[str, ModelConfig] = {
    MODEL_AIRFRESH_T2017: ModelConfig(
        features=FEATURE_FLAGS_AIRFRESH_T2017,
        attributes=AVAILABLE_ATTRIBUTES_AIRFRESH_T2017,
        preset_modes=list(OPERATION_MODES_AIRFRESH_T2017),
    ),
    MODEL_AIRFRESH_A1: ModelConfig(
        features=FEATURE_FLAGS_AIRFRESH_A1,
        attributes=AVAILABLE_ATTRIBUTES_AIRFRESH_A1,
        preset_modes=list(OPERATION_MODES_AIRFRESH_T2017),
    ),
    MODEL_AIRFRESH_VA4: ModelConfig(
        features=FEATURE_FLAGS_AIRFRESH_VA4,
        attributes=AVAILABLE_ATTRIBUTES_AIRFRESH_VA4,
        preset_modes=list(OPERATION_MODES_AIRFRESH),
    ),
}


class XiaomiAirFreshFan(XiaomiMiioBaseFan):
    """Coordinator-based fan entity for Air Fresh devices."""

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
    ) -> None:
        """Initialize the air fresh fan entity."""
        model = coordinator.model

        # Determine device type
        self._is_t2017 = model in [MODEL_AIRFRESH_T2017, MODEL_AIRFRESH_A1]

        # Lookup model config (replaces if/elif chain)
        config = _AIRFRESH_MODEL_CONFIGS.get(model, _DEFAULT_AIRFRESH_CONFIG)
        self._device_features = config.features
        self._available_attributes = config.attributes
        self._preset_modes = list(config.preset_modes)

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
            if self._is_t2017:
                mode_enum = AirfreshT2017OperationMode[preset_mode.title()]
            else:
                mode_enum = AirfreshOperationMode[preset_mode.title()]
        except KeyError:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        await self._try_command(
            "Setting preset mode of the miio device failed: %s",
            self.coordinator.device.set_mode,
            mode_enum,
        )
        await self.coordinator.async_request_refresh()
