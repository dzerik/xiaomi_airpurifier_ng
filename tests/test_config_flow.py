"""Tests for config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from miio import DeviceException
import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN


async def test_form_user(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
) -> None:
    """Test we get the user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_form_user_success(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
            CONF_NAME: "Test Purifier",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Purifier"
    assert result["data"] == {
        CONF_HOST: mock_config_entry_data[CONF_HOST],
        CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        CONF_MODEL: "zhimi.airpurifier.mc1",
    }


async def test_form_user_with_model(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test user flow with explicit model selection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
            CONF_MODEL: "zhimi.airpurifier.mb3",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MODEL] == "zhimi.airpurifier.mb3"


async def test_form_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we handle cannot connect error."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device"
    ) as mock_device:
        mock_device.return_value.info.side_effect = DeviceException("Cannot connect")

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: mock_config_entry_data[CONF_HOST],
                CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we handle unknown error."""
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device"
    ) as mock_device:
        mock_device.return_value.info.side_effect = Exception("Unknown error")

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: mock_config_entry_data[CONF_HOST],
                CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


async def test_form_already_configured(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we abort if already configured."""
    # Create first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    # Try to create second entry with same MAC
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reconfigure flow."""
    # Create initial entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    entry = result["result"]

    # Start reconfigure flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Submit new configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "192.168.1.200",
            CONF_TOKEN: "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
            CONF_MODEL: "zhimi.airpurifier.mb3",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    # Verify entry was updated
    assert entry.data[CONF_HOST] == "192.168.1.200"


async def test_reconfigure_flow_cannot_connect(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reconfigure flow with connection error."""
    # Create initial entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        },
    )

    entry = result["result"]

    # Start reconfigure flow with connection error
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device"
    ) as mock_device_fail:
        mock_device_fail.return_value.info.side_effect = DeviceException("Cannot connect")

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.200",
                CONF_TOKEN: "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_import_flow(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test import flow from YAML."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=mock_config_entry_data,
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == mock_config_entry_data[CONF_HOST]


async def test_reauth_flow(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reauthentication flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    # Create initial entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    # Start reauth flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=mock_config_entry_data,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    # Submit new token
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TOKEN: "new_token_12345678901234567890123",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"

    # Verify entry was updated
    assert entry.data[CONF_TOKEN] == "new_token_12345678901234567890123"


async def test_reauth_flow_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reauthentication flow with connection error."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    # Create initial entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device"
    ) as mock_device_fail:
        mock_device_fail.return_value.info.side_effect = DeviceException("Cannot connect")

        # Start reauth flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
            data=mock_config_entry_data,
        )

        # Submit invalid token
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_TOKEN: "bad_token_123456789012345678901234",
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}
