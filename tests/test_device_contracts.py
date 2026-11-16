"""Exercise real driver setters and status objects at the network boundary."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.exceptions import ServiceValidationError
from miio.integrations.fan.dmaker.fan_miot import FanStatus1C
from miio.integrations.fan.zhimi.fan import FanStatus

from custom_components.xiaomi_miio_airpurifier_ng import _create_coordinator
from custom_components.xiaomi_miio_airpurifier_ng.const import (
    DOMAIN,
    SUPPORTED_MODELS_AIRHUMIDIFIER,
)
from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import create_device
from custom_components.xiaomi_miio_airpurifier_ng.fans.purifier import XiaomiAirPurifierFan
from custom_components.xiaomi_miio_airpurifier_ng.fans.standing import XiaomiStandingFan
from custom_components.xiaomi_miio_airpurifier_ng.humidifier import XiaomiAirHumidifier
from custom_components.xiaomi_miio_airpurifier_ng.number import (
    NUMBER_DESCRIPTIONS,
    XiaomiMiioNumber,
)
from custom_components.xiaomi_miio_airpurifier_ng.select import (
    SELECT_DESCRIPTIONS,
    XiaomiMiioSelect,
)
from tests.ha_helpers import MockConfigEntry


@pytest.fixture
def driver_coordinator(hass):
    """Keep real driver code; substitute only packets sent to the device."""

    def make(model, data=None):
        entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id="aabbccddeeff",
            title="Test",
            data={"host": "192.0.2.1", "token": "0" * 32, "model": model},
        )
        device = create_device("192.0.2.1", "0" * 32, model)
        sent = []

        def send(method, params=None):
            sent.append((method, params))
            return (
                [{"did": p["did"], "code": 0} for p in params]
                if method == "set_properties"
                else ["ok"]
            )

        device.send = send
        coordinator = _create_coordinator(hass, entry, device, model)
        coordinator.data = data if data is not None else {"power": "on", "mode": "Normal"}
        coordinator.async_request_refresh = AsyncMock()
        coordinator._device_info = SimpleNamespace(
            mac_address="AA:BB:CC:DD:EE:FF", firmware_version="1", hardware_version="1"
        )
        return coordinator, sent

    return make


@pytest.mark.parametrize(
    "percentage,level", [(1, 1), (33, 1), (34, 2), (66, 2), (67, 3), (99, 3), (100, 3)]
)
async def test_three_speed_write_boundaries(driver_coordinator, percentage, level):
    coordinator, sent = driver_coordinator("dmaker.fan.1c")
    await XiaomiStandingFan(coordinator).async_set_percentage(percentage)
    writes = [(prop["did"], prop["value"]) for method, props in sent for prop in props]
    assert writes == [("fan_level", level)]


@pytest.mark.parametrize("platform", ["humidifier", "number"])
async def test_humidity_platforms_use_same_prerequisite(driver_coordinator, platform):
    from custom_components.xiaomi_miio_airpurifier_ng.number import (
        NUMBER_DESCRIPTIONS,
        XiaomiMiioNumber,
    )

    coordinator, sent = driver_coordinator("deerma.humidifier.jsqs", {"power": "on", "mode": "Low"})
    if platform == "humidifier":
        await XiaomiAirHumidifier(coordinator).async_set_humidity(55)
    else:
        description = next(d for d in NUMBER_DESCRIPTIONS if d.key == "target_humidity")
        await XiaomiMiioNumber(coordinator, description).async_set_native_value(55)
    writes = [(prop["did"], prop["value"]) for method, props in sent for prop in props]
    assert writes == [("mode", 4), ("target_humidity", 55)]
    assert coordinator.data["mode"] == "Auto"
    assert coordinator.data["target_humidity"] == 55


async def test_partial_humidity_failure_refreshes_actual_state(driver_coordinator):
    from homeassistant.exceptions import HomeAssistantError

    coordinator, sent = driver_coordinator("deerma.humidifier.jsqs", {"power": "on", "mode": "Low"})
    calls = []

    def send(method, params):
        calls.append(params[0]["did"])
        return [{"code": 0 if len(calls) == 1 else -1}]

    coordinator.device.send = send
    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_humidity(55)
    assert calls == ["mode", "target_humidity"]
    assert coordinator.data == {"power": "on", "mode": "Low"}
    coordinator.async_request_refresh.assert_awaited_once()


async def test_failed_prerequisite_stops_humidity_sequence(driver_coordinator):
    from homeassistant.exceptions import HomeAssistantError

    coordinator, sent = driver_coordinator("deerma.humidifier.jsqs", {"power": "on", "mode": "Low"})
    calls = []

    def send(method, params):
        calls.append(params[0]["did"])
        return [{"code": -1}]

    coordinator.device.send = send
    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_humidity(55)
    assert calls == ["mode"]


async def test_optional_number_discovery_is_idempotent(driver_coordinator):
    from unittest.mock import Mock

    from custom_components.xiaomi_miio_airpurifier_ng.number import async_setup_entry

    coordinator, sent = driver_coordinator("zhimi.airpurifier.ma4", {"power": "on"})
    entry = coordinator.config_entry
    entry.runtime_data = coordinator
    added = Mock()
    await async_setup_entry(coordinator.hass, entry, added)
    assert not added.called
    coordinator.async_set_updated_data({"power": "on", "fan_level": 2})
    coordinator.async_set_updated_data({"power": "on", "fan_level": 3})
    assert added.call_count == 1
    assert [entity.entity_description.key for entity in added.call_args.args[0]] == ["fan_level"]


@pytest.mark.parametrize(
    "model,percentage,expected",
    [
        ("zhimi.airfresh.va2", 33, [("set_mode", ["low"])]),
        ("zhimi.airfresh.va4", 100, [("set_mode", ["strong"])]),
        ("dmaker.airfresh.a1", 50, [("set_mode", ["favourite"]), ("set_favourite_speed", [75])]),
        (
            "dmaker.airfresh.t2017",
            50,
            [("set_mode", ["favourite"]), ("set_favourite_speed", [180])],
        ),
    ],
)
async def test_air_fresh_manual_speed_packets(driver_coordinator, model, percentage, expected):
    from custom_components.xiaomi_miio_airpurifier_ng.fans.air_fresh import XiaomiAirFreshFan

    coordinator, sent = driver_coordinator(model)
    await XiaomiAirFreshFan(coordinator).async_set_percentage(percentage)
    assert sent == expected


async def test_air_fresh_turn_on_and_zero(driver_coordinator):
    from custom_components.xiaomi_miio_airpurifier_ng.fans.air_fresh import XiaomiAirFreshFan

    coordinator, sent = driver_coordinator("dmaker.airfresh.a1", {"power": "off"})
    entity = XiaomiAirFreshFan(coordinator)
    await entity.async_turn_on(percentage=50)
    assert sent == [
        ("set_power", [True]),
        ("set_mode", ["favourite"]),
        ("set_favourite_speed", [75]),
    ]
    sent.clear()
    await entity.async_set_percentage(0)
    assert sent == [("set_power", [False])]


async def test_air_fresh_rejects_speed_before_power(driver_coordinator):
    from homeassistant.exceptions import ServiceValidationError

    from custom_components.xiaomi_miio_airpurifier_ng.fans.air_fresh import XiaomiAirFreshFan

    coordinator, sent = driver_coordinator("dmaker.airfresh.a1", {"power": "off"})
    with pytest.raises(ServiceValidationError):
        await XiaomiAirFreshFan(coordinator).async_turn_on(percentage=101)
    assert not sent


@pytest.mark.parametrize("model", ["zhimi.airpurifier.mb4", "zhimi.airp.mb4a"])
@pytest.mark.parametrize("percentage,rpm", [(1, 320), (50, 1300), (100, 2300)])
async def test_purifier_rpm_manual_speed(driver_coordinator, model, percentage, rpm):
    from homeassistant.components.fan import FanEntityFeature

    coordinator, sent = driver_coordinator(model, {"power": "on", "mode": "Auto"})
    entity = XiaomiAirPurifierFan(coordinator)
    assert entity.supported_features & FanEntityFeature.SET_SPEED
    await entity.async_set_percentage(percentage)
    writes = [(prop["did"], prop["value"]) for method, props in sent for prop in props]
    assert writes == [("mode", 2), ("favorite_rpm", rpm)]
    from unittest.mock import Mock

    from miio.integrations.airpurifier.zhimi.airpurifier_miot import AirPurifierMiotStatus

    raw = dict.fromkeys(coordinator.device._get_mapping())
    raw.update(power=True, mode=2, favorite_rpm=rpm)
    coordinator.device.status = Mock(return_value=AirPurifierMiotStatus(raw, model))
    coordinator.data = coordinator._get_status()
    assert entity.percentage == percentage
    assert entity.speed_count == 201


@pytest.mark.parametrize(
    "model",
    [
        "dmaker.fan.1c",
        "dmaker.fan.p8",
        "dmaker.fan.p9",
        "dmaker.fan.p10",
        "dmaker.fan.p11",
        "dmaker.fan.p15",
        "dmaker.fan.p18",
        "dmaker.fan.p33",
    ],
)
async def test_dmaker_led_switch_uses_light_property(driver_coordinator, model):
    from custom_components.xiaomi_miio_airpurifier_ng.switch import (
        SWITCH_DESCRIPTIONS,
        XiaomiMiioSwitch,
    )

    coordinator, sent = driver_coordinator(model, {"power": "on", "led": True})
    description = next(d for d in SWITCH_DESCRIPTIONS if d.key == "led")
    await XiaomiMiioSwitch(coordinator, description).async_turn_on()
    assert sent[0][0] == "set_properties"
    assert sent[0][1][0]["did"] == "light"
    assert sent[0][1][0]["value"] is True


async def test_unsupported_miot_switches_not_discovered(driver_coordinator):
    from unittest.mock import Mock

    from miio.integrations.airpurifier.zhimi.airpurifier_miot import AirPurifierMiotStatus

    from custom_components.xiaomi_miio_airpurifier_ng.switch import async_setup_entry

    coordinator, sent = driver_coordinator("zhimi.airpurifier.ma4")
    raw = dict.fromkeys(coordinator.device._get_mapping())
    raw.update(power=True, mode=0)
    coordinator.device.status = Mock(
        return_value=AirPurifierMiotStatus(raw, "zhimi.airpurifier.ma4")
    )
    coordinator.data = coordinator._get_status()
    entry = coordinator.config_entry
    entry.runtime_data = coordinator
    added = Mock()
    await async_setup_entry(coordinator.hass, entry, added)
    keys = [e.entity_description.key for call in added.call_args_list for e in call.args[0]]
    assert "anion" not in keys
    assert "gestures" not in keys
    assert "set_anion" not in coordinator.profile.commands
    assert "set_gestures" not in coordinator.profile.commands


@pytest.mark.parametrize("model", ["dmaker.fan.p15", "dmaker.fan.p18"])
async def test_unimplemented_alias_angle_not_advertised(driver_coordinator, model):
    from unittest.mock import Mock

    from custom_components.xiaomi_miio_airpurifier_ng.number import async_setup_entry

    coordinator, sent = driver_coordinator(model, {"power": "on", "angle": 60})
    entry = coordinator.config_entry
    entry.runtime_data = coordinator
    added = Mock()
    await async_setup_entry(coordinator.hass, entry, added)
    assert not added.called
    assert "set_angle" not in coordinator.profile.commands


@pytest.mark.parametrize("level,expected", [(1, 33), (2, 66), (3, 100)])
def test_1c_reports_percent_not_level(driver_coordinator, level, expected):
    coordinator, _ = driver_coordinator("dmaker.fan.1c")
    raw = dict.fromkeys(coordinator.device._get_mapping(), 0)
    raw.update(power=True, fan_level=level, mode=0)
    coordinator.device.status = Mock(return_value=FanStatus1C(raw))
    coordinator.data = coordinator._get_status()
    assert XiaomiStandingFan(coordinator).percentage == expected


def test_legacy_reports_direct_speed_not_motor_rpm(driver_coordinator):
    coordinator, _ = driver_coordinator("zhimi.fan.v2")
    raw = {
        "power": "on",
        "speed": 850,
        "speed_level": 35,
        "natural_level": 0,
        "angle_enable": "off",
        "angle": 30,
        "led_b": 0,
        "buzzer": "off",
        "child_lock": "off",
        "use_time": 0,
        "ac_power": "on",
        "poweroff_time": 0,
    }
    coordinator.device.status = Mock(return_value=FanStatus(raw))
    coordinator.data = coordinator._get_status()
    assert XiaomiStandingFan(coordinator).percentage == 35


@pytest.mark.parametrize(
    "model,entity_class",
    [
        ("dmaker.fan.1c", XiaomiStandingFan),
        ("zhimi.airpurifier.ma4", XiaomiAirPurifierFan),
        ("zhimi.airpurifier.v2", XiaomiAirPurifierFan),
    ],
)
async def test_zero_speed_turns_power_off(driver_coordinator, model, entity_class):
    coordinator, sent = driver_coordinator(model, {"power": "on", "mode": "Normal", "speed": 50})
    entity = entity_class(coordinator)
    await entity.async_set_percentage(0)
    assert coordinator.data["power"] == "off"
    assert sent


@pytest.mark.parametrize(
    "model,entity_class",
    [("dmaker.fan.1c", XiaomiStandingFan), ("zhimi.airpurifier.ma4", XiaomiAirPurifierFan)],
)
async def test_turn_on_applies_requested_speed(driver_coordinator, model, entity_class):
    coordinator, sent = driver_coordinator(model, {"power": "off", "mode": "Auto", "fan_level": 1})
    entity = entity_class(coordinator)
    await entity.async_turn_on(percentage=75)
    writes = [prop for method, props in sent if method == "set_properties" for prop in props]
    assert any(p["did"] == "power" and p["value"] in (True, "on") for p in writes)
    assert any(p["did"] == "fan_level" and p["value"] == 3 for p in writes)


@pytest.mark.parametrize(
    "model", ["dmaker.fan.p5", "dmaker.fan.1c", "dmaker.fan.p9", "zhimi.fan.v2"]
)
def test_current_preset_belongs_to_advertised_modes(driver_coordinator, model):
    coordinator, _ = driver_coordinator(
        model,
        {"power": "on", "mode": "Normal", "speed": 50, "natural_speed": 0, "direct_speed": 50},
    )
    entity = XiaomiStandingFan(coordinator)
    assert entity.preset_mode is None or entity.preset_mode in entity.preset_modes
    assert not any(mode.startswith("Level") for mode in entity.preset_modes)


@pytest.mark.parametrize(
    "model,key,option,method,expected",
    [
        ("zhimi.airpurifier.v2", "led_brightness", "dim", "set_led_b", [1]),
        ("shuii.humidifier.jsq001", "led_brightness", "off", "set_brightness", [0]),
        ("dmaker.airfresh.t2017", "ptc_level", "medium", "set_ptc_level", ["medium"]),
        ("dmaker.airfresh.t2017", "display_orientation", "left", "set_screen_direction", ["left"]),
    ],
)
async def test_select_encodes_driver_enum(driver_coordinator, model, key, option, method, expected):
    coordinator, sent = driver_coordinator(model)
    entity = XiaomiMiioSelect(coordinator, next(d for d in SELECT_DESCRIPTIONS if d.key == key))
    await entity.async_select_option(option)
    assert sent == [(method, expected)]


async def test_jsq001_rejects_unsupported_humidity_before_network(driver_coordinator):
    coordinator, sent = driver_coordinator("shuii.humidifier.jsq001")
    with pytest.raises(ServiceValidationError):
        await XiaomiAirHumidifier(coordinator).async_set_humidity(50)
    assert sent == []


@pytest.mark.parametrize("value", [30, 70, 80])
async def test_dehumidifier_number_rejects_invalid_targets(driver_coordinator, value):
    coordinator, sent = driver_coordinator(
        "nwt.derh.wdh318efw1", {"power": "on", "mode": "Auto", "target_humidity": 50}
    )
    entity = XiaomiMiioNumber(
        coordinator, next(d for d in NUMBER_DESCRIPTIONS if d.key == "target_humidity")
    )
    assert (entity.native_min_value, entity.native_max_value) == (40, 60)
    with pytest.raises(ServiceValidationError):
        await entity.async_set_native_value(value)
    assert sent == []


async def test_airdog_uses_combined_mode_speed_command(driver_coordinator):
    coordinator, sent = driver_coordinator(
        "airdog.airpurifier.x3", {"power": "on", "mode": "Auto", "speed": 1}
    )
    await XiaomiAirPurifierFan(coordinator).async_set_percentage(100)
    assert sent[-1] == ("set_wind", [1, 4])


def test_powered_off_fan_does_not_report_previous_speed(driver_coordinator):
    coordinator, _ = driver_coordinator("dmaker.fan.p5", {"power": "off", "speed": 75})
    assert XiaomiStandingFan(coordinator).percentage == 0


async def test_legacy_timer_converts_minutes_to_seconds(driver_coordinator):
    coordinator, sent = driver_coordinator("zhimi.fan.v2", {"delay_off_countdown": 120})
    entity = XiaomiMiioNumber(
        coordinator, next(d for d in NUMBER_DESCRIPTIONS if d.key == "delay_off_countdown")
    )
    assert entity.native_value == 2
    await entity.async_set_native_value(3)
    assert sent == [("set_poweroff_time", [180])]


def test_airdog_poll_preserves_pollution_and_speed(driver_coordinator):
    from miio.integrations.airpurifier.airdog.airpurifier_airdog import AirDogStatus

    coordinator, _ = driver_coordinator("airdog.airpurifier.x3")
    coordinator.device.status = Mock(
        return_value=AirDogStatus(
            {
                "power": "on",
                "mode": "manual",
                "speed": 3,
                "lock": "unlock",
                "clean": "n",
                "pm": 12,
                "hcho": 0,
            }
        )
    )
    data = coordinator._get_status()
    assert data["aqi"] == 12
    assert data["speed"] == 3


async def test_invalid_turn_on_preset_does_not_power_device(driver_coordinator):
    coordinator, sent = driver_coordinator("zhimi.airpurifier.ma4", {"power": "off"})
    with pytest.raises(ServiceValidationError):
        await XiaomiAirPurifierFan(coordinator).async_turn_on(preset_mode="unsupported")
    assert sent == []


@pytest.mark.parametrize("model", SUPPORTED_MODELS_AIRHUMIDIFIER)
async def test_humidifier_modes_use_real_driver_enum(driver_coordinator, model):
    coordinator, sent = driver_coordinator(model, {"power": "on"})
    entity = XiaomiAirHumidifier(coordinator)
    for mode in entity.available_modes:
        await entity.async_set_mode(mode)
        assert entity.mode == mode
    assert sent


@pytest.mark.parametrize(
    "model,preset",
    [
        ("zhimi.fan.v2", "Nature"),
        ("dmaker.fan.1c", "Nature"),
        ("dmaker.fan.p5", "Nature"),
        ("dmaker.fan.p9", "Nature"),
        ("leshow.fan.ss4", "Sleep"),
    ],
)
async def test_real_automatic_presets_are_executable(driver_coordinator, model, preset):
    coordinator, sent = driver_coordinator(model, {"power": "off", "direct_speed": 50})
    entity = XiaomiStandingFan(coordinator)
    assert preset in entity.preset_modes
    await entity.async_turn_on(preset_mode=preset)
    assert coordinator.data["power"] == "on"
    assert sent
