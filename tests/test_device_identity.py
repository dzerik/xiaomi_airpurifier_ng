"""Configuration identity contracts, exercised through Home Assistant flows."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr

from custom_components.xiaomi_miio_airpurifier_ng.const import CONF_MODEL, DOMAIN
from custom_components.xiaomi_miio_airpurifier_ng.coordinator import XiaomiAirPurifierCoordinator
from custom_components.xiaomi_miio_airpurifier_ng.entity import XiaomiMiioEntity
from tests.ha_helpers import MockConfigEntry

DATA = {CONF_HOST: "192.0.2.1", CONF_TOKEN: "0" * 32, CONF_MODEL: "zhimi.airpurifier.mc1"}


@pytest.mark.parametrize("mac", ["AA:BB:CC:DD:EE:FF", "aa-bb-cc-dd-ee-ff", "AABBCCDDEEFF"])
def test_normalized_identity(mac):
    from custom_components.xiaomi_miio_airpurifier_ng.identity import normalize_mac

    assert normalize_mac(mac) == "aabbccddeeff"


@pytest.mark.parametrize(
    "source", [config_entries.SOURCE_RECONFIGURE, config_entries.SOURCE_REAUTH]
)
async def test_different_device_does_not_change_entry(hass, mock_device, mock_setup_entry, source):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id="AA-BB-CC-DD-EE-FF")
    entry.add_to_hass(hass)
    original = dict(entry.data)
    mock_device.return_value.info.return_value = SimpleNamespace(
        model=DATA[CONF_MODEL],
        mac_address="00:11:22:33:44:55",
        firmware_version="1",
        hardware_version="1",
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": source, "entry_id": entry.entry_id},
        data=DATA if source == config_entries.SOURCE_REAUTH else None,
    )
    submission = {CONF_TOKEN: "1" * 32}
    if source == config_entries.SOURCE_RECONFIGURE:
        submission[CONF_HOST] = "192.0.2.2"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], submission)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert dict(entry.data) == original
    assert entry.unique_id == "AA-BB-CC-DD-EE-FF"


async def test_reconfigure_autodetects_and_preserves_identity(hass, mock_device, mock_setup_entry):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id="AA-BB-CC-DD-EE-FF")
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.2", CONF_TOKEN: "1" * 32}
    )
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_MODEL] == DATA[CONF_MODEL]
    assert entry.unique_id == "AA-BB-CC-DD-EE-FF"


async def test_unknown_detected_model_rejected(hass, mock_device, mock_setup_entry):
    mock_device.return_value.info.return_value._data["model"] = "zhimi.airpurifier.future"
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "manual"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.1", CONF_TOKEN: "0" * 32}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unsupported_model"}
    assert not hass.config_entries.async_entries(DOMAIN)


async def test_manual_matches_legacy_noncanonical_mac(hass, mock_device, mock_setup_entry):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id="AA-BB-CC-DD-EE-FF")
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"setup_method": "manual"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.1", CONF_TOKEN: "0" * 32}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_stored_unsupported_model_has_permanent_setup_error(hass):
    from homeassistant.exceptions import ConfigEntryError

    from custom_components.xiaomi_miio_airpurifier_ng import async_setup_entry

    entry = MockConfigEntry(domain=DOMAIN, data={**DATA, CONF_MODEL: "unknown.model"})
    entry.add_to_hass(hass)
    with pytest.raises(ConfigEntryError) as error:
        await async_setup_entry(hass, entry)
    assert error.value.translation_key == "unsupported_model"


async def test_cloud_with_only_unsupported_devices_rejected(hass):
    with patch(
        "custom_components.xiaomi_miio_airpurifier_ng.config_flow.XiaomiMiioConfigFlow._async_cloud_login",
        return_value={"1": {"model": "unknown.model", "name": "Other", "localip": "192.0.2.1"}},
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"setup_method": "cloud"}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"cloud_username": "test@example.com", "cloud_password": "fake", "cloud_server": "ru"},
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cloud_no_devices"}


async def test_late_info_keeps_one_device_and_entity_ids(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id="aabbccddeeff")
    entry.add_to_hass(hass)
    device = Mock()
    coordinator = XiaomiAirPurifierCoordinator(hass, entry, device)
    coordinator.data = {"power": "on", "aqi": 5}
    main = XiaomiMiioEntity(coordinator)
    registry = dr.async_get(hass)
    original = registry.async_get_or_create(config_entry_id=entry.entry_id, **main.device_info)
    # Legacy installs may have only used the entry id before info was available.
    registry.async_update_device(original.id, new_identifiers={(DOMAIN, entry.entry_id)})
    coordinator._get_status = Mock(return_value={"power": "on", "aqi": 5, "humidity": 50})
    device.info.return_value = SimpleNamespace(
        model=DATA[CONF_MODEL],
        mac_address="AA-BB-CC-DD-EE-FF",
        firmware_version="2.0",
        hardware_version="rev2",
    )
    await coordinator.async_refresh()
    late = XiaomiMiioEntity(coordinator, "humidity")
    registered = registry.async_get_or_create(config_entry_id=entry.entry_id, **late.device_info)
    assert registered.id == original.id
    assert len(dr.async_entries_for_config_entry(registry, entry.entry_id)) == 1
    assert registry.async_get(original.id).sw_version == "2.0"
    assert registry.async_get(original.id).hw_version == "rev2"
    assert main.unique_id == XiaomiMiioEntity(coordinator).unique_id == entry.entry_id
    assert late.unique_id == f"{entry.entry_id}_humidity"


async def test_late_info_updates_registry_without_new_entity(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id="aabbccddeeff")
    entry.add_to_hass(hass)
    device = Mock()
    coordinator = XiaomiAirPurifierCoordinator(hass, entry, device)
    main = XiaomiMiioEntity(coordinator)
    registry = dr.async_get(hass)
    registered = registry.async_get_or_create(config_entry_id=entry.entry_id, **main.device_info)
    coordinator._get_status = Mock(return_value={"power": "on"})
    device.info.return_value = SimpleNamespace(
        model=DATA[CONF_MODEL],
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="2.1",
        hardware_version="rev3",
    )
    await coordinator.async_refresh()
    assert registry.async_get(registered.id).sw_version == "2.1"
    assert len(dr.async_entries_for_config_entry(registry, entry.entry_id)) == 1
