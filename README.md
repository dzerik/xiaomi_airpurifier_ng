# Xiaomi Air Purifier NG

![GitHub actions](https://github.com/dzerik/xiaomi_airpurifier_ng/actions/workflows/ci.yaml/badge.svg)
![GitHub stars](https://img.shields.io/github/stars/dzerik/xiaomi_airpurifier_ng)
![GitHub forks](https://img.shields.io/github/forks/dzerik/xiaomi_airpurifier_ng)
![GitHub watchers](https://img.shields.io/github/watchers/dzerik/xiaomi_airpurifier_ng)
[!["Buy Me A Coffee"](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg)](https://www.buymeacoffee.com/dzerik)

This is a custom component for Home Assistant to integrate Xiaomi Mi Air Purifier, Air Purifier Pro, Air Humidifier, Air Fresh, Air Dehumidifier and Pedestal Fan devices.

> **Note**: This is a modernized fork of [syssi/xiaomi_airpurifier](https://github.com/syssi/xiaomi_airpurifier) with improved architecture and UI configuration support.

## Key Features

- **UI Configuration**: Setup devices through Home Assistant UI (Settings → Integrations)
- **Modern Architecture**: Uses DataUpdateCoordinator for efficient polling
- **Full Device Support**: Air Purifiers, Humidifiers, Air Fresh, Dehumidifiers, Pedestal Fans
- **Rich Entity Attributes**: Comprehensive device state and sensor data
- **Service Calls**: Control buzzer, LED, child lock, and device-specific features

## Requirements

- Home Assistant 2023.1 or newer
- Device token (see [Retrieving the Access Token](https://www.home-assistant.io/integrations/xiaomi_miio/#xiaomi-cloud-tokens-extractor))

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for the python-miio library.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add `https://github.com/dzerik/xiaomi_airpurifier_ng` with category "Integration"
5. Search for "Xiaomi Air Purifier NG" and install
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/xiaomi_miio_airpurifier_ng` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Xiaomi Air Purifier NG"
4. Enter:
   - **Name**: Device name
   - **Host**: Device IP address
   - **Token**: 32-character API token
   - **Model** (optional): Device model (auto-detected if not specified)

## Supported Devices

### Air Purifiers (Fan Platform)

| Name | Model |
|------|-------|
| Air Purifier | zhimi.airpurifier.v1 |
| Air Purifier 2 | zhimi.airpurifier.v2 |
| Air Purifier V3 | zhimi.airpurifier.v3 |
| Air Purifier V5 | zhimi.airpurifier.v5 |
| Air Purifier Pro | zhimi.airpurifier.v6 |
| Air Purifier Pro V7 | zhimi.airpurifier.v7 |
| Air Purifier 2 (mini) | zhimi.airpurifier.m1 |
| Air Purifier (mini) | zhimi.airpurifier.m2 |
| Air Purifier MA1 | zhimi.airpurifier.ma1 |
| Air Purifier MA2 | zhimi.airpurifier.ma2 |
| Air Purifier 2S | zhimi.airpurifier.mc1 |
| Air Purifier 2H | zhimi.airpurifier.mc2 |
| Air Purifier Super | zhimi.airpurifier.sa1 |
| Air Purifier Super 2 | zhimi.airpurifier.sa2 |
| Air Purifier 3 (2019) | zhimi.airpurifier.ma4 |
| Air Purifier 3H (2019) | zhimi.airpurifier.mb3 |
| Air Purifier ZA1 | zhimi.airpurifier.za1 |
| Air Dog X3 | airdog.airpurifier.x3 |
| Air Dog X5 | airdog.airpurifier.x5 |
| Air Dog X7SM | airdog.airpurifier.x7sm |

### Air Humidifiers (Fan Platform)

| Name | Model |
|------|-------|
| Air Humidifier | zhimi.humidifier.v1 |
| Air Humidifier CA1 | zhimi.humidifier.ca1 |
| Smartmi Humidifier Evaporator 2 | zhimi.humidifier.ca4 |
| Smartmi Evaporative Humidifier | zhimi.humidifier.cb1 |
| Smartmi Evaporative Humidifier (Korea) | zhimi.humidifier.cb2 |
| Mijia Smart Sterilization Humidifier S | deerma.humidifier.mjjsq |
| Mijia Intelligent Sterilization Humidifier | deerma.humidifier.jsq |
| Mijia Smart Humidifier 2 (EU) | deerma.humidifier.jsq2w |
| Mijia Humidifier 4L | deerma.humidifier.jsq3 |
| Mijia Intelligent Sterilization Humidifier | deerma.humidifier.jsq5 |
| Mijia Smart Sterilization Humidifier S (EU) | deerma.humidifier.jsqs |
| Mijia Intelligent Sterilization Humidifier SCK0A45 | deerma.humidifier.jsq1 |
| Zero Fog Humidifier | shuii.humidifier.jsq001 |

### Air Fresh (Fan Platform)

| Name | Model |
|------|-------|
| Smartmi Fresh Air System | zhimi.airfresh.va2 |
| Smartmi Fresh Air System (PTC) | zhimi.airfresh.va4 |
| Mi Fresh Air Ventilator | dmaker.airfresh.t2017 |
| Mi Fresh Air Ventilator | dmaker.airfresh.a1 |

### Pedestal Fans (Fan Platform)

| Name | Model |
|------|-------|
| Pedestal Fan V2 | zhimi.fan.v2 |
| Pedestal Fan V3 | zhimi.fan.v3 |
| Pedestal Fan SA1 | zhimi.fan.sa1 |
| Pedestal Fan ZA1 | zhimi.fan.za1 |
| Pedestal Fan ZA3 | zhimi.fan.za3 |
| Pedestal Fan ZA4 | zhimi.fan.za4 |
| Pedestal Fan 1C | dmaker.fan.1c |
| Pedestal Fan P5 | dmaker.fan.p5 |
| Pedestal Fan P8 | dmaker.fan.p8 |
| Pedestal Fan P9 | dmaker.fan.p9 |
| Pedestal Fan P10 | dmaker.fan.p10 |
| Mijia Pedestal Fan | dmaker.fan.p11 |
| Rosou SS4 Ventilator | leshow.fan.ss4 |

### Air Dehumidifiers (Climate Platform)

| Name | Model |
|------|-------|
| New Widetech Internet Dehumidifier | nwt.derh.wdh318efw1 |

## Services

### Common Services

All fan entities support these services:

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.fan_set_buzzer_on` | Turn buzzer on |
| `xiaomi_miio_airpurifier_ng.fan_set_buzzer_off` | Turn buzzer off |
| `xiaomi_miio_airpurifier_ng.fan_set_child_lock_on` | Turn child lock on |
| `xiaomi_miio_airpurifier_ng.fan_set_child_lock_off` | Turn child lock off |
| `xiaomi_miio_airpurifier_ng.fan_set_led_on` | Turn LED on |
| `xiaomi_miio_airpurifier_ng.fan_set_led_off` | Turn LED off |
| `xiaomi_miio_airpurifier_ng.fan_set_led_brightness` | Set LED brightness (0=bright, 1=dim, 2=off) |

### Air Purifier Services

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.fan_set_favorite_level` | Set favorite level (0-16) |
| `xiaomi_miio_airpurifier_ng.fan_set_auto_detect_on/off` | Auto detect (Pro only) |
| `xiaomi_miio_airpurifier_ng.fan_set_learn_mode_on/off` | Learn mode |
| `xiaomi_miio_airpurifier_ng.fan_set_volume` | Set volume (Pro only, 0-100) |
| `xiaomi_miio_airpurifier_ng.fan_set_fan_level` | Set fan level (3H only, 1-3) |
| `xiaomi_miio_airpurifier_ng.fan_reset_filter` | Reset filter |

### Air Humidifier Services

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.fan_set_target_humidity` | Set target humidity |
| `xiaomi_miio_airpurifier_ng.fan_set_dry_on/off` | Dry mode (CA models) |
| `xiaomi_miio_airpurifier_ng.fan_set_motor_speed` | Set motor speed (CA4, 200-2000 RPM) |
| `xiaomi_miio_airpurifier_ng.fan_set_clean_mode_on/off` | Clean mode (CA4) |
| `xiaomi_miio_airpurifier_ng.fan_set_wet_protection_on/off` | Wet protection (jsq1) |

### Air Fresh Services

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.fan_set_ptc_on/off` | PTC heater (VA4, T2017) |
| `xiaomi_miio_airpurifier_ng.fan_set_ptc_level` | PTC level (T2017: Low/Medium/High) |
| `xiaomi_miio_airpurifier_ng.fan_set_favorite_speed` | Favorite speed (T2017, 60-300) |
| `xiaomi_miio_airpurifier_ng.fan_set_display_on/off` | Display (T2017) |
| `xiaomi_miio_airpurifier_ng.fan_set_display_orientation` | Display orientation (T2017) |
| `xiaomi_miio_airpurifier_ng.fan_set_extra_features` | Extra features |
| `xiaomi_miio_airpurifier_ng.fan_reset_filter` | Reset filter |

### Pedestal Fan Services

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.fan_set_oscillation_angle` | Set oscillation angle (30/60/90/120) |
| `xiaomi_miio_airpurifier_ng.fan_set_natural_mode_on/off` | Natural mode |
| `xiaomi_miio_airpurifier_ng.fan_set_delay_off` | Delayed turn off (minutes) |

### Climate Services (Dehumidifier)

| Service | Description |
|---------|-------------|
| `xiaomi_miio_airpurifier_ng.climate_set_buzzer_on/off` | Turn buzzer on/off |
| `xiaomi_miio_airpurifier_ng.climate_set_led_on/off` | Turn LED on/off |
| `xiaomi_miio_airpurifier_ng.climate_set_child_lock_on/off` | Turn child lock on/off |

## Entities

The integration automatically creates entities based on device capabilities.

### Sensors

| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `aqi` | Air Quality Index | AQI | - |
| `pm25` | PM2.5 particulate matter | µg/m³ | PM25 |
| `pm10` | PM10 particulate matter | µg/m³ | PM10 |
| `average_aqi` | Average Air Quality Index | AQI | - |
| `temperature` | Current temperature | °C | Temperature |
| `humidity` | Current humidity | % | Humidity |
| `co2` | CO2 level | ppm | CO2 |
| `tvoc` | Total Volatile Organic Compounds | µg/m³ | VOC |
| `illuminance` | Light level | lx | Illuminance |
| `filter_life_remaining` | Filter life remaining | % | - |
| `filter_hours_used` | Filter usage hours | h | Duration |
| `filter_left_time` | Filter days left | days | - |
| `filter_type` | Filter type | - | - |
| `motor_speed` | Motor speed | RPM | - |
| `motor2_speed` | Secondary motor speed | RPM | - |
| `use_time` | Device usage time | s | Duration |
| `purify_volume` | Air purified volume | m³ | - |
| `water_level` | Water level in tank | % | - |
| `target_humidity` | Target humidity setting | % | - |
| `volume` | Buzzer/speaker volume | % | - |
| `battery` | Battery level | % | Battery |
| `mode` | Current operation mode | - | - |
| `temperature_outside` | Outside temperature (Air Fresh) | °C | Temperature |
| `dust_filter_life_remaining` | Dust filter life (Air Fresh) | % | - |
| `dust_filter_life_remaining_days` | Dust filter days left | days | - |
| `upper_filter_life_remaining` | Upper filter life (Air Fresh) | % | - |
| `upper_filter_life_remaining_days` | Upper filter days left | days | - |
| `favorite_speed` | Favorite speed setting | RPM | - |
| `control_speed` | Control speed | RPM | - |
| `speed` | Fan speed | - | - |
| `natural_speed` | Natural mode speed | - | - |
| `direct_speed` | Direct mode speed | - | - |
| `angle` | Oscillation angle | ° | - |

### Binary Sensors

| Entity | Description | Device Class | Devices |
|--------|-------------|--------------|---------|
| `water_tank` | Water tank installed | Connectivity | JSQS Humidifiers |
| `water_shortage` | Water shortage fault | Problem | JSQS Humidifiers |
| `water_tank_detached` | Water tank removed | Problem | MJJSQ Humidifiers |
| `no_water` | No water in tank | Problem | MJJSQ Humidifiers |
| `ac_power` | AC power connected | Plug | Pedestal Fans |
| `battery_charge` | Battery charging | Battery Charging | Pedestal Fans |
| `oscillate` | Oscillation active | - | Pedestal Fans |
| `ptc_status` | PTC heater active | Heat | Air Fresh |

### Switches

| Entity | Description | Icon | Devices |
|--------|-------------|------|---------|
| `buzzer` | Buzzer on/off | mdi:volume-high | All |
| `led` | LED on/off | mdi:led-on | Air Purifiers, Zhimi Humidifiers |
| `led_light` | LED light on/off | mdi:led-on | JSQS Humidifiers |
| `child_lock` | Child lock on/off | mdi:lock | All |
| `dry` | Dry mode | mdi:water-off | Zhimi Humidifiers |
| `learn_mode` | Learn mode | mdi:school | Air Purifiers |
| `auto_detect` | Auto detect | mdi:auto-fix | Air Purifiers Pro |
| `oscillate` | Oscillation | mdi:rotate-3d-variant | Pedestal Fans |
| `ptc` | PTC heater | mdi:radiator | Air Fresh |
| `display` | Display on/off | mdi:monitor | Air Fresh T2017 |
| `overwet_protect` | Overwet protection | mdi:water-alert | JSQS Humidifiers |
| `anion` | Ionizer | mdi:atom | Air Purifiers |
| `gestures` | Gesture control | mdi:gesture-tap | Air Purifiers |

### Numbers (Sliders)

| Entity | Description | Range | Step | Unit |
|--------|-------------|-------|------|------|
| `favorite_level` | Favorite level | 0-16 | 1 | - |
| `fan_level` | Fan level | 1-3 | 1 | - |
| `volume` | Buzzer volume | 0-100 | 1 | % |
| `target_humidity` | Target humidity | 30-80 | 10 | % |
| `angle` | Oscillation angle | 30-120 | 30 | ° |
| `delay_off_countdown` | Delay off timer | 0-480 | 1 | min |

### Selects (Dropdowns)

| Entity | Description | Options |
|--------|-------------|---------|
| `led_brightness` | LED brightness | bright, dim, off |
| `display_orientation` | Display orientation (T2017) | forward, left, right |
| `ptc_level` | PTC heater level (T2017) | low, medium, high |
| `mode` | Operation mode | Device-specific (Auto, Silent, Low, Medium, High, etc.) |

### Buttons

| Entity | Description | Devices |
|--------|-------------|---------|
| `reset_filter` | Reset filter counter | Air Purifiers, Air Fresh |
| `filters_cleaned` | Mark filters as cleaned | Humidifiers |

All entities are created automatically based on device capabilities.

## Debugging

Enable debug logging if you encounter issues:

```yaml
logger:
  default: warn
  logs:
    custom_components.xiaomi_miio_airpurifier_ng: debug
    miio: debug
```

## Migration from xiaomi_miio_airpurifier

If you're migrating from the original integration:

1. Remove old YAML configuration
2. Install this integration via HACS
3. Add devices via UI (Settings → Integrations)
4. Update service calls to use `xiaomi_miio_airpurifier_ng` domain
5. Update entity IDs in automations if needed

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
