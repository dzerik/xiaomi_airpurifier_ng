"""Stable device identities shared by discovery, entities, and polling."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


def normalize_mac(value: str) -> str:
    """Return a canonical MAC, rejecting malformed addresses."""
    normalized = value.replace(":", "").replace("-", "").lower()
    if len(normalized) != 12 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError("Invalid MAC address")
    return normalized


def known_macs(hass: HomeAssistant, entry: ConfigEntry) -> set[str]:
    """Find MAC aliases without changing an existing config entry unique id."""
    candidates = [entry.unique_id] if entry.unique_id else []
    for device in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id):
        candidates.extend(value for domain, value in device.identifiers if domain == DOMAIN)
    result = set()
    for candidate in candidates:
        try:
            result.add(normalize_mac(candidate))
        except ValueError:
            continue  # Old host/entry-id based unique ids are deliberately preserved.
    return result


def device_identifiers(hass: HomeAssistant, entry: ConfigEntry, info: Any) -> set[tuple[str, str]]:
    """Include the stable id and legacy aliases so late discovery cannot split devices."""
    identifiers = {(DOMAIN, entry.entry_id)}
    if entry.unique_id:
        identifiers.add((DOMAIN, entry.unique_id))
    registry = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        identifiers.update(device.identifiers)
    if info and info.mac_address:
        mac = normalize_mac(info.mac_address)
        expected = known_macs(hass, entry)
        if not expected or mac in expected:
            identifiers.add((DOMAIN, mac))
    return identifiers


def update_device_metadata(hass: HomeAssistant, entry: ConfigEntry, info: Any, model: str) -> None:
    """Refresh existing registry records even when no new entity is discovered."""
    if info is None:
        return
    registry = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        registry.async_update_device(
            device.id,
            merge_identifiers=device_identifiers(hass, entry, info),
            sw_version=info.firmware_version,
            hw_version=info.hardware_version,
            model_id=model,
        )
