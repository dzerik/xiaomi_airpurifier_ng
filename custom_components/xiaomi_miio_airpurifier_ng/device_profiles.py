"""Explicit protocol and capability profiles for supported Xiaomi devices."""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any

from miio import (
    AirDehumidifier,
    AirDogX3,
    AirFresh,
    AirFreshA1,
    AirFreshT2017,
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierJsqs,
    AirHumidifierMiot,
    AirHumidifierMjjsq,
    AirPurifier,
    AirPurifierMiot,
    Device,
    Fan,
    Fan1C,
    FanLeshow,
    FanMiot,
    FanP5,
)

from . import const as c


class UnsupportedModelError(ValueError):
    """The model has no verified integration profile."""


class SpeedKind(StrEnum):
    """Interpretation of a driver's speed value."""

    NONE = "none"
    LEGACY = "legacy"
    LEVELS = "levels"
    PERCENTAGE = "percentage"
    PURIFIER = "purifier"
    AIRDOG = "airdog"


@dataclass(frozen=True)
class HumidityControl:
    """Valid target humidity and any prerequisite device mode."""

    minimum: int
    maximum: int
    step: int = 1
    mode: Enum | None = None
    mode_delay: float = 0

    def normalize(self, value: int) -> int:
        """Validate before quantizing, so invalid requests cannot be clamped silently."""
        if type(value) is not int or not self.minimum <= value <= self.maximum:
            raise ValueError(f"Humidity must be between {self.minimum} and {self.maximum}")
        return round(value / self.step) * self.step if self.step > 1 else value


@dataclass(frozen=True)
class DeviceProfile:
    """Small, immutable description of a real driver's public capabilities."""

    category: c.DeviceCategory
    driver: type[Device]
    features: int
    attributes: Mapping[str, str]
    mode_enum: type[Enum] | None
    speed_kind: SpeedKind = SpeedKind.NONE
    speed_range: tuple[int, int] | None = None
    humidity: HumidityControl | None = None
    select_enums: Mapping[str, type[Enum]] = field(default_factory=lambda: MappingProxyType({}))
    commands: frozenset[str] = frozenset()
    device_options: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    preset_modes: tuple[str, ...] = ()
    command_aliases: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    speed_modes: tuple[str, ...] = ()
    delay_unit_seconds: bool = False
    delay_max_minutes: int = 480
    speed_step: int = 1


JSQS_MAPPING = {
    "power": {"siid": 2, "piid": 1},
    "fault": {"siid": 2, "piid": 2},
    "mode": {"siid": 2, "piid": 5},
    "target_humidity": {"siid": 2, "piid": 6},
    "relative_humidity": {"siid": 3, "piid": 1},
    "temperature": {"siid": 3, "piid": 7},
    "buzzer": {"siid": 5, "piid": 1},
    "led_light": {"siid": 6, "piid": 1},
    "water_shortage_fault": {"siid": 7, "piid": 1},
    "tank_filed": {"siid": 7, "piid": 2},
    "overwet_protect": {"siid": 7, "piid": 3},
}

# Aliases use the same known protocol; new model names never get a generic Device.
_DRIVER_GROUPS = (
    (AirPurifier, c.SUPPORTED_MODELS_AIRPURIFIER, "AIRPURIFIER", c.DeviceCategory.PURIFIER),
    (AirHumidifier, c.SUPPORTED_MODELS_AIRHUMIDIFIER, "AIRHUMIDIFIER", c.DeviceCategory.HUMIDIFIER),
    (AirFresh, c.SUPPORTED_MODELS_AIRFRESH, "AIRFRESH", c.DeviceCategory.AIR_FRESH),
    (Fan, c.SUPPORTED_MODELS_FAN, "FAN", c.DeviceCategory.FAN),
    (
        AirDehumidifier,
        [c.MODEL_AIRDEHUMIDIFIER_V1],
        "AIRDEHUMIDIFIER",
        c.DeviceCategory.DEHUMIDIFIER,
    ),
)
_DRIVER_OVERRIDES = {
    **dict.fromkeys(c.PURIFIER_MIOT, AirPurifierMiot),
    **dict.fromkeys(
        [
            c.MODEL_AIRPURIFIER_AIRDOG_X3,
            c.MODEL_AIRPURIFIER_AIRDOG_X5,
            c.MODEL_AIRPURIFIER_AIRDOG_X7SM,
        ],
        AirDogX3,
    ),
    **dict.fromkeys(c.HUMIDIFIER_MIOT, AirHumidifierMiot),
    **dict.fromkeys(
        [c.MODEL_AIRHUMIDIFIER_MJJSQ, c.MODEL_AIRHUMIDIFIER_JSQ, c.MODEL_AIRHUMIDIFIER_JSQ1],
        AirHumidifierMjjsq,
    ),
    **dict.fromkeys(
        [
            c.MODEL_AIRHUMIDIFIER_JSQ2W,
            c.MODEL_AIRHUMIDIFIER_JSQ3,
            c.MODEL_AIRHUMIDIFIER_JSQ5,
            c.MODEL_AIRHUMIDIFIER_JSQS,
        ],
        AirHumidifierJsqs,
    ),
    c.MODEL_AIRHUMIDIFIER_JSQ001: AirHumidifierJsq,
    c.MODEL_AIRFRESH_A1: AirFreshA1,
    c.MODEL_AIRFRESH_T2017: AirFreshT2017,
    **dict.fromkeys([c.MODEL_FAN_1C, c.MODEL_FAN_P8], Fan1C),
    c.MODEL_FAN_P5: FanP5,
    **dict.fromkeys(
        [
            c.MODEL_FAN_P9,
            c.MODEL_FAN_P10,
            c.MODEL_FAN_P11,
            c.MODEL_FAN_P15,
            c.MODEL_FAN_P18,
            c.MODEL_FAN_P33,
        ],
        FanMiot,
    ),
    c.MODEL_FAN_LESHOW_SS4: FanLeshow,
}
_UI_OVERRIDES = {
    c.MODEL_AIRPURIFIER_PRO: "AIRPURIFIER_PRO",
    c.MODEL_AIRPURIFIER_PRO_V7: "AIRPURIFIER_PRO_V7",
    c.MODEL_AIRPURIFIER_2S: "AIRPURIFIER_2S",
    c.MODEL_AIRPURIFIER_2H: "AIRPURIFIER_2H",
    c.MODEL_AIRPURIFIER_V3: "AIRPURIFIER_V3",
    **dict.fromkeys(c.PURIFIER_MIOT, "AIRPURIFIER_3"),
    c.MODEL_AIRHUMIDIFIER_CA1: "AIRHUMIDIFIER_CA_AND_CB",
    c.MODEL_AIRHUMIDIFIER_CB1: "AIRHUMIDIFIER_CA_AND_CB",
    c.MODEL_AIRHUMIDIFIER_CB2: "AIRHUMIDIFIER_CA_AND_CB",
    **dict.fromkeys(c.HUMIDIFIER_MIOT, "AIRHUMIDIFIER_CA4"),
    c.MODEL_AIRHUMIDIFIER_MJJSQ: "AIRHUMIDIFIER_MJJSQ",
    c.MODEL_AIRHUMIDIFIER_JSQ: "AIRHUMIDIFIER_MJJSQ",
    c.MODEL_AIRHUMIDIFIER_JSQ1: "AIRHUMIDIFIER_JSQ1",
    c.MODEL_AIRHUMIDIFIER_JSQ2W: "AIRHUMIDIFIER_JSQS",
    c.MODEL_AIRHUMIDIFIER_JSQS: "AIRHUMIDIFIER_JSQS",
    c.MODEL_AIRHUMIDIFIER_JSQ3: "AIRHUMIDIFIER_JSQ5",
    c.MODEL_AIRHUMIDIFIER_JSQ5: "AIRHUMIDIFIER_JSQ5",
    c.MODEL_AIRHUMIDIFIER_JSQ001: "AIRHUMIDIFIER_JSQ",
    c.MODEL_AIRFRESH_A1: "AIRFRESH_A1",
    c.MODEL_AIRFRESH_T2017: "AIRFRESH_T2017",
    c.MODEL_AIRFRESH_VA4: "AIRFRESH_VA4",
    **dict.fromkeys([c.MODEL_FAN_1C, c.MODEL_FAN_P8], "FAN_1C"),
    **dict.fromkeys(
        [
            c.MODEL_FAN_P5,
            c.MODEL_FAN_P9,
            c.MODEL_FAN_P10,
            c.MODEL_FAN_P11,
            c.MODEL_FAN_P15,
            c.MODEL_FAN_P18,
            c.MODEL_FAN_P33,
        ],
        "FAN_P5",
    ),
    c.MODEL_FAN_LESHOW_SS4: "FAN_LESHOW_SS4",
}
_FEATURE_COMMANDS = {
    c.FEATURE_SET_BUZZER: "set_buzzer",
    c.FEATURE_SET_LED: "set_led",
    c.FEATURE_SET_CHILD_LOCK: "set_child_lock",
    c.FEATURE_SET_LED_BRIGHTNESS: "set_led_brightness",
    c.FEATURE_SET_FAVORITE_LEVEL: "set_favorite_level",
    c.FEATURE_SET_AUTO_DETECT: "set_auto_detect",
    c.FEATURE_SET_LEARN_MODE: "set_learn_mode",
    c.FEATURE_SET_VOLUME: "set_volume",
    c.FEATURE_SET_EXTRA_FEATURES: "set_extra_features",
    c.FEATURE_SET_TARGET_HUMIDITY: "set_target_humidity",
    c.FEATURE_SET_DRY: "set_dry",
    c.FEATURE_SET_OSCILLATION_ANGLE: "set_angle",
    c.FEATURE_SET_FAN_LEVEL: "set_fan_level",
    c.FEATURE_SET_PTC: "set_ptc",
    c.FEATURE_SET_PTC_LEVEL: "set_ptc_level",
    c.FEATURE_SET_FAVORITE_SPEED: "set_favorite_speed",
    c.FEATURE_SET_DISPLAY_ORIENTATION: "set_display_orientation",
    c.FEATURE_SET_WET_PROTECTION: "set_wet_protection",
    c.FEATURE_SET_CLEAN_MODE: "set_clean_mode",
}
_MIOT_PROPERTIES = {
    "set_favorite_rpm": "favorite_rpm",
    "set_anion": "anion",
    "set_gestures": "gestures",
    "set_volume": "buzzer_volume",
    "set_led_brightness_level": "led_brightness_level",
    "set_fan_level": "fan_level",
    "set_favorite_level": "favorite_level",
    "set_led_brightness": "led_brightness",
    "set_led": "led",
    "set_buzzer": "buzzer",
    "set_child_lock": "child_lock",
    "set_target_humidity": "target_humidity",
    "set_mode": "mode",
    "set_clean_mode": "clean_mode",
    "set_dry": "dry",
    "set_overwet_protect": "overwet_protect",
    "set_light": "led_light",
}


def _build_profile(
    model: str, default_driver: type[Device], suffix: str, category: c.DeviceCategory
) -> DeviceProfile:
    """Collect one family's capabilities with explicit model exceptions."""
    driver = _DRIVER_OVERRIDES.get(model, default_driver)
    suffix = _UI_OVERRIDES.get(model, suffix)
    airdog = driver is AirDogX3
    features = getattr(
        c, "FEATURE_FLAGS_AIRPURIFIER_AIRDOG" if airdog else f"FEATURE_FLAGS_{suffix}"
    )
    attribute_suffix = "AIRPURIFIER_AIRDOG_" + model.rsplit(".", 1)[1].upper() if airdog else suffix
    attributes = getattr(c, f"AVAILABLE_ATTRIBUTES_{attribute_suffix}")
    module = inspect.getmodule(driver)
    mode_enum = getattr(module, "OperationMode", None)
    options = {"mapping": JSQS_MAPPING} if driver is AirHumidifierJsqs else {}
    commands = {"on", "off", "set_mode"}
    commands.update(f"set_{name}" for name in attributes)
    commands.update(
        name
        for name in dir(driver)
        if name.startswith("reset_")
        or (name.startswith("set_") and name not in ("set_property", "set_property_by"))
    )
    commands.update(command for flag, command in _FEATURE_COMMANDS.items() if features & flag)
    if category is c.DeviceCategory.FAN:
        commands.update(
            {
                "set_speed",
                "set_direct_speed",
                "set_natural_speed",
                "set_oscillate",
                "set_rotate",
                "delay_off",
            }
        )
    if features & c.FEATURE_RESET_FILTER:
        commands.update(
            {"reset_filter", "reset_dust_filter", "reset_upper_filter", "set_filters_cleaned"}
        )
    if driver is AirHumidifierJsqs:
        commands.update({"set_light", "set_overwet_protect"})
    if driver is AirFreshT2017 or driver is AirFreshA1:
        commands.add("set_display")
    aliases = (
        {"set_mode": "set_mode_and_speed", "reset_filter": "set_filters_cleaned"} if airdog else {}
    )
    if driver in (AirFreshA1, AirFreshT2017):
        aliases["reset_filter"] = "reset_dust_filter"
    if driver is AirDehumidifier:
        commands.add("set_fan_speed")
    if aliases.get("reset_filter"):
        commands.add("reset_filter")
    if airdog:
        commands.update({"set_mode_and_speed", "set_filters_cleaned"})
    commands = {
        name for name in commands if callable(getattr(driver, aliases.get(name, name), None))
    }
    mappings = getattr(driver, "_mappings", {})
    if mappings:
        # All fallback aliases in this registry are explicit members of the known family.
        mapping = options.get("mapping") or mappings.get(model) or next(iter(mappings.values()))
        command_properties = dict(_MIOT_PROPERTIES)
        if driver in (Fan1C, FanMiot):
            command_properties.update(
                {
                    "set_led": "light",
                    "set_speed": "fan_level" if driver is Fan1C else "fan_speed",
                    "set_oscillate": "swing_mode",
                    "set_angle": "swing_mode_angle",
                    "set_rotate": "set_move",
                    "delay_off": "power_off_time",
                }
            )
        elif driver is AirHumidifierMiot:
            command_properties["set_speed"] = "speed_level"
        commands = {
            name
            for name in commands
            if name not in command_properties or command_properties[name] in mapping
        }
        if driver is FanMiot and model not in module.SUPPORTED_ANGLES:
            commands.discard("set_angle")
    humidity = None
    if "set_target_humidity" in commands:
        if driver is AirDehumidifier:
            humidity = HumidityControl(40, 60, 10, mode_enum.Auto, 1)
        elif driver is AirHumidifierJsqs:
            humidity = HumidityControl(40, 80, 1, mode_enum.Auto)
        elif driver is AirHumidifierMjjsq:
            humidity = HumidityControl(0, 99, 1, mode_enum.Humidity)
        elif driver is AirHumidifierMiot:
            humidity = HumidityControl(30, 80, 1, mode_enum.Auto)
        else:
            humidity = HumidityControl(
                30, 80, 10, mode_enum.Auto if suffix == "AIRHUMIDIFIER_CA_AND_CB" else None
            )
    speed_kind, speed_range = SpeedKind.NONE, None
    if category is c.DeviceCategory.FAN:
        speed_kind = (
            SpeedKind.LEGACY
            if driver is Fan
            else SpeedKind.LEVELS
            if driver is Fan1C
            else SpeedKind.PERCENTAGE
        )
        speed_range = (1, 3) if driver is Fan1C else (1, 100)
    elif category is c.DeviceCategory.PURIFIER:
        speed_kind = SpeedKind.AIRDOG if airdog else SpeedKind.PURIFIER
        speed_range = (
            (1, 4 if model == c.MODEL_AIRPURIFIER_AIRDOG_X3 else 5)
            if airdog
            else (1, 3)
            if "set_fan_level" in commands
            else (300, 2300)
            if "set_favorite_rpm" in commands
            else ((0, 14) if driver is AirPurifierMiot else (0, 17))
            if "set_favorite_level" in commands
            else None
        )
    if category is c.DeviceCategory.AIR_FRESH and "set_favorite_speed" in commands:
        speed_kind = SpeedKind.PERCENTAGE
        speed_range = (60, 300) if driver is AirFreshT2017 else (0, 150)
    speed_modes = ()
    if category is c.DeviceCategory.AIR_FRESH and driver is AirFresh:
        speed_kind, speed_range = SpeedKind.LEVELS, (1, 3)
        speed_modes = ("Low", "Middle", "Strong")
    enums = {}
    for name, enum_name in [
        ("led_brightness", "LedBrightness"),
        ("ptc_level", "PtcLevel"),
        ("display_orientation", "DisplayOrientation"),
    ]:
        enum = getattr(module, enum_name, None)
        if enum is not None and f"set_{name}" in commands:
            enums[name] = enum
    presets = tuple(mode.name for mode in mode_enum) if mode_enum else ()
    configured = getattr(c, f"OPERATION_MODES_{suffix}", presets)
    presets = tuple(name for name in presets if name in configured)
    if driver is Fan or driver in (FanP5, FanMiot, Fan1C):
        presets = ("Nature",)
    elif driver is FanLeshow:
        presets = tuple(name for name in presets if name != "Manual")
    elif driver is AirHumidifier and suffix == "AIRHUMIDIFIER":
        presets = tuple(name for name in presets if name != "Auto")
    elif driver is AirHumidifier and suffix == "AIRHUMIDIFIER_CA_AND_CB":
        presets = tuple(name for name in presets if name not in ("Medium", "Strong"))
    elif driver is AirHumidifierMjjsq and model != c.MODEL_AIRHUMIDIFIER_JSQ1:
        presets = tuple(name for name in presets if name != "WetAndProtect")
    if category is c.DeviceCategory.PURIFIER:
        presets = tuple(name for name in presets if name not in ("Favorite", "Fan", "Manual"))
    presets = tuple(name for name in presets if name != "Off" and name not in speed_modes)
    if category is c.DeviceCategory.AIR_FRESH:
        presets = tuple(name for name in presets if name != "Favorite")
    return DeviceProfile(
        category,
        driver,
        features,
        MappingProxyType(dict(attributes)),
        mode_enum,
        speed_kind,
        speed_range,
        humidity,
        MappingProxyType(enums),
        frozenset(commands),
        MappingProxyType(options),
        presets,
        MappingProxyType(aliases),
        speed_modes,
        driver is Fan,
        540 if driver is FanLeshow else 480,
        speed_step=10 if speed_range == (300, 2300) else 1,
    )


PROFILES: Mapping[str, DeviceProfile] = MappingProxyType(
    {
        model: _build_profile(model, driver, suffix, category)
        for driver, models, suffix, category in _DRIVER_GROUPS
        for model in models
    }
)


def get_device_profile(model: str | None) -> DeviceProfile:
    """Resolve a supported model; never guess a driver for unknown hardware."""
    try:
        return PROFILES[model]
    except KeyError as exc:
        raise UnsupportedModelError(f"Unsupported Xiaomi model: {model}") from exc


def create_device(host: str, token: str, model: str) -> Device:
    """Instantiate the selected protocol without contacting the network."""
    profile = get_device_profile(model)
    return profile.driver(ip=host, token=token, model=model, **profile.device_options)


def read_speed_percentage(profile: DeviceProfile, data: Mapping[str, Any]) -> int | None:
    """Convert the active protocol speed without interpreting motor RPM as percent."""
    from homeassistant.util.percentage import ranged_value_to_percentage

    power = data.get("power")
    if power in (False, "off"):
        return 0
    limits = profile.speed_range
    if limits is None:
        return None
    if profile.speed_kind is SpeedKind.LEGACY:
        natural = data.get("natural_speed")
        value = natural if natural and natural > 0 else data.get("direct_speed")
    elif profile.speed_kind is SpeedKind.PURIFIER:
        if data.get("mode") in ("Auto", "Silent", "Idle"):
            return None
        if data.get("mode") == "Favorite" or "set_fan_level" not in profile.commands:
            if (
                "set_favorite_level" not in profile.commands
                and "set_favorite_rpm" in profile.commands
            ):
                value = data.get("favorite_rpm")
            else:
                value = data.get("favorite_level")
                limits = (0, 14) if profile.driver is AirPurifierMiot else (0, 17)
        else:
            value = data.get("fan_level")
    elif profile.category is c.DeviceCategory.AIR_FRESH:
        if profile.speed_modes:
            mode = data.get("mode")
            value = profile.speed_modes.index(mode) + 1 if mode in profile.speed_modes else None
        else:
            value = data.get("favorite_speed")
    else:
        value = data.get("speed")
    if value is None:
        return None
    return max(0, min(100, ranged_value_to_percentage(limits, value)))


def speed_value_for_percentage(profile: DeviceProfile, percentage: int) -> int:
    """Select a valid device speed, including discrete lowest and highest steps."""
    import math

    from homeassistant.util.percentage import percentage_to_ranged_value

    if type(percentage) is not int or not 1 <= percentage <= 100 or profile.speed_range is None:
        raise ValueError("Speed must be between 1 and 100 percent")
    minimum = profile.speed_range[0]
    value = percentage_to_ranged_value(profile.speed_range, percentage)
    return minimum + math.ceil((value - minimum) / profile.speed_step) * profile.speed_step
