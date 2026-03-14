"""Config flow for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from miio import Device, DeviceException

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SUPPORTED_MODELS,
)

_LOGGER = logging.getLogger(__name__)

# Cloud server regions
CLOUD_SERVERS = {
    "cn": "China",
    "de": "Germany (Europe)",
    "i2": "India",
    "ru": "Russia",
    "sg": "Singapore",
    "us": "United States",
}

# Known integration domains that store Xiaomi device tokens
_XIAOMI_DOMAINS = ("xiaomi_miio", "xiaomi_miot")

# Setup method constants
SETUP_CLOUD = "cloud"
SETUP_MANUAL = "manual"


class XiaomiMiioConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Air Purifier NG."""

    VERSION = 1
    MINOR_VERSION = 2

    @staticmethod
    def async_get_options_flow(
        config_entry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return XiaomiMiioOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._token: str | None = None
        self._name: str | None = None
        self._model: str | None = None
        self._cloud_devices: dict[str, dict[str, Any]] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step — choose setup method."""
        if user_input is not None:
            method = user_input.get("setup_method", SETUP_MANUAL)
            if method == SETUP_CLOUD:
                return await self.async_step_cloud()
            return await self.async_step_manual()

        # Check if tokens are available from other Xiaomi integrations
        imported = self._find_existing_xiaomi_entries()
        description_placeholders = {}
        if imported:
            description_placeholders["existing_count"] = str(len(imported))

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("setup_method", default=SETUP_CLOUD): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"value": SETUP_CLOUD, "label": "Xiaomi Cloud Login"},
                                {"value": SETUP_MANUAL, "label": "Manual Setup (IP + Token)"},
                            ],
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            description_placeholders=description_placeholders,
        )

    async def async_step_cloud(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle Xiaomi Cloud login step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input["cloud_username"]
            password = user_input["cloud_password"]
            server = user_input["cloud_server"]

            try:
                devices = await self._async_cloud_login(username, password, server)
            except Exception as ex:  # noqa: BLE001
                _LOGGER.error("Cloud login failed: %s", ex)
                errors["base"] = "cloud_login_error"
            else:
                if not devices:
                    errors["base"] = "cloud_no_devices"
                else:
                    # Filter to supported models only
                    supported = {
                        k: v for k, v in devices.items() if v.get("model") in SUPPORTED_MODELS
                    }
                    if not supported:
                        # Show all devices if none match our supported list
                        self._cloud_devices = devices
                    else:
                        self._cloud_devices = supported

                    if not self._cloud_devices:
                        errors["base"] = "cloud_no_devices"
                    else:
                        return await self.async_step_select()

        return self.async_show_form(
            step_id="cloud",
            data_schema=vol.Schema(
                {
                    vol.Required("cloud_username"): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.EMAIL)
                    ),
                    vol.Required("cloud_password"): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Required("cloud_server", default="ru"): SelectSelector(
                        SelectSelectorConfig(
                            options=[{"value": k, "label": v} for k, v in CLOUD_SERVERS.items()],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_select(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle device selection from cloud list."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_key = user_input["device"]
            device_info = self._cloud_devices[selected_key]

            self._host = device_info["localip"]
            self._token = device_info["token"]
            self._model = device_info["model"]
            self._name = device_info["name"]

            # Validate connection
            try:
                info = await self._async_try_connect(self._host, self._token, self._model)
            except DeviceException:
                _LOGGER.warning(
                    "Cloud device %s (%s) not reachable locally, saving anyway",
                    self._name,
                    self._host,
                )
                info = {"model": self._model, "mac": device_info.get("mac")}
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception connecting to %s", self._host)
                errors["base"] = "cannot_connect"

            if not errors:
                # Set unique ID
                mac = device_info.get("mac") or (info and info.get("mac"))
                if mac:
                    mac_clean = mac.replace(":", "").replace("-", "").lower()
                    await self.async_set_unique_id(mac_clean)
                    self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})
                else:
                    await self.async_set_unique_id(f"{DOMAIN}_{self._host}")
                    self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._name or self._model or DEFAULT_NAME,
                    data={
                        CONF_HOST: self._host,
                        CONF_TOKEN: self._token,
                        CONF_MODEL: self._model,
                    },
                )

        # Build device selection list
        device_options = []
        for key, dev in self._cloud_devices.items():
            label = f"{dev['name']} — {dev['model']} ({dev['localip']})"
            device_options.append({"value": key, "label": label})

        return self.async_show_form(
            step_id="select",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle manual setup (IP + token)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._token = user_input[CONF_TOKEN]
            self._name = user_input.get(CONF_NAME, DEFAULT_NAME)
            self._model = user_input.get(CONF_MODEL)

            # Validate connection
            try:
                device_info = await self._async_try_connect(self._host, self._token, self._model)
            except DeviceException as ex:
                _LOGGER.error("Cannot connect to device: %s", ex)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID based on MAC address if available
                mac = device_info.get("mac")
                if mac:
                    await self.async_set_unique_id(mac.replace(":", "").lower())
                    self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})
                else:
                    await self.async_set_unique_id(f"{DOMAIN}_{self._host}")
                    self._abort_if_unique_id_configured()

                # Use detected model if not specified
                if not self._model and device_info.get("model"):
                    self._model = device_info["model"]

                return self.async_create_entry(
                    title=self._name or device_info.get("model", DEFAULT_NAME),
                    data={
                        CONF_HOST: self._host,
                        CONF_TOKEN: self._token,
                        CONF_MODEL: self._model,
                    },
                )

        # Pre-fill token from existing Xiaomi integrations if available
        default_token = ""
        default_host = ""
        imported = self._find_existing_xiaomi_entries()
        if imported:
            _LOGGER.debug("Found %d existing Xiaomi entries with tokens", len(imported))

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=default_host): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_TOKEN, default=default_token): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(CONF_NAME): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_MODEL): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                            sort=True,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        _LOGGER.warning(
            "Configuration via YAML is deprecated. Please use the UI to configure the integration"
        )

        host = import_config.get(CONF_HOST)
        if host:
            self._async_abort_entries_match({CONF_HOST: host})

        return await self.async_step_manual(import_config)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle reauthorization flow triggered by auth failure."""
        self._host = entry_data.get(CONF_HOST)
        self._model = entry_data.get(CONF_MODEL)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauth confirmation step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = user_input[CONF_TOKEN]

            try:
                await self._async_try_connect(self._host, token, self._model)
            except DeviceException:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={CONF_TOKEN: token},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOKEN): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
            description_placeholders={"host": self._host},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            host = user_input[CONF_HOST]
            token = user_input[CONF_TOKEN]
            model = user_input.get(CONF_MODEL)

            try:
                await self._async_try_connect(host, token, model)
            except DeviceException:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_HOST: host,
                        CONF_TOKEN: token,
                        CONF_MODEL: model,
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data.get(CONF_HOST)): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_TOKEN, default=entry.data.get(CONF_TOKEN)): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(CONF_MODEL, default=entry.data.get(CONF_MODEL)): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                            sort=True,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_try_connect(
        self, host: str, token: str, model: str | None = None
    ) -> dict[str, Any]:
        """Try to connect to the device and return device info."""
        device = Device(ip=host, token=token, model=model)

        info = await self.hass.async_add_executor_job(device.info)

        return {
            "model": info.model,
            "mac": info.mac_address,
            "firmware": info.firmware_version,
            "hardware": info.hardware_version,
        }

    async def _async_cloud_login(
        self, username: str, password: str, server: str
    ) -> dict[str, dict[str, Any]]:
        """Login to Xiaomi Cloud and return device list.

        Credentials are NOT stored — used only for this one-time fetch.
        """
        from miio.cloud import CloudInterface  # noqa: PLC0415

        cloud = await self.hass.async_add_executor_job(CloudInterface, username, password)
        raw_devices = await self.hass.async_add_executor_job(cloud.get_devices, server)

        # Convert CloudDeviceInfo objects to plain dicts
        devices: dict[str, dict[str, Any]] = {}
        for did, dev in raw_devices.items():
            # Skip child devices (sub-devices of gateways)
            if dev.parent_id:
                continue
            devices[did] = {
                "did": dev.did,
                "name": dev.name,
                "model": dev.model,
                "localip": dev.ip,
                "token": dev.token,
                "mac": dev.mac,
            }
        return devices

    def _find_existing_xiaomi_entries(self) -> list[dict[str, Any]]:
        """Find tokens from existing Xiaomi integrations (xiaomi_miio, xiaomi_miot)."""
        results = []
        for domain in _XIAOMI_DOMAINS:
            entries = self.hass.config_entries.async_entries(domain)
            for entry in entries:
                token = entry.data.get("token")
                host = entry.data.get("host")
                model = entry.data.get("model")
                if token and host:
                    results.append({"host": host, "token": token, "model": model, "source": domain})
        return results


class XiaomiMiioOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle options flow for Xiaomi Air Purifier NG."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=10,
                            max=300,
                            step=5,
                            unit_of_measurement="seconds",
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )
