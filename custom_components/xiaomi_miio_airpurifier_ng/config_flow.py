"""Config flow for Xiaomi Air Purifier NG integration."""

from __future__ import annotations

import logging
from typing import Any

from miio import Device, DeviceException
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_MODEL,
    DEFAULT_NAME,
    DOMAIN,
    SUPPORTED_MODELS,
)

_LOGGER = logging.getLogger(__name__)


class XiaomiMiioConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Air Purifier NG."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._token: str | None = None
        self._name: str | None = None
        self._model: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._token = user_input[CONF_TOKEN]
            self._name = user_input.get(CONF_NAME, DEFAULT_NAME)
            self._model = user_input.get(CONF_MODEL)

            # Validate connection
            try:
                device_info = await self._async_try_connect(
                    self._host, self._token, self._model
                )
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
                    self._abort_if_unique_id_configured(
                        updates={CONF_HOST: self._host}
                    )
                else:
                    # Fall back to host-based unique ID
                    await self.async_set_unique_id(f"{DOMAIN}_{self._host}")
                    self._abort_if_unique_id_configured()

                # Use detected model if not specified
                if not self._model and device_info.get("model"):
                    self._model = device_info["model"]

                # Create the entry
                return self.async_create_entry(
                    title=self._name or device_info.get("model", DEFAULT_NAME),
                    data={
                        CONF_HOST: self._host,
                        CONF_TOKEN: self._token,
                        CONF_MODEL: self._model,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_TOKEN): TextSelector(
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

    async def async_step_import(
        self, import_config: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        _LOGGER.warning(
            "Configuration via YAML is deprecated. "
            "Please use the UI to configure the integration"
        )

        # Check if already configured
        host = import_config.get(CONF_HOST)
        if host:
            self._async_abort_entries_match({CONF_HOST: host})

        return await self.async_step_user(import_config)

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
                    vol.Required(
                        CONF_HOST, default=entry.data.get(CONF_HOST)
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                    vol.Required(
                        CONF_TOKEN, default=entry.data.get(CONF_TOKEN)
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(
                        CONF_MODEL, default=entry.data.get(CONF_MODEL)
                    ): SelectSelector(
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

        # Run info() in executor to avoid blocking
        info = await self.hass.async_add_executor_job(device.info)

        return {
            "model": info.model,
            "mac": info.mac_address,
            "firmware": info.firmware_version,
            "hardware": info.hardware_version,
        }
