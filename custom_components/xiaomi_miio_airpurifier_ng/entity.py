"""Base entity for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from .coordinator import XiaomiMiioDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XiaomiMiioEntity(CoordinatorEntity["XiaomiMiioDataUpdateCoordinator"]):
    """Base class for Xiaomi Miio entities."""

    _attr_has_entity_name = True
    _device_features: int = 0

    def __init__(
        self,
        coordinator: XiaomiMiioDataUpdateCoordinator,
        unique_id_suffix: str | None = None,
    ) -> None:
        """Initialize the entity.

        Args:
            coordinator: The data update coordinator.
            unique_id_suffix: Optional suffix for unique_id (e.g., "_aqi" for sensors).
        """
        super().__init__(coordinator)
        from .device_profiles import get_device_profile

        self.profile = get_device_profile(coordinator.model)

        # Instance-level mutable attributes (NOT class-level to avoid shared state)
        # Only set defaults if not already initialized by subclass __init__
        if not hasattr(self, "_available_attributes"):
            self._available_attributes: dict[str, str] = {}
        if not hasattr(self, "_state_attrs"):
            self._state_attrs: dict[str, Any] = {}

        # Build unique ID
        entry_id = coordinator.config_entry.entry_id
        if unique_id_suffix:
            self._attr_unique_id = f"{entry_id}_{unique_id_suffix}"
        else:
            self._attr_unique_id = entry_id

        # Set device info for Device Registry
        self._attr_device_info = self._build_device_info()

    def _build_device_info(self) -> DeviceInfo:
        """Build device info for the device registry."""
        coordinator = self.coordinator
        entry = coordinator.config_entry

        from .identity import device_identifiers

        identifiers = device_identifiers(coordinator.hass, entry, coordinator.device_info_raw)

        # Determine model name for display
        model = coordinator.model or "Unknown Model"
        model_display = self._get_model_display_name(model)

        return DeviceInfo(
            identifiers=identifiers,
            name=entry.title or model_display,
            manufacturer="Xiaomi",
            model=model_display,
            model_id=model,
            sw_version=self._get_firmware_version(),
            hw_version=self._get_hardware_version(),
        )

    def _get_model_display_name(self, model: str) -> str:
        """Get a human-readable model name."""
        # Map model IDs to display names
        model_names = {
            # Air Purifiers
            "zhimi.airpurifier.v1": "Mi Air Purifier",
            "zhimi.airpurifier.v2": "Mi Air Purifier 2",
            "zhimi.airpurifier.v3": "Mi Air Purifier Super",
            "zhimi.airpurifier.v5": "Mi Air Purifier V5",
            "zhimi.airpurifier.v6": "Mi Air Purifier Pro",
            "zhimi.airpurifier.v7": "Mi Air Purifier Pro V7",
            "zhimi.airpurifier.m1": "Mi Air Purifier 2 Mini",
            "zhimi.airpurifier.m2": "Mi Air Purifier 2 Mini",
            "zhimi.airpurifier.ma1": "Mi Air Purifier 2S",
            "zhimi.airpurifier.ma2": "Mi Air Purifier 2S",
            "zhimi.airpurifier.sa1": "Mi Air Purifier Super",
            "zhimi.airpurifier.sa2": "Mi Air Purifier Super 2",
            "zhimi.airpurifier.mc1": "Mi Air Purifier 2S",
            "zhimi.airpurifier.mc2": "Mi Air Purifier 2H",
            "zhimi.airpurifier.ma4": "Mi Air Purifier 3",
            "zhimi.airpurifier.mb3": "Mi Air Purifier 3H",
            "zhimi.airpurifier.za1": "Smartmi Air Purifier",
            "airdog.airpurifier.x3": "Airdog X3",
            "airdog.airpurifier.x5": "Airdog X5",
            "airdog.airpurifier.x7sm": "Airdog X7SM",
            # Air Humidifiers
            "zhimi.humidifier.v1": "Mi Smart Humidifier",
            "zhimi.humidifier.ca1": "Mi Smart Evaporative Humidifier",
            "zhimi.humidifier.ca4": "Mi Smart Evaporative Humidifier 2",
            "zhimi.humidifier.cb1": "Mi Smart Antibacterial Humidifier",
            "zhimi.humidifier.cb2": "Mi Smart Evaporative Humidifier 2",
            "deerma.humidifier.mjjsq": "Mi Smart Humidifier",
            "deerma.humidifier.jsq": "Mi Smart Humidifier",
            "deerma.humidifier.jsq1": "Mi Smart Humidifier",
            "deerma.humidifier.jsq2w": "Xiaomi Smart Humidifier 2",
            "deerma.humidifier.jsq3": "Xiaomi Smart Humidifier 2",
            "deerma.humidifier.jsq5": "Xiaomi Smart Humidifier 2",
            "deerma.humidifier.jsqs": "Deerma Humidifier",
            "shuii.humidifier.jsq001": "Shuii Humidifier",
            # Air Fresh
            "dmaker.airfresh.a1": "Mi Fresh Air Ventilator A1",
            "zhimi.airfresh.va2": "Mi Fresh Air Ventilator",
            "zhimi.airfresh.va4": "Mi Fresh Air Ventilator VA4",
            "dmaker.airfresh.t2017": "Mi Fresh Air Ventilator",
            # Fans
            "zhimi.fan.v2": "Mi Smart Standing Fan 2",
            "zhimi.fan.v3": "Mi Smart Standing Fan 2",
            "zhimi.fan.sa1": "Mi Smart Standing Fan",
            "zhimi.fan.za1": "Smartmi Standing Fan",
            "zhimi.fan.za3": "Smartmi Standing Fan 2",
            "zhimi.fan.za4": "Smartmi Standing Fan 2S",
            "dmaker.fan.p5": "Mi Smart Standing Fan Pro",
            "dmaker.fan.p8": "Mi Smart Tower Fan",
            "dmaker.fan.p9": "Mi Smart Standing Fan",
            "dmaker.fan.p10": "Mi Smart Standing Fan 2",
            "dmaker.fan.p11": "Mi Smart Standing Fan Pro",
            "dmaker.fan.p18": "Mi Smart Standing Fan 2",
            "leshow.fan.ss4": "Leshow Smart Fan SS4",
            "dmaker.fan.1c": "Mi Smart Standing Fan 1C",
            # Dehumidifier
            "nwt.derh.wdh318efw1": "Mi Smart Dehumidifier",
        }
        return model_names.get(model, model)

    def _get_firmware_version(self) -> str | None:
        """Get firmware version from cached device info."""
        info = self.coordinator.device_info_raw
        if info:
            return info.firmware_version
        return None

    def _get_hardware_version(self) -> str | None:
        """Get hardware version from cached device info."""
        info = self.coordinator.device_info_raw
        if info:
            return info.hardware_version
        return None

    def _check_feature(self, feature_flag: int, feature_name: str) -> bool:
        """Check if a feature is supported and log warning if not."""
        if self._device_features & feature_flag == 0:
            _LOGGER.debug(
                "Feature %s not supported by %s (feature flag not set)",
                feature_name,
                self.coordinator.model,
            )
            return False
        return True

    @staticmethod
    def _extract_value_from_attribute(value: Any) -> Any:
        """Extract the actual value from an attribute, handling Enums."""
        if isinstance(value, Enum):
            return value.value
        return value

    async def _async_command(self, name: str, *args: Any) -> None:
        """Use the coordinator's shared serialization and error contract."""
        await self.coordinator.async_execute_command(name, *args)

    @property
    def is_on(self) -> bool | None:
        """Return true if the device is on.

        python-miio returns power as string "on"/"off" for all models.
        Using bool(power) would be incorrect since bool("off") == True.
        """
        if self.coordinator.data:
            power = self.coordinator.data.get("power")
            if power is not None:
                if isinstance(power, str):
                    return power == "on"
                return bool(power)
            is_on = self.coordinator.data.get("is_on")
            if is_on is not None:
                return bool(is_on)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes of the device."""
        if self.coordinator.data and self._available_attributes:
            for key, attr_name in self._available_attributes.items():
                value = self.coordinator.data.get(attr_name)
                if value is not None:
                    self._state_attrs[key] = self._extract_value_from_attribute(value)
        return self._state_attrs

    async def _async_device_on(self) -> None:
        """Apply power through the shared command and state-update path."""
        await self._async_command("on")

    async def _async_device_off(self) -> None:
        """Apply power through the shared command and state-update path."""
        await self._async_command("off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.coordinator.available
