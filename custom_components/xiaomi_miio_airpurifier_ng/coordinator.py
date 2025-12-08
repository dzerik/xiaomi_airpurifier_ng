"""DataUpdateCoordinator for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from miio import Device, DeviceException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


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

        # Get scan interval from options or use default
        scan_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        self._scan_interval_seconds = scan_interval

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.data[CONF_HOST]}",
            config_entry=config_entry,
            update_interval=timedelta(seconds=scan_interval),
            always_update=True,
        )

        # Listen for option updates
        config_entry.async_on_unload(
            config_entry.add_update_listener(self._async_options_updated)
        )

    @staticmethod
    async def _async_options_updated(
        hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        await hass.config_entries.async_reload(entry.entry_id)

    @property
    def available(self) -> bool:
        """Return True if the device is available."""
        return self._available

    async def _async_setup(self) -> None:
        """Set up the coordinator.

        This method is called during async_config_entry_first_refresh.
        """
        # Get device info to validate connection and detect model
        try:
            info = await self.hass.async_add_executor_job(self.device.info)
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
        """Fetch data from the device.

        This method is called periodically to refresh the device state.
        """
        try:
            # Get status from the device
            # Note: This runs in executor because python-miio is synchronous
            status = await self.hass.async_add_executor_job(self._get_status)
            self._available = True
            return status
        except DeviceException as ex:
            self._available = False
            # Check if it's an authentication error
            if "Unable to discover" in str(ex) or "token" in str(ex).lower():
                raise ConfigEntryAuthFailed(
                    f"Authentication failed for device: {ex}"
                ) from ex
            raise UpdateFailed(f"Error communicating with device: {ex}") from ex

    def _get_status(self) -> dict[str, Any]:
        """Get the device status (runs in executor).

        This method should be overridden by device-specific coordinators
        to return the appropriate status data.
        """
        # Default implementation - returns raw status
        # Device-specific coordinators should override this
        try:
            status = self.device.status()
            # Convert status object to dictionary for easier access
            if hasattr(status, "__dict__"):
                return {
                    k: v for k, v in vars(status).items() if not k.startswith("_")
                }
            return {"raw": status}
        except Exception as ex:
            _LOGGER.debug("Error getting status: %s", ex)
            raise


class XiaomiAirPurifierCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Purifier devices."""

    def _get_status(self) -> dict[str, Any]:
        """Get air purifier status."""
        status = self.device.status()

        # Extract common attributes
        data: dict[str, Any] = {}

        # Map status attributes to data dictionary
        if hasattr(status, "power"):
            data["power"] = status.power
        if hasattr(status, "aqi"):
            data["aqi"] = status.aqi
        if hasattr(status, "average_aqi"):
            data["average_aqi"] = status.average_aqi
        if hasattr(status, "humidity"):
            data["humidity"] = status.humidity
        if hasattr(status, "temperature"):
            data["temperature"] = status.temperature
        if hasattr(status, "mode"):
            # Store mode name (e.g., "Low") and value for enum lookup
            if status.mode:
                data["mode"] = status.mode.name if hasattr(status.mode, "name") else str(status.mode)
                data["mode_value"] = status.mode.value if hasattr(status.mode, "value") else None
            else:
                data["mode"] = None
                data["mode_value"] = None
        if hasattr(status, "led"):
            data["led"] = status.led
        if hasattr(status, "led_brightness"):
            data["led_brightness"] = (
                str(status.led_brightness) if status.led_brightness else None
            )
        if hasattr(status, "buzzer"):
            data["buzzer"] = status.buzzer
        if hasattr(status, "child_lock"):
            data["child_lock"] = status.child_lock
        if hasattr(status, "favorite_level"):
            data["favorite_level"] = status.favorite_level
        if hasattr(status, "fan_level"):
            data["fan_level"] = status.fan_level
        if hasattr(status, "filter_hours_used"):
            data["filter_hours_used"] = status.filter_hours_used
        if hasattr(status, "filter_life_remaining"):
            data["filter_life_remaining"] = status.filter_life_remaining
        if hasattr(status, "motor_speed"):
            data["motor_speed"] = status.motor_speed
        if hasattr(status, "use_time"):
            data["use_time"] = status.use_time
        if hasattr(status, "purify_volume"):
            data["purify_volume"] = status.purify_volume
        # Additional sensors
        if hasattr(status, "illuminance"):
            data["illuminance"] = status.illuminance
        if hasattr(status, "tvoc"):
            data["tvoc"] = status.tvoc
        if hasattr(status, "pm10_density"):
            data["pm10"] = status.pm10_density
        if hasattr(status, "motor2_speed"):
            data["motor2_speed"] = status.motor2_speed
        # Filter RFID info
        if hasattr(status, "filter_rfid_tag"):
            data["filter_rfid_tag"] = status.filter_rfid_tag
        if hasattr(status, "filter_rfid_product_id"):
            data["filter_rfid_product_id"] = status.filter_rfid_product_id
        if hasattr(status, "filter_type"):
            data["filter_type"] = str(status.filter_type) if status.filter_type else None
        if hasattr(status, "filter_left_time"):
            data["filter_left_time"] = status.filter_left_time
        # Boolean features
        if hasattr(status, "anion"):
            data["anion"] = status.anion
        if hasattr(status, "gestures"):
            data["gestures"] = status.gestures
        if hasattr(status, "auto_detect"):
            data["auto_detect"] = status.auto_detect
        if hasattr(status, "learn_mode"):
            data["learn_mode"] = status.learn_mode
        # Volume
        if hasattr(status, "volume"):
            data["volume"] = status.volume
        if hasattr(status, "buzzer_volume"):
            data["buzzer_volume"] = status.buzzer_volume

        return data


class XiaomiAirHumidifierCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Humidifier devices."""

    def _get_status(self) -> dict[str, Any]:
        """Get air humidifier status."""
        status = self.device.status()

        data: dict[str, Any] = {}

        if hasattr(status, "power"):
            data["power"] = status.power
        if hasattr(status, "humidity"):
            data["humidity"] = status.humidity
        if hasattr(status, "target_humidity"):
            data["target_humidity"] = status.target_humidity
        if hasattr(status, "temperature"):
            data["temperature"] = status.temperature
        if hasattr(status, "mode"):
            # Store mode name (e.g., "Low") and value for enum lookup
            if status.mode:
                data["mode"] = status.mode.name if hasattr(status.mode, "name") else str(status.mode)
                data["mode_value"] = status.mode.value if hasattr(status.mode, "value") else None
            else:
                data["mode"] = None
                data["mode_value"] = None
        if hasattr(status, "led_brightness"):
            data["led_brightness"] = (
                str(status.led_brightness) if status.led_brightness else None
            )
        if hasattr(status, "buzzer"):
            data["buzzer"] = status.buzzer
        if hasattr(status, "child_lock"):
            data["child_lock"] = status.child_lock
        if hasattr(status, "motor_speed"):
            data["motor_speed"] = status.motor_speed
        if hasattr(status, "depth"):
            data["depth"] = status.depth
        if hasattr(status, "dry"):
            data["dry"] = status.dry
        if hasattr(status, "use_time"):
            data["use_time"] = status.use_time
        if hasattr(status, "water_level"):
            data["water_level"] = status.water_level
        # Water tank status (Jsqs models)
        if hasattr(status, "tank_filed"):
            data["tank_filed"] = status.tank_filed
        if hasattr(status, "water_shortage_fault"):
            data["water_shortage_fault"] = status.water_shortage_fault
        # Water tank status (Mjjsq models)
        if hasattr(status, "no_water"):
            data["no_water"] = status.no_water
        if hasattr(status, "water_tank_detached"):
            data["water_tank_detached"] = status.water_tank_detached

        return data


class XiaomiFanCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Fan devices."""

    def _get_status(self) -> dict[str, Any]:
        """Get fan status."""
        status = self.device.status()

        data: dict[str, Any] = {}

        if hasattr(status, "power"):
            data["power"] = status.power
        if hasattr(status, "speed"):
            data["speed"] = status.speed
        if hasattr(status, "oscillate"):
            data["oscillate"] = status.oscillate
        if hasattr(status, "angle"):
            data["angle"] = status.angle
        if hasattr(status, "mode"):
            # Store mode name (e.g., "Low") and value for enum lookup
            if status.mode:
                data["mode"] = status.mode.name if hasattr(status.mode, "name") else str(status.mode)
                data["mode_value"] = status.mode.value if hasattr(status.mode, "value") else None
            else:
                data["mode"] = None
                data["mode_value"] = None
        if hasattr(status, "led"):
            data["led"] = status.led
        if hasattr(status, "led_brightness"):
            data["led_brightness"] = (
                str(status.led_brightness) if status.led_brightness else None
            )
        if hasattr(status, "buzzer"):
            data["buzzer"] = status.buzzer
        if hasattr(status, "child_lock"):
            data["child_lock"] = status.child_lock
        if hasattr(status, "natural_speed"):
            data["natural_speed"] = status.natural_speed
        if hasattr(status, "direct_speed"):
            data["direct_speed"] = status.direct_speed
        if hasattr(status, "battery"):
            data["battery"] = status.battery
        if hasattr(status, "battery_charge"):
            data["battery_charge"] = status.battery_charge
        if hasattr(status, "ac_power"):
            data["ac_power"] = status.ac_power
        if hasattr(status, "delay_off_countdown"):
            data["delay_off_countdown"] = status.delay_off_countdown
        # Additional fan attributes
        if hasattr(status, "temperature"):
            data["temperature"] = status.temperature
        if hasattr(status, "humidity"):
            data["humidity"] = status.humidity
        if hasattr(status, "fan_level"):
            data["fan_level"] = status.fan_level
        if hasattr(status, "light"):
            data["light"] = status.light
        if hasattr(status, "use_time"):
            data["use_time"] = status.use_time
        if hasattr(status, "power_off_time"):
            data["power_off_time"] = status.power_off_time

        return data


class XiaomiAirFreshCoordinator(XiaomiMiioDataUpdateCoordinator):
    """Coordinator for Xiaomi Air Fresh devices."""

    def _get_status(self) -> dict[str, Any]:
        """Get air fresh status."""
        status = self.device.status()

        data: dict[str, Any] = {}

        if hasattr(status, "power"):
            data["power"] = status.power
        if hasattr(status, "aqi"):
            data["aqi"] = status.aqi
        if hasattr(status, "co2"):
            data["co2"] = status.co2
        if hasattr(status, "humidity"):
            data["humidity"] = status.humidity
        if hasattr(status, "temperature"):
            data["temperature"] = status.temperature
        if hasattr(status, "mode"):
            # Store mode name (e.g., "Low") and value for enum lookup
            if status.mode:
                data["mode"] = status.mode.name if hasattr(status.mode, "name") else str(status.mode)
                data["mode_value"] = status.mode.value if hasattr(status.mode, "value") else None
            else:
                data["mode"] = None
                data["mode_value"] = None
        if hasattr(status, "led"):
            data["led"] = status.led
        if hasattr(status, "led_brightness"):
            data["led_brightness"] = (
                str(status.led_brightness) if status.led_brightness else None
            )
        if hasattr(status, "buzzer"):
            data["buzzer"] = status.buzzer
        if hasattr(status, "child_lock"):
            data["child_lock"] = status.child_lock
        if hasattr(status, "filter_hours_used"):
            data["filter_hours_used"] = status.filter_hours_used
        if hasattr(status, "filter_life_remaining"):
            data["filter_life_remaining"] = status.filter_life_remaining
        if hasattr(status, "motor_speed"):
            data["motor_speed"] = status.motor_speed
        if hasattr(status, "use_time"):
            data["use_time"] = status.use_time
        if hasattr(status, "ptc"):
            data["ptc"] = status.ptc
        # T2017 specific attributes
        if hasattr(status, "pm25"):
            data["pm25"] = status.pm25
        if hasattr(status, "temperature_outside"):
            data["temperature_outside"] = status.temperature_outside
        if hasattr(status, "favorite_speed"):
            data["favorite_speed"] = status.favorite_speed
        if hasattr(status, "control_speed"):
            data["control_speed"] = status.control_speed
        # Dust filter (intermediate)
        if hasattr(status, "dust_filter_life_remaining"):
            data["dust_filter_life_remaining"] = status.dust_filter_life_remaining
        if hasattr(status, "dust_filter_life_remaining_days"):
            data["dust_filter_life_remaining_days"] = status.dust_filter_life_remaining_days
        # Upper filter (efficient/HEPA)
        if hasattr(status, "upper_filter_life_remaining"):
            data["upper_filter_life_remaining"] = status.upper_filter_life_remaining
        if hasattr(status, "upper_filter_life_remaining_days"):
            data["upper_filter_life_remaining_days"] = status.upper_filter_life_remaining_days
        # PTC heater
        if hasattr(status, "ptc_level"):
            data["ptc_level"] = str(status.ptc_level) if status.ptc_level else None
        if hasattr(status, "ptc_status"):
            data["ptc_status"] = status.ptc_status
        # Display
        if hasattr(status, "display"):
            data["display"] = status.display
        if hasattr(status, "display_orientation"):
            data["display_orientation"] = (
                str(status.display_orientation) if status.display_orientation else None
            )

        return data
