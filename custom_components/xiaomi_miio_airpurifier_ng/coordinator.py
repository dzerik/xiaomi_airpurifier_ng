"""DataUpdateCoordinator for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from miio import Device, DeviceException

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PurifierStatusData(TypedDict, total=False):
    """Typed dict for air purifier coordinator data."""

    power: str
    aqi: int
    average_aqi: int
    humidity: int
    temperature: float
    led: bool
    buzzer: bool
    child_lock: bool
    favorite_level: int
    fan_level: int
    filter_hours_used: int
    filter_life_remaining: int
    motor_speed: int
    use_time: int
    purify_volume: int
    illuminance: int
    tvoc: int
    motor2_speed: int
    filter_rfid_tag: str
    filter_rfid_product_id: str
    filter_left_time: int
    anion: bool
    gestures: bool
    auto_detect: bool
    learn_mode: bool
    volume: int
    buzzer_volume: int
    mode: str | None
    mode_value: Any
    led_brightness: str | None
    filter_type: str | None
    pm10: int


class HumidifierStatusData(TypedDict, total=False):
    """Typed dict for air humidifier coordinator data."""

    power: str
    humidity: int
    target_humidity: int
    temperature: float
    buzzer: bool
    child_lock: bool
    motor_speed: int
    depth: int
    dry: bool
    use_time: int
    water_level: int
    tank_filed: bool
    water_shortage_fault: bool
    no_water: bool
    water_tank_detached: bool
    led_light: bool
    overwet_protect: bool
    mode: str | None
    mode_value: Any
    led_brightness: str | None


class FanStatusData(TypedDict, total=False):
    """Typed dict for fan coordinator data."""

    power: str
    speed: int
    oscillate: bool
    angle: int
    led: bool
    buzzer: bool
    child_lock: bool
    natural_speed: int
    direct_speed: int
    battery: int
    battery_charge: str
    ac_power: bool
    delay_off_countdown: int
    temperature: float
    humidity: int
    fan_level: int
    light: bool
    use_time: int
    power_off_time: int
    mode: str | None
    mode_value: Any
    led_brightness: str | None


class AirFreshStatusData(TypedDict, total=False):
    """Typed dict for air fresh coordinator data."""

    power: str
    aqi: int
    co2: int
    humidity: int
    temperature: float
    led: bool
    buzzer: bool
    child_lock: bool
    filter_hours_used: int
    filter_life_remaining: int
    motor_speed: int
    use_time: int
    ptc: bool
    pm25: int
    temperature_outside: float
    favorite_speed: int
    control_speed: int
    dust_filter_life_remaining: int
    dust_filter_life_remaining_days: int
    upper_filter_life_remaining: int
    upper_filter_life_remaining_days: int
    ptc_status: bool
    display: bool
    mode: str | None
    mode_value: Any
    led_brightness: str | None
    ptc_level: str | None
    display_orientation: str | None


class DehumidifierStatusData(TypedDict, total=False):
    """Typed dict for air dehumidifier coordinator data."""

    power: str
    humidity: int
    target_humidity: int
    temperature: float
    buzzer: bool
    led: bool
    child_lock: bool
    tank_full: bool
    compressor_status: bool
    defrost_status: bool
    fan_st: int
    mode: str | None
    mode_value: Any
    fan_speed: str | None


class XiaomiMiioDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Xiaomi Miio device data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: Device,
    ) -> None:
        """Initialize the coordinator."""
        self.device = device
        self.model = config_entry.data.get(CONF_MODEL)
        self._available = True
        self._device_info = None

        # Get scan interval from options or use default
        scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self._scan_interval_seconds = scan_interval

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.data[CONF_HOST]}",
            config_entry=config_entry,
            update_interval=timedelta(seconds=scan_interval),
        )

        # Listen for option updates
        config_entry.async_on_unload(config_entry.add_update_listener(self._async_options_updated))

    @staticmethod
    async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Handle options update."""
        await hass.config_entries.async_reload(entry.entry_id)

    @property
    def available(self) -> bool:
        """Return True if the device is available."""
        return self._available

    @property
    def device_info_raw(self) -> Any:
        """Return cached device info from initial connection."""
        return self._device_info

    async def _async_setup(self) -> None:
        """Set up the coordinator.

        This method is called during async_config_entry_first_refresh.
        """
        # Get device info to validate connection and detect model
        try:
            info = await self.hass.async_add_executor_job(self.device.info)
            self._device_info = info
            if not self.model:
                self.model = info.model
            _LOGGER.debug(
                "Connected to device: model=%s, firmware=%s",
                info.model,
                info.firmware_version,
            )
        except DeviceException as ex:
            _LOGGER.error("Failed to get device info: %s", ex)
            raise UpdateFailed(f"Failed to connect to device: {ex}") from ex

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            status = await self.hass.async_add_executor_job(self._get_status)
            self._available = True
            return status
        except DeviceException as ex:
            self._available = False
            error_msg = str(ex).lower()
            # Only raise auth failure for actual token errors, not network issues
            if "token" in error_msg and "unable to discover" not in error_msg:
                raise ConfigEntryAuthFailed(f"Authentication failed for device: {ex}") from ex
            raise UpdateFailed(f"Error communicating with device: {ex}") from ex

    def _parse_mode(self, status: Any, data: dict) -> None:
        """Parse mode from status into data dict."""
        if hasattr(status, "mode"):
            if status.mode is not None:
                data["mode"] = (
                    status.mode.name if hasattr(status.mode, "name") else str(status.mode)
                )
                data["mode_value"] = status.mode.value if hasattr(status.mode, "value") else None
            else:
                data["mode"] = None
                data["mode_value"] = None

    @staticmethod
    def _extract_attrs(status: Any, attr_names: list[str]) -> dict[str, Any]:
        """Extract attributes from status object by name.

        Reduces cyclomatic complexity by replacing repeated hasattr/getattr blocks.
        """
        data: dict[str, Any] = {}
        for attr in attr_names:
            if hasattr(status, attr):
                data[attr] = getattr(status, attr)
        return data

    @staticmethod
    def _extract_str_attrs(status: Any, data: dict, *attr_names: str) -> None:
        """Extract attributes as strings into data dict.

        If attribute exists and is not None, stores str(value).
        If attribute exists and is None, stores None.
        If attribute doesn't exist, skips it.
        """
        for attr in attr_names:
            if hasattr(status, attr):
                val = getattr(status, attr)
                data[attr] = str(val) if val is not None else None

    def _get_status(self) -> dict[str, Any]:
        """Get the device status (runs in executor)."""
        status = self.device.status()
        if hasattr(status, "__dict__"):
            return {k: v for k, v in vars(status).items() if not k.startswith("_")}
        return {"raw": status}


class XiaomiAirPurifierCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Purifier devices."""

    # Simple attributes extracted directly from status
    _SIMPLE_ATTRS = [
        "power",
        "aqi",
        "average_aqi",
        "humidity",
        "temperature",
        "led",
        "buzzer",
        "child_lock",
        "favorite_level",
        "fan_level",
        "filter_hours_used",
        "filter_life_remaining",
        "motor_speed",
        "use_time",
        "purify_volume",
        "illuminance",
        "tvoc",
        "motor2_speed",
        "filter_rfid_tag",
        "filter_rfid_product_id",
        "filter_left_time",
        "anion",
        "gestures",
        "auto_detect",
        "learn_mode",
        "volume",
        "buzzer_volume",
    ]

    def _get_status(self) -> PurifierStatusData:
        """Get air purifier status."""
        status = self.device.status()
        data: PurifierStatusData = self._extract_attrs(status, self._SIMPLE_ATTRS)

        self._parse_mode(status, data)
        self._extract_str_attrs(status, data, "led_brightness", "filter_type")

        # Renamed attribute
        if hasattr(status, "pm10_density"):
            data["pm10"] = status.pm10_density

        return data


class XiaomiAirHumidifierCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Humidifier devices."""

    _SIMPLE_ATTRS = [
        "power",
        "target_humidity",
        "temperature",
        "buzzer",
        "child_lock",
        "motor_speed",
        "depth",
        "dry",
        "use_time",
        "water_level",
        "tank_filed",
        "water_shortage_fault",
        "no_water",
        "water_tank_detached",
        "led_light",
        "overwet_protect",
    ]

    def _get_status(self) -> HumidifierStatusData:
        """Get air humidifier status."""
        status = self.device.status()
        data: HumidifierStatusData = self._extract_attrs(status, self._SIMPLE_ATTRS)

        # humidity with fallback to relative_humidity (JSQS models)
        if hasattr(status, "humidity"):
            data["humidity"] = status.humidity
        elif hasattr(status, "relative_humidity"):
            data["humidity"] = status.relative_humidity

        self._parse_mode(status, data)
        self._extract_str_attrs(status, data, "led_brightness")

        return data


class XiaomiFanCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Fan devices."""

    _SIMPLE_ATTRS = [
        "power",
        "speed",
        "oscillate",
        "angle",
        "led",
        "buzzer",
        "child_lock",
        "natural_speed",
        "direct_speed",
        "battery",
        "battery_charge",
        "ac_power",
        "delay_off_countdown",
        "temperature",
        "humidity",
        "fan_level",
        "light",
        "use_time",
        "power_off_time",
    ]

    def _get_status(self) -> FanStatusData:
        """Get fan status."""
        status = self.device.status()
        data: FanStatusData = self._extract_attrs(status, self._SIMPLE_ATTRS)

        self._parse_mode(status, data)
        self._extract_str_attrs(status, data, "led_brightness")

        return data


class XiaomiAirFreshCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Fresh devices."""

    _SIMPLE_ATTRS = [
        "power",
        "aqi",
        "co2",
        "humidity",
        "temperature",
        "led",
        "buzzer",
        "child_lock",
        "filter_hours_used",
        "filter_life_remaining",
        "motor_speed",
        "use_time",
        "ptc",
        "pm25",
        "temperature_outside",
        "favorite_speed",
        "control_speed",
        "dust_filter_life_remaining",
        "dust_filter_life_remaining_days",
        "upper_filter_life_remaining",
        "upper_filter_life_remaining_days",
        "ptc_status",
        "display",
    ]

    def _get_status(self) -> AirFreshStatusData:
        """Get air fresh status."""
        status = self.device.status()
        data: AirFreshStatusData = self._extract_attrs(status, self._SIMPLE_ATTRS)

        self._parse_mode(status, data)

        # String-converted attributes
        self._extract_str_attrs(status, data, "led_brightness", "ptc_level", "display_orientation")

        return data


class XiaomiAirDehumidifierCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Dehumidifier devices."""

    _SIMPLE_ATTRS = [
        "power",
        "humidity",
        "target_humidity",
        "temperature",
        "buzzer",
        "led",
        "child_lock",
        "tank_full",
        "compressor_status",
        "defrost_status",
        "fan_st",
    ]

    def _get_status(self) -> DehumidifierStatusData:
        """Get air dehumidifier status."""
        status = self.device.status()
        data: DehumidifierStatusData = self._extract_attrs(status, self._SIMPLE_ATTRS)

        # Use unified _parse_mode for operation mode (stores .name and .value)
        self._parse_mode(status, data)

        # fan_speed needs separate handling (not covered by _parse_mode)
        if hasattr(status, "fan_speed"):
            if status.fan_speed is not None:
                if hasattr(status.fan_speed, "name"):
                    data["fan_speed"] = status.fan_speed.name
                else:
                    data["fan_speed"] = str(status.fan_speed)
            else:
                data["fan_speed"] = None

        return data
