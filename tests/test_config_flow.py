"""Tests for config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from miio import DeviceException

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN


async def test_form_user(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
) -> None:
    """Test we get the user form with setup method selection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_form_user_manual_path(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
) -> None:
    """Test user form → manual path."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"setup_method": "manual"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual"


async def test_form_user_cloud_path(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
) -> None:
    """Test user form → cloud path."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"setup_method": "cloud"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "cloud"


async def test_manual_success(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test successful manual flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Select manual setup
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"setup_method": "manual"},
    )

    # Fill manual form
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


async def test_manual_with_model(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test manual flow with explicit model selection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"setup_method": "manual"},
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


async def test_manual_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we handle cannot connect error in manual flow."""
    with patch("custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device") as mock_dev:
        mock_dev.return_value.info.side_effect = DeviceException("Cannot connect")

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"setup_method": "manual"},
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


async def test_manual_unknown_error(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we handle unknown error in manual flow."""
    with patch("custom_components.xiaomi_miio_airpurifier_ng.config_flow.Device") as mock_dev:
        mock_dev.return_value.info.side_effect = Exception("Unknown error")

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"setup_method": "manual"},
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


async def test_manual_already_configured(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test we abort if already configured."""
    # Create first entry via manual
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "manual"}
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
        result["flow_id"], {"setup_method": "manual"}
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


async def test_cloud_login_error(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
) -> None:
    """Test cloud login error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "cloud"}
    )

    with patch(
        "miio.cloud.CloudInterface",
        side_effect=Exception("Login failed"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "cloud_username": "user@test.com",
                "cloud_password": "wrong_pass",
                "cloud_server": "ru",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "cloud"
    assert result["errors"] == {"base": "cloud_login_error"}


async def test_cloud_no_devices(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
) -> None:
    """Test cloud login with no devices."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "cloud"}
    )

    mock_cloud = MagicMock()
    mock_cloud.get_devices.return_value = {}

    with patch(
        "miio.cloud.CloudInterface",
        return_value=mock_cloud,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "cloud_username": "user@test.com",
                "cloud_password": "pass",
                "cloud_server": "ru",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cloud_no_devices"}


async def test_cloud_success(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
) -> None:
    """Test full cloud flow: login → select → create entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "cloud"}
    )

    # Mock cloud device info
    mock_dev_info = MagicMock()
    mock_dev_info.did = "12345"
    mock_dev_info.name = "Air Purifier 2S"
    mock_dev_info.model = "zhimi.airpurifier.mc1"
    mock_dev_info.ip = "192.168.1.100"
    mock_dev_info.token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    mock_dev_info.mac = "AA:BB:CC:DD:EE:FF"
    mock_dev_info.parent_id = ""

    mock_cloud = MagicMock()
    mock_cloud.get_devices.return_value = {"12345": mock_dev_info}

    with patch(
        "miio.cloud.CloudInterface",
        return_value=mock_cloud,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "cloud_username": "user@test.com",
                "cloud_password": "pass",
                "cloud_server": "ru",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "select"

    # Select the device
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"device": "12345"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Air Purifier 2S"
    assert result["data"][CONF_HOST] == "192.168.1.100"
    assert result["data"][CONF_TOKEN] == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    assert result["data"][CONF_MODEL] == "zhimi.airpurifier.mc1"


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_device: MagicMock,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reconfigure flow."""
    # Create initial entry via manual
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "manual"}
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
        result["flow_id"], {"setup_method": "manual"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: mock_config_entry_data[CONF_HOST],
            CONF_TOKEN: mock_config_entry_data[CONF_TOKEN],
        },
    )
    entry = result["result"]

    # Start reconfigure with connection error
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

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        unique_id="aabbccddeeff",
    )
    entry.add_to_hass(hass)

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

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_TOKEN: "new_token_12345678901234567890123"},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == "new_token_12345678901234567890123"


async def test_reauth_flow_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: MagicMock,
    mock_config_entry_data: dict,
) -> None:
    """Test reauthentication flow with connection error."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

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

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
            data=mock_config_entry_data,
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_TOKEN: "bad_token_123456789012345678901234"},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}
