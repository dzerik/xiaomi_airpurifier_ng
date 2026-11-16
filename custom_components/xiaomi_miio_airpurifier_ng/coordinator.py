"""DataUpdateCoordinator for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from typing import Any, TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from miio import Device, DeviceException

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .device_profiles import UnsupportedModelError, get_device_profile

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


@dataclass(frozen=True)
class DeviceCommand:
    """One operation in an ordered device transaction."""

    name: str
    args: tuple[Any, ...] = ()
    delay_after: float = 0


def validate_command_result(result: Any) -> None:
    """Recognize both legacy miIO acknowledgments and MIoT result codes."""
    if result == ["ok"]:
        return
    if (
        isinstance(result, list)
        and result
        and all(
            isinstance(item, dict) and type(item.get("code")) is int and item["code"] == 0
            for item in result
        )
    ):
        return
    raise HomeAssistantError(translation_domain=DOMAIN, translation_key="command_rejected")


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
        self._io_lock = asyncio.Lock()
        try:
            self.profile = get_device_profile(self.model)
        except UnsupportedModelError:
            self.profile = None
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

    async def _async_io(self, func: Any, *args: Any) -> Any:
        """Keep the I/O lock until an executor job finishes, even on cancellation."""
        future = asyncio.ensure_future(self.hass.async_add_executor_job(func, *args))
        try:
            return await asyncio.shield(future)
        except asyncio.CancelledError:
            while not future.done():
                try:
                    await asyncio.shield(future)
                except asyncio.CancelledError:
                    continue
                except Exception:
                    break
            if not future.cancelled():
                future.exception()
            raise

    async def async_execute_command(self, name: str, *args: Any) -> None:
        """Execute a single supported operation."""
        await self.async_execute_commands((DeviceCommand(name, args),))

    async def async_execute_commands(self, commands: Sequence[DeviceCommand]) -> None:
        """Serialize an entire transaction; publish and refresh after releasing I/O."""
        try:
            async with self._io_lock:
                optimistic = await self._async_execute_locked(commands)
        except ServiceValidationError:
            raise
        except HomeAssistantError:
            # The device may have accepted earlier operations in this transaction.
            await self.async_request_refresh()
            raise
        await self._async_publish_command(optimistic)

    async def _async_execute_locked(self, commands: Sequence[DeviceCommand]) -> dict[str, Any]:
        """Execute an already serialized transaction after validating every operation."""
        operations = []
        for command in commands:
            if not self.profile or command.name not in self.profile.commands:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="unsupported_command",
                    translation_placeholders={"command": command.name},
                )
            method = getattr(
                self.device, self.profile.command_aliases.get(command.name, command.name), None
            )
            if not callable(method):
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="unsupported_command",
                    translation_placeholders={"command": command.name},
                )
            operations.append((command, method))
        optimistic = {}
        for command, method in operations:
            try:
                result = await self._async_io(partial(method, *command.args))
                validate_command_result(result)
            except DeviceException as exc:
                raise HomeAssistantError(
                    translation_domain=DOMAIN, translation_key="communication_error"
                ) from exc
            if command.name in ("on", "off"):
                optimistic["power"] = command.name
            elif command.name == "set_mode" and command.args:
                optimistic["mode"] = getattr(command.args[0], "name", command.args[0])
            elif command.name == "set_target_humidity":
                optimistic["target_humidity"] = command.args[0]
            if command.delay_after:
                await asyncio.sleep(command.delay_after)
        return optimistic

    async def _async_publish_command(self, optimistic: dict[str, Any]) -> None:
        """Notify all entities only after the protocol acknowledges the transaction."""
        if optimistic and self.data is not None:
            self.async_set_updated_data({**self.data, **optimistic})
        await self.async_request_refresh()

    async def async_set_humidity(self, value: int) -> None:
        """Apply the same range and mode prerequisites for every humidity platform."""
        control = self.profile.humidity if self.profile else None
        if control is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unsupported_command",
                translation_placeholders={"command": "set_target_humidity"},
            )
        try:
            target = control.normalize(value)
        except ValueError as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_humidity",
                translation_placeholders={
                    "minimum": str(control.minimum),
                    "maximum": str(control.maximum),
                },
            ) from exc
        try:
            async with self._io_lock:
                commands = []
                if control.mode is not None and (self.data or {}).get("mode") != control.mode.name:
                    commands.append(DeviceCommand("set_mode", (control.mode,), control.mode_delay))
                commands.append(DeviceCommand("set_target_humidity", (target,)))
                optimistic = await self._async_execute_locked(commands)
        except ServiceValidationError:
            raise
        except HomeAssistantError:
            # The device may have accepted earlier operations in this transaction.
            await self.async_request_refresh()
            raise
        await self._async_publish_command(optimistic)

    @property
    def available(self) -> bool:
        """Return True if the device is available."""
        return self._available

    @property
    def device_info_raw(self) -> Any:
        """Return cached device info from initial connection."""
        return self._device_info

    async def _async_setup(self) -> None:
        """Fetch optional metadata without changing a device's stable identity."""
        try:
            async with self._io_lock:
                self._device_info = await self._async_io(self.device.info)
                if not self.model:
                    self.model = self._device_info.model
                    self.profile = get_device_profile(self.model)
        except DeviceException as ex:
            _LOGGER.debug("Device info not available yet: %s", ex)

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll with the same serialization used by all command platforms."""
        try:
            async with self._io_lock:
                status = await self._async_io(self._get_status)
                self._available = True
                if self._device_info is None:
                    try:
                        self._device_info = await self._async_io(self.device.info)
                        if not self.model:
                            self.model = self._device_info.model
                            self.profile = get_device_profile(self.model)
                    except DeviceException:
                        pass
                from .identity import update_device_metadata

                update_device_metadata(self.hass, self.config_entry, self._device_info, self.model)
                return status
        except DeviceException as ex:
            self._available = False
            error_msg = str(ex).lower()
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

        data.update(
            self._extract_attrs(status, ["speed", "hcho", "clean_filters", "pm25", "favorite_rpm"])
        )
        if data.get("aqi") is None and data.get("pm25") is not None:
            data["aqi"] = data["pm25"]
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
