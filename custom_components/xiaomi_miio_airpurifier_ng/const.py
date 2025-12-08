"""Constants for the Xiaomi Air Purifier NG integration."""

from typing import Final

# Integration constants
DOMAIN: Final = "xiaomi_miio_airpurifier_ng"
DATA_KEY: Final = f"fan.{DOMAIN}"
DEFAULT_NAME: Final = "Xiaomi Miio Device"
DEFAULT_RETRIES: Final = 20

# Configuration constants
CONF_MODEL: Final = "model"
CONF_RETRIES: Final = "retries"

# Platform types
PLATFORMS: Final = ["fan", "climate"]

# Device model identifiers - Air Purifiers
MODEL_AIRPURIFIER_V1: Final = "zhimi.airpurifier.v1"
MODEL_AIRPURIFIER_V2: Final = "zhimi.airpurifier.v2"
MODEL_AIRPURIFIER_V3: Final = "zhimi.airpurifier.v3"
MODEL_AIRPURIFIER_V5: Final = "zhimi.airpurifier.v5"
MODEL_AIRPURIFIER_PRO: Final = "zhimi.airpurifier.v6"
MODEL_AIRPURIFIER_PRO_V7: Final = "zhimi.airpurifier.v7"
MODEL_AIRPURIFIER_M1: Final = "zhimi.airpurifier.m1"
MODEL_AIRPURIFIER_M2: Final = "zhimi.airpurifier.m2"
MODEL_AIRPURIFIER_MA1: Final = "zhimi.airpurifier.ma1"
MODEL_AIRPURIFIER_MA2: Final = "zhimi.airpurifier.ma2"
MODEL_AIRPURIFIER_SA1: Final = "zhimi.airpurifier.sa1"
MODEL_AIRPURIFIER_SA2: Final = "zhimi.airpurifier.sa2"
MODEL_AIRPURIFIER_2S: Final = "zhimi.airpurifier.mc1"
MODEL_AIRPURIFIER_2H: Final = "zhimi.airpurifier.mc2"
MODEL_AIRPURIFIER_3: Final = "zhimi.airpurifier.ma4"
MODEL_AIRPURIFIER_3H: Final = "zhimi.airpurifier.mb3"
MODEL_AIRPURIFIER_ZA1: Final = "zhimi.airpurifier.za1"
MODEL_AIRPURIFIER_AIRDOG_X3: Final = "airdog.airpurifier.x3"
MODEL_AIRPURIFIER_AIRDOG_X5: Final = "airdog.airpurifier.x5"
MODEL_AIRPURIFIER_AIRDOG_X7SM: Final = "airdog.airpurifier.x7sm"

# Device model identifiers - Air Humidifiers
MODEL_AIRHUMIDIFIER_V1: Final = "zhimi.humidifier.v1"
MODEL_AIRHUMIDIFIER_CA1: Final = "zhimi.humidifier.ca1"
MODEL_AIRHUMIDIFIER_CA4: Final = "zhimi.humidifier.ca4"
MODEL_AIRHUMIDIFIER_CB1: Final = "zhimi.humidifier.cb1"
MODEL_AIRHUMIDIFIER_CB2: Final = "zhimi.humidifier.cb2"
MODEL_AIRHUMIDIFIER_MJJSQ: Final = "deerma.humidifier.mjjsq"
MODEL_AIRHUMIDIFIER_JSQ: Final = "deerma.humidifier.jsq"
MODEL_AIRHUMIDIFIER_JSQ1: Final = "deerma.humidifier.jsq1"
MODEL_AIRHUMIDIFIER_JSQ2W: Final = "deerma.humidifier.jsq2w"
MODEL_AIRHUMIDIFIER_JSQ3: Final = "deerma.humidifier.jsq3"
MODEL_AIRHUMIDIFIER_JSQ5: Final = "deerma.humidifier.jsq5"
MODEL_AIRHUMIDIFIER_JSQS: Final = "deerma.humidifier.jsqs"
MODEL_AIRHUMIDIFIER_JSQ001: Final = "shuii.humidifier.jsq001"

# Device model identifiers - Air Fresh
MODEL_AIRFRESH_A1: Final = "dmaker.airfresh.a1"
MODEL_AIRFRESH_VA2: Final = "zhimi.airfresh.va2"
MODEL_AIRFRESH_VA4: Final = "zhimi.airfresh.va4"
MODEL_AIRFRESH_T2017: Final = "dmaker.airfresh.t2017"

# Device model identifiers - Fans
MODEL_FAN_V2: Final = "zhimi.fan.v2"
MODEL_FAN_V3: Final = "zhimi.fan.v3"
MODEL_FAN_SA1: Final = "zhimi.fan.sa1"
MODEL_FAN_ZA1: Final = "zhimi.fan.za1"
MODEL_FAN_ZA3: Final = "zhimi.fan.za3"
MODEL_FAN_ZA4: Final = "zhimi.fan.za4"
MODEL_FAN_P5: Final = "dmaker.fan.p5"
MODEL_FAN_P8: Final = "dmaker.fan.p8"
MODEL_FAN_P9: Final = "dmaker.fan.p9"
MODEL_FAN_P10: Final = "dmaker.fan.p10"
MODEL_FAN_P11: Final = "dmaker.fan.p11"
MODEL_FAN_P18: Final = "dmaker.fan.p18"
MODEL_FAN_LESHOW_SS4: Final = "leshow.fan.ss4"
MODEL_FAN_1C: Final = "dmaker.fan.1c"

# Device model identifiers - Air Dehumidifier
MODEL_AIRDEHUMIDIFIER_V1: Final = "nwt.derh.wdh318efw1"

# Device model groups
PURIFIER_MIOT: Final = [MODEL_AIRPURIFIER_3, MODEL_AIRPURIFIER_3H, MODEL_AIRPURIFIER_ZA1]
HUMIDIFIER_MIOT: Final = [MODEL_AIRHUMIDIFIER_CA4]

# All supported models list
SUPPORTED_MODELS_AIRPURIFIER: Final = [
    MODEL_AIRPURIFIER_V1,
    MODEL_AIRPURIFIER_V2,
    MODEL_AIRPURIFIER_V3,
    MODEL_AIRPURIFIER_V5,
    MODEL_AIRPURIFIER_PRO,
    MODEL_AIRPURIFIER_PRO_V7,
    MODEL_AIRPURIFIER_M1,
    MODEL_AIRPURIFIER_M2,
    MODEL_AIRPURIFIER_MA1,
    MODEL_AIRPURIFIER_MA2,
    MODEL_AIRPURIFIER_SA1,
    MODEL_AIRPURIFIER_SA2,
    MODEL_AIRPURIFIER_2S,
    MODEL_AIRPURIFIER_2H,
    MODEL_AIRPURIFIER_3,
    MODEL_AIRPURIFIER_3H,
    MODEL_AIRPURIFIER_ZA1,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_AIRDOG_X5,
    MODEL_AIRPURIFIER_AIRDOG_X7SM,
]

SUPPORTED_MODELS_AIRHUMIDIFIER: Final = [
    MODEL_AIRHUMIDIFIER_V1,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_CB2,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_JSQ,
    MODEL_AIRHUMIDIFIER_JSQ1,
    MODEL_AIRHUMIDIFIER_JSQ2W,
    MODEL_AIRHUMIDIFIER_JSQ3,
    MODEL_AIRHUMIDIFIER_JSQ5,
    MODEL_AIRHUMIDIFIER_JSQS,
    MODEL_AIRHUMIDIFIER_JSQ001,
]

SUPPORTED_MODELS_AIRFRESH: Final = [
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_VA2,
    MODEL_AIRFRESH_VA4,
    MODEL_AIRFRESH_T2017,
]

SUPPORTED_MODELS_FAN: Final = [
    MODEL_FAN_V2,
    MODEL_FAN_V3,
    MODEL_FAN_SA1,
    MODEL_FAN_ZA1,
    MODEL_FAN_ZA3,
    MODEL_FAN_ZA4,
    MODEL_FAN_P5,
    MODEL_FAN_P8,
    MODEL_FAN_P9,
    MODEL_FAN_P10,
    MODEL_FAN_P11,
    MODEL_FAN_P18,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_1C,
]

SUPPORTED_MODELS: Final = (
    SUPPORTED_MODELS_AIRPURIFIER
    + SUPPORTED_MODELS_AIRHUMIDIFIER
    + SUPPORTED_MODELS_AIRFRESH
    + SUPPORTED_MODELS_FAN
)

# Speed mode
SPEED_OFF: Final = "off"

# Common entity attributes
ATTR_MODEL: Final = "model"
ATTR_SPEED: Final = "speed"

# Air Purifier attributes
ATTR_TEMPERATURE: Final = "temperature"
ATTR_HUMIDITY: Final = "humidity"
ATTR_AIR_QUALITY_INDEX: Final = "aqi"
ATTR_FILTER_HOURS_USED: Final = "filter_hours_used"
ATTR_FILTER_LIFE: Final = "filter_life_remaining"
ATTR_FAVORITE_LEVEL: Final = "favorite_level"
ATTR_BUZZER: Final = "buzzer"
ATTR_CHILD_LOCK: Final = "child_lock"
ATTR_LED: Final = "led"
ATTR_LED_BRIGHTNESS: Final = "led_brightness"
ATTR_MOTOR_SPEED: Final = "motor_speed"
ATTR_AVERAGE_AIR_QUALITY_INDEX: Final = "average_aqi"
ATTR_PURIFY_VOLUME: Final = "purify_volume"
ATTR_BRIGHTNESS: Final = "brightness"
ATTR_LEVEL: Final = "level"
ATTR_FAN_LEVEL: Final = "fan_level"
ATTR_MOTOR2_SPEED: Final = "motor2_speed"
ATTR_ILLUMINANCE: Final = "illuminance"
ATTR_FILTER_RFID_PRODUCT_ID: Final = "filter_rfid_product_id"
ATTR_FILTER_RFID_TAG: Final = "filter_rfid_tag"
ATTR_FILTER_TYPE: Final = "filter_type"
ATTR_LEARN_MODE: Final = "learn_mode"
ATTR_SLEEP_TIME: Final = "sleep_time"
ATTR_SLEEP_LEARN_COUNT: Final = "sleep_mode_learn_count"
ATTR_EXTRA_FEATURES: Final = "extra_features"
ATTR_FEATURES: Final = "features"
ATTR_TURBO_MODE_SUPPORTED: Final = "turbo_mode_supported"
ATTR_AUTO_DETECT: Final = "auto_detect"
ATTR_SLEEP_MODE: Final = "sleep_mode"
ATTR_VOLUME: Final = "volume"
ATTR_USE_TIME: Final = "use_time"
ATTR_BUTTON_PRESSED: Final = "button_pressed"

# Air Humidifier attributes
ATTR_TARGET_HUMIDITY: Final = "target_humidity"
ATTR_TRANS_LEVEL: Final = "trans_level"
ATTR_HARDWARE_VERSION: Final = "hardware_version"

# Air Humidifier CA attributes
ATTR_DRY: Final = "dry"

# Air Humidifier CA4 attributes
ATTR_WATER_LEVEL: Final = "water_level"
ATTR_ACTUAL_MOTOR_SPEED: Final = "actual_speed"
ATTR_FAHRENHEIT: Final = "fahrenheit"
ATTR_FAULT: Final = "fault"
ATTR_POWER_TIME: Final = "power_time"
ATTR_CLEAN_MODE: Final = "clean_mode"

# Air Humidifier MJJSQ, JSQ, JSQ1, JSQ5 and JSQS attributes
ATTR_NO_WATER: Final = "no_water"
ATTR_WATER_TANK_DETACHED: Final = "water_tank_detached"
ATTR_WET_PROTECTION: Final = "wet_protection"

# Air Humidifier JSQ001 attributes
ATTR_LID_OPENED: Final = "lid_opened"

# Air Fresh attributes
ATTR_CO2: Final = "co2"
ATTR_PTC: Final = "ptc"
ATTR_NTC_TEMPERATURE: Final = "ntc_temperature"

# Air Fresh T2017 attributes
ATTR_POWER: Final = "power"
ATTR_PM25: Final = "pm25"
ATTR_FAVORITE_SPEED: Final = "favorite_speed"
ATTR_CONTROL_SPEED: Final = "control_speed"
ATTR_DUST_FILTER_LIFE_REMAINING: Final = "dust_filter_life_remaining"
ATTR_DUST_FILTER_LIFE_REMAINING_DAYS: Final = "dust_filter_life_remaining_days"
ATTR_UPPER_FILTER_LIFE_REMAINING: Final = "upper_filter_life_remaining"
ATTR_UPPER_FILTER_LIFE_REMAINING_DAYS: Final = "upper_filter_life_remaining_days"
ATTR_PTC_LEVEL: Final = "ptc_level"
ATTR_PTC_STATUS: Final = "ptc_status"
ATTR_DISPLAY: Final = "display"
ATTR_DISPLAY_ORIENTATION: Final = "display_orientation"

# Smart Fan attributes
ATTR_NATURAL_SPEED: Final = "natural_speed"
ATTR_OSCILLATE: Final = "oscillate"
ATTR_BATTERY: Final = "battery"
ATTR_BATTERY_CHARGE: Final = "battery_charge"
ATTR_BATTERY_STATE: Final = "battery_state"
ATTR_AC_POWER: Final = "ac_power"
ATTR_DELAY_OFF_COUNTDOWN: Final = "delay_off_countdown"
ATTR_ANGLE: Final = "angle"
ATTR_DIRECT_SPEED: Final = "direct_speed"
ATTR_SPEED_LEVEL: Final = "speed_level"
ATTR_RAW_SPEED: Final = "raw_speed"

# Fan Leshow SS4 attributes
ATTR_ERROR_DETECTED: Final = "error_detected"

# AirDog attributes
ATTR_FORMALDEHYDE: Final = "hcho"
ATTR_CLEAN_FILTERS: Final = "clean_filters"

# Air Dehumidifier attributes
ATTR_CURRENT_TEMPERATURE: Final = "_current_temperature"
ATTR_ALARM: Final = "alarm"

# Service attribute names
SERVICE_SET_BUZZER_ON: Final = "fan_set_buzzer_on"
SERVICE_SET_BUZZER_OFF: Final = "fan_set_buzzer_off"
SERVICE_SET_LED_ON: Final = "fan_set_led_on"
SERVICE_SET_LED_OFF: Final = "fan_set_led_off"
SERVICE_SET_CHILD_LOCK_ON: Final = "fan_set_child_lock_on"
SERVICE_SET_CHILD_LOCK_OFF: Final = "fan_set_child_lock_off"
SERVICE_SET_FAVORITE_LEVEL: Final = "fan_set_favorite_level"
SERVICE_SET_FAN_LEVEL: Final = "fan_set_fan_level"
SERVICE_SET_LED_BRIGHTNESS: Final = "fan_set_led_brightness"
SERVICE_SET_AUTO_DETECT_ON: Final = "fan_set_auto_detect_on"
SERVICE_SET_AUTO_DETECT_OFF: Final = "fan_set_auto_detect_off"
SERVICE_SET_LEARN_MODE_ON: Final = "fan_set_learn_mode_on"
SERVICE_SET_LEARN_MODE_OFF: Final = "fan_set_learn_mode_off"
SERVICE_SET_VOLUME: Final = "fan_set_volume"
SERVICE_RESET_FILTER: Final = "fan_reset_filter"
SERVICE_SET_EXTRA_FEATURES: Final = "fan_set_extra_features"
SERVICE_SET_TARGET_HUMIDITY: Final = "fan_set_target_humidity"
SERVICE_SET_DRY_ON: Final = "fan_set_dry_on"
SERVICE_SET_DRY_OFF: Final = "fan_set_dry_off"
SERVICE_SET_FILTERS_CLEANED: Final = "fan_set_filters_cleaned"

# Additional service names from fan.py
SERVICE_SET_FAN_LED_ON: Final = "fan_set_led_on"
SERVICE_SET_FAN_LED_OFF: Final = "fan_set_led_off"
SERVICE_SET_MOTOR_SPEED: Final = "fan_set_motor_speed"
SERVICE_SET_CLEAN_MODE_ON: Final = "fan_set_clean_mode_on"
SERVICE_SET_CLEAN_MODE_OFF: Final = "fan_set_clean_mode_off"
SERVICE_SET_WET_PROTECTION_ON: Final = "fan_set_wet_protection_on"
SERVICE_SET_WET_PROTECTION_OFF: Final = "fan_set_wet_protection_off"
SERVICE_SET_FAVORITE_SPEED: Final = "fan_set_favorite_speed"
SERVICE_SET_DISPLAY_ON: Final = "fan_set_display_on"
SERVICE_SET_DISPLAY_OFF: Final = "fan_set_display_off"
SERVICE_SET_PTC_LEVEL: Final = "fan_set_ptc_level"
SERVICE_SET_DISPLAY_ORIENTATION: Final = "fan_set_display_orientation"
SERVICE_SET_DELAY_OFF: Final = "fan_set_delay_off"
SERVICE_SET_OSCILLATION_ANGLE: Final = "fan_set_oscillation_angle"
SERVICE_SET_NATURAL_MODE_ON: Final = "fan_set_natural_mode_on"
SERVICE_SET_NATURAL_MODE_OFF: Final = "fan_set_natural_mode_off"
SERVICE_SET_PTC_ON: Final = "fan_set_ptc_on"
SERVICE_SET_PTC_OFF: Final = "fan_set_ptc_off"

# Climate/Dehumidifier service names (use different prefix to avoid conflicts)
SERVICE_CLIMATE_SET_BUZZER_ON: Final = "xiaomi_miio_set_buzzer_on"
SERVICE_CLIMATE_SET_BUZZER_OFF: Final = "xiaomi_miio_set_buzzer_off"
SERVICE_CLIMATE_SET_LED_ON: Final = "xiaomi_miio_set_led_on"
SERVICE_CLIMATE_SET_LED_OFF: Final = "xiaomi_miio_set_led_off"
SERVICE_CLIMATE_SET_CHILD_LOCK_ON: Final = "xiaomi_miio_set_child_lock_on"
SERVICE_CLIMATE_SET_CHILD_LOCK_OFF: Final = "xiaomi_miio_set_child_lock_off"

# Air Dehumidifier specific attributes
ATTR_MODE: Final = "mode"
ATTR_FAN_SPEED: Final = "fan_speed"
ATTR_TANK_FULL: Final = "tank_full"
ATTR_COMPRESSOR_STATUS: Final = "compressor_status"
ATTR_DEFROST_STATUS: Final = "defrost_status"
ATTR_FAN_ST: Final = "fan_st"

# Common result status
SUCCESS: Final = ["ok"]

# Feature flags (bitwise)
FEATURE_SET_BUZZER: Final = 1
FEATURE_SET_LED: Final = 2
FEATURE_SET_CHILD_LOCK: Final = 4
FEATURE_SET_LED_BRIGHTNESS: Final = 8
FEATURE_SET_FAVORITE_LEVEL: Final = 16
FEATURE_SET_AUTO_DETECT: Final = 32
FEATURE_SET_LEARN_MODE: Final = 64
FEATURE_SET_VOLUME: Final = 128
FEATURE_RESET_FILTER: Final = 256
FEATURE_SET_EXTRA_FEATURES: Final = 512
FEATURE_SET_TARGET_HUMIDITY: Final = 1024
FEATURE_SET_DRY: Final = 2048
FEATURE_SET_OSCILLATION_ANGLE: Final = 4096
FEATURE_SET_NATURAL_MODE: Final = 8192
FEATURE_SET_FAN_LEVEL: Final = 16384
FEATURE_SET_MOTOR_SPEED: Final = 32768
FEATURE_SET_PTC: Final = 65536
FEATURE_SET_PTC_LEVEL: Final = 131072
FEATURE_SET_FAVORITE_SPEED: Final = 262144
FEATURE_SET_DISPLAY_ORIENTATION: Final = 524288
FEATURE_SET_WET_PROTECTION: Final = 1048576
FEATURE_SET_CLEAN_MODE: Final = 2097152

# Feature flag combinations for Air Purifiers
FEATURE_FLAGS_AIRPURIFIER: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_LEARN_MODE
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

FEATURE_FLAGS_AIRPURIFIER_PRO: Final = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_AUTO_DETECT
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_PRO_V7: Final = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_2S: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
)

FEATURE_FLAGS_AIRPURIFIER_2H: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_LED_BRIGHTNESS
)

FEATURE_FLAGS_AIRPURIFIER_3: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_FAN_LEVEL
    | FEATURE_SET_LED_BRIGHTNESS
)

FEATURE_FLAGS_AIRPURIFIER_V3: Final = (
    FEATURE_SET_BUZZER | FEATURE_SET_CHILD_LOCK | FEATURE_SET_LED
)

FEATURE_FLAGS_AIRPURIFIER_AIRDOG: Final = FEATURE_SET_CHILD_LOCK

# Feature flag combinations for Air Humidifiers
FEATURE_FLAGS_AIRHUMIDIFIER: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB: Final = FEATURE_FLAGS_AIRHUMIDIFIER | FEATURE_SET_DRY

FEATURE_FLAGS_AIRHUMIDIFIER_CA4: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_DRY
    | FEATURE_SET_MOTOR_SPEED
    | FEATURE_SET_CLEAN_MODE
)

FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ: Final = (
    FEATURE_SET_BUZZER | FEATURE_SET_LED | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_WET_PROTECTION
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5: Final = (
    FEATURE_SET_BUZZER | FEATURE_SET_LED | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQS: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_WET_PROTECTION
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_CHILD_LOCK
)

# Feature flag combinations for Air Fresh
FEATURE_FLAGS_AIRFRESH: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

FEATURE_FLAGS_AIRFRESH_VA4: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
    | FEATURE_SET_PTC
)

FEATURE_FLAGS_AIRFRESH_A1: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_RESET_FILTER
    | FEATURE_SET_PTC
    | FEATURE_SET_FAVORITE_SPEED
)

FEATURE_FLAGS_AIRFRESH_T2017: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_RESET_FILTER
    | FEATURE_SET_PTC
    | FEATURE_SET_PTC_LEVEL
    | FEATURE_SET_FAVORITE_SPEED
    | FEATURE_SET_DISPLAY_ORIENTATION
)

# Feature flag combinations for Fans
FEATURE_FLAGS_FAN: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_NATURAL_MODE
)

FEATURE_FLAGS_FAN_P5: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_NATURAL_MODE
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_LED
)

FEATURE_FLAGS_FAN_LESHOW_SS4: Final = FEATURE_SET_BUZZER
FEATURE_FLAGS_FAN_1C: Final = FEATURE_FLAGS_FAN

# Feature flag combinations for Air Dehumidifier
FEATURE_FLAGS_AIRDEHUMIDIFIER: Final = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_TARGET_HUMIDITY
)

# Fan speed level constants
FAN_SPEED_LEVEL1: Final = "Level 1"
FAN_SPEED_LEVEL2: Final = "Level 2"
FAN_SPEED_LEVEL3: Final = "Level 3"
FAN_SPEED_LEVEL4: Final = "Level 4"

# Fan preset modes
FAN_PRESET_MODES: Final = {
    SPEED_OFF: range(0, 1),
    FAN_SPEED_LEVEL1: range(1, 26),
    FAN_SPEED_LEVEL2: range(26, 51),
    FAN_SPEED_LEVEL3: range(51, 76),
    FAN_SPEED_LEVEL4: range(76, 101),
}

FAN_PRESET_MODE_VALUES: Final = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 74,
    FAN_SPEED_LEVEL4: 100,
}

FAN_PRESET_MODE_VALUES_P5: Final = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 70,
    FAN_SPEED_LEVEL4: 100,
}

FAN_PRESET_MODES_1C: Final = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 2,
    FAN_SPEED_LEVEL3: 3,
}

FAN_SPEEDS_1C: Final = [FAN_SPEED_LEVEL1, FAN_SPEED_LEVEL2, FAN_SPEED_LEVEL3]

# Operation modes for Air Purifiers
OPERATION_MODES_AIRPURIFIER: Final = ["Auto", "Silent", "Favorite", "Idle"]
OPERATION_MODES_AIRPURIFIER_PRO: Final = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_PRO_V7: Final = OPERATION_MODES_AIRPURIFIER_PRO
OPERATION_MODES_AIRPURIFIER_2S: Final = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_2H: Final = OPERATION_MODES_AIRPURIFIER
OPERATION_MODES_AIRPURIFIER_3: Final = ["Auto", "Silent", "Favorite", "Fan"]
OPERATION_MODES_AIRPURIFIER_V3: Final = [
    "Auto",
    "Silent",
    "Favorite",
    "Idle",
    "Medium",
    "High",
    "Strong",
]

# Operation modes for Air Fresh
OPERATION_MODES_AIRFRESH: Final = ["Auto", "Silent", "Interval", "Low", "Middle", "Strong"]
OPERATION_MODES_AIRFRESH_T2017: Final = ["Auto", "Sleep", "Favorite"]

# Map attributes to properties of the state object - Air Purifiers
AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON: Final = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_TURBO_MODE_SUPPORTED: "turbo_mode_supported",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_SLEEP_MODE: "sleep_mode",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_BUZZER: "buzzer",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H: Final = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_TURBO_MODE_SUPPORTED: "turbo_mode_supported",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_3: Final = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_FAN_LEVEL: "fan_level",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3: Final = {
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_VOLUME: "volume",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

# AirDog attributes
AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3: Final = {
    ATTR_MODE: "mode",
    ATTR_SPEED: "speed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_CLEAN_FILTERS: "clean_filters",
    ATTR_PM25: "pm25",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X5: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3,
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X7SM: Final = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3,
    ATTR_FORMALDEHYDE: "hcho",
}

# Map attributes to properties - Air Humidifiers
AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON: Final = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_BUZZER: "buzzer",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_TRANS_LEVEL: "trans_level",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_HARDWARE_VERSION: "hardware_version",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_DRY: "dry",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_HARDWARE_VERSION: "hardware_version",
    ATTR_WATER_LEVEL: "water_level",
    ATTR_WATER_TANK_DETACHED: "water_tank_detached",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_ACTUAL_MOTOR_SPEED: "actual_speed",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_DRY: "dry",
    ATTR_FAHRENHEIT: "fahrenheit",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_POWER_TIME: "power_time",
    ATTR_WATER_LEVEL: "water_level",
    ATTR_USE_TIME: "use_time",
    ATTR_CLEAN_MODE: "clean_mode",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED: "led",
    ATTR_NO_WATER: "no_water",
    ATTR_WATER_TANK_DETACHED: "water_tank_detached",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ,
    ATTR_WET_PROTECTION: "wet_protection",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_HUMIDITY: "relative_humidity",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED: "led_light",
    ATTR_NO_WATER: "water_shortage_fault",
    ATTR_WATER_TANK_DETACHED: "tank_filed",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5,
    ATTR_WET_PROTECTION: "overwet_protect",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ: Final = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_NO_WATER: "no_water",
    ATTR_LID_OPENED: "lid_opened",
}

# Map attributes to properties - Air Fresh
AVAILABLE_ATTRIBUTES_AIRFRESH: Final = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_CO2: "co2",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_USE_TIME: "use_time",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_EXTRA_FEATURES: "extra_features",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_VA4: Final = {
    **AVAILABLE_ATTRIBUTES_AIRFRESH,
    ATTR_PTC: "ptc",
    ATTR_NTC_TEMPERATURE: "ntc_temperature",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_A1: Final = {
    ATTR_POWER: "power",
    ATTR_MODE: "mode",
    ATTR_PM25: "pm25",
    ATTR_CO2: "co2",
    ATTR_TEMPERATURE: "temperature",
    ATTR_FAVORITE_SPEED: "favorite_speed",
    ATTR_CONTROL_SPEED: "control_speed",
    ATTR_DUST_FILTER_LIFE_REMAINING: "dust_filter_life_remaining",
    ATTR_DUST_FILTER_LIFE_REMAINING_DAYS: "dust_filter_life_remaining_days",
    ATTR_PTC: "ptc",
    ATTR_PTC_STATUS: "ptc_status",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_BUZZER: "buzzer",
    ATTR_DISPLAY: "display",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_T2017: Final = {
    **AVAILABLE_ATTRIBUTES_AIRFRESH_A1,
    ATTR_UPPER_FILTER_LIFE_REMAINING: "upper_filter_life_remaining",
    ATTR_UPPER_FILTER_LIFE_REMAINING_DAYS: "upper_filter_life_remaining_days",
    ATTR_PTC_LEVEL: "ptc_level",
    ATTR_DISPLAY_ORIENTATION: "display_orientation",
}

# Map attributes to properties - Fans
AVAILABLE_ATTRIBUTES_FAN: Final = {
    ATTR_ANGLE: "angle",
    ATTR_RAW_SPEED: "speed",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_AC_POWER: "ac_power",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DIRECT_SPEED: "direct_speed",
    ATTR_NATURAL_SPEED: "natural_speed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_BATTERY: "battery",
    ATTR_BATTERY_CHARGE: "battery_charge",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_LED: "led",
    ATTR_BATTERY_STATE: "battery_state",
}

AVAILABLE_ATTRIBUTES_FAN_P5: Final = {
    ATTR_MODE: "mode",
    ATTR_OSCILLATE: "oscillate",
    ATTR_ANGLE: "angle",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_RAW_SPEED: "speed",
}

AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4: Final = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_ERROR_DETECTED: "error_detected",
}

AVAILABLE_ATTRIBUTES_FAN_1C: Final = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_CHILD_LOCK: "child_lock",
}

# Map attributes to properties - Air Dehumidifier
AVAILABLE_ATTRIBUTES_AIRDEHUMIDIFIER: Final = {
    ATTR_CURRENT_TEMPERATURE: "temperature",
    "current_humidity": "humidity",
    ATTR_MODE: "mode",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED: "led",
    ATTR_FAN_SPEED: "fan_speed",
    ATTR_TANK_FULL: "tank_full",
    ATTR_COMPRESSOR_STATUS: "compressor_status",
    ATTR_DEFROST_STATUS: "defrost_status",
    ATTR_FAN_ST: "fan_st",
    ATTR_ALARM: "alarm",
}
