# Xiaomi Air Purifier NG

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2026.3.4%2B-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](CHANGELOG.md)

[README на русском](README_RU.md)

Custom Home Assistant integration for Xiaomi devices: air purifiers, humidifiers, fans, air fresh systems and dehumidifiers.

Devices are polled locally over WiFi via the miIO protocol — no cloud or internet required.

> Fork of [syssi/xiaomi_airpurifier](https://github.com/syssi/xiaomi_airpurifier) with reworked architecture, UI-based configuration and support for current Home Assistant versions.

> **Note:** For new installations, consider using [Xiaomi Miot Auto](https://github.com/al-one/hass-xiaomi-miot) — a more universal integration that supports virtually all Xiaomi devices via the MIoT protocol, including Wi-Fi, BLE and ZigBee. This integration (Xiaomi Air Purifier NG) is maintained for users who prefer a **lightweight, fully local** solution without cloud or Xiaomi account, or who need stable support for **legacy miIO devices**. The project is in maintenance mode — bug fixes and community contributions are welcome, but no major new features are planned.

---

## Supported Devices

### Air Purifier (`fan` platform)

| Name | Model |
| --- | --- |
| Air Purifier | zhimi.airpurifier.v1 |
| Air Purifier 2 | zhimi.airpurifier.v2 |
| Air Purifier V3 | zhimi.airpurifier.v3 |
| Air Purifier V5 | zhimi.airpurifier.v5 |
| Air Purifier Pro | zhimi.airpurifier.v6 |
| Air Purifier Pro V7 | zhimi.airpurifier.v7 |
| Air Purifier 2 mini | zhimi.airpurifier.m1 |
| Air Purifier mini | zhimi.airpurifier.m2 |
| Air Purifier MA1 | zhimi.airpurifier.ma1 |
| Air Purifier MA2 | zhimi.airpurifier.ma2 |
| Air Purifier Super | zhimi.airpurifier.sa1 |
| Air Purifier Super 2 | zhimi.airpurifier.sa2 |
| Air Purifier 2S | zhimi.airpurifier.mc1 |
| Air Purifier 2H | zhimi.airpurifier.mc2 |
| Air Purifier 3 | zhimi.airpurifier.ma4 |
| Air Purifier 3H | zhimi.airpurifier.mb3 |
| Air Purifier 3H (alt) | zhimi.airpurifier.mb3a |
| Air Purifier ZA1 | zhimi.airpurifier.za1 |
| Air Purifier Pro H | zhimi.airpurifier.va1 |
| Air Purifier 4 | zhimi.airpurifier.vb2 |
| Air Purifier 3C | zhimi.airpurifier.mb4 |
| Air Purifier 3C (rev) | zhimi.airp.mb4a |
| Air Purifier 3C (rev2) | zhimi.airp.mb5 |
| Air Purifier Pro H (MIoT) | zhimi.airp.va2 |
| Air Purifier 4 Pro | zhimi.airp.vb4 |
| Air Purifier 4 Lite | zhimi.airpurifier.rma1 |
| Air Purifier 4 Lite (alt) | zhimi.airp.rmb1 |
| Air Dog X3 | airdog.airpurifier.x3 |
| Air Dog X5 | airdog.airpurifier.x5 |
| Air Dog X7SM | airdog.airpurifier.x7sm |

### Air Humidifier (`humidifier` platform)

| Name | Model |
| --- | --- |
| Air Humidifier | zhimi.humidifier.v1 |
| Air Humidifier CA1 | zhimi.humidifier.ca1 |
| Smartmi Humidifier Evaporator 2 | zhimi.humidifier.ca4 |
| Smartmi Evaporative Humidifier | zhimi.humidifier.cb1 |
| Smartmi Evaporative Humidifier (Korea) | zhimi.humidifier.cb2 |
| Mijia Smart Sterilization Humidifier S | deerma.humidifier.mjjsq |
| Mijia Intelligent Sterilization Humidifier | deerma.humidifier.jsq |
| Mijia Intelligent Sterilization Humidifier SCK0A45 | deerma.humidifier.jsq1 |
| Mijia Smart Humidifier 2 EU | deerma.humidifier.jsq2w |
| Mijia Humidifier 4L | deerma.humidifier.jsq3 |
| Mijia Intelligent Sterilization Humidifier 2 | deerma.humidifier.jsq5 |
| Mijia Smart Sterilization Humidifier S EU | deerma.humidifier.jsqs |
| Zero Fog Humidifier | shuii.humidifier.jsq001 |

### Air Fresh (`fan` platform)

| Name | Model |
| --- | --- |
| Mi Fresh Air Ventilator A1 | dmaker.airfresh.a1 |
| Smartmi Fresh Air System | zhimi.airfresh.va2 |
| Smartmi Fresh Air System PTC | zhimi.airfresh.va4 |
| Mi Fresh Air Ventilator T2017 | dmaker.airfresh.t2017 |

### Standing Fan (`fan` platform)

| Name | Model |
| --- | --- |
| Pedestal Fan V2 | zhimi.fan.v2 |
| Pedestal Fan V3 | zhimi.fan.v3 |
| Pedestal Fan SA1 | zhimi.fan.sa1 |
| Pedestal Fan ZA1 | zhimi.fan.za1 |
| Pedestal Fan ZA3 | zhimi.fan.za3 |
| Pedestal Fan ZA4 | zhimi.fan.za4 |
| Pedestal Fan P5 | dmaker.fan.p5 |
| Pedestal Fan P8 | dmaker.fan.p8 |
| Pedestal Fan P9 | dmaker.fan.p9 |
| Pedestal Fan P10 | dmaker.fan.p10 |
| Mijia Pedestal Fan P11 | dmaker.fan.p11 |
| Smart Standing Fan Pro EU | dmaker.fan.p15 |
| Pedestal Fan P18 | dmaker.fan.p18 |
| Smart Standing Fan 2 Pro | dmaker.fan.p33 |
| Rosou SS4 Ventilator | leshow.fan.ss4 |
| Pedestal Fan 1C | dmaker.fan.1c |

### Air Dehumidifier (`climate` platform)

| Name | Model |
| --- | --- |
| New Widetech Internet Dehumidifier | nwt.derh.wdh318efw1 |

---

## Installation via HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Click the menu (three dots) -> **Custom repositories**.
4. Add repository: `https://github.com/dzerik/xiaomi_airpurifier_ng`, category — **Integration**.
5. Find **Xiaomi Air Purifier NG** and click **Download**.
6. Restart Home Assistant.

## Manual Installation

1. Copy the `custom_components/xiaomi_miio_airpurifier_ng` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

The integration is configured via the UI — no YAML configuration is needed.

1. Go to **Settings** -> **Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Xiaomi Air Purifier NG**.
4. Enter the parameters:

| Parameter | Description |
| --- | --- |
| Host | Device IP address on the local network |
| Token | 32-character device token |
| Model | Device model (e.g. `zhimi.airpurifier.ma4`) |

After setup, the polling interval can be changed via **Options** (default: 30 seconds).

---

## Platforms and Entities

The integration automatically creates entities based on the capabilities of each device model.

| Platform | Description |
| --- | --- |
| `fan` | Air purifiers, air fresh, standing fans — on/off, speed, modes |
| `humidifier` | Humidifiers — on/off, target humidity, modes |
| `climate` | Dehumidifier — on/off, target humidity, HVAC mode |
| `sensor` | Temperature, humidity, AQI, CO2, motor speed, filter status, etc. |
| `switch` | Buzzer, LED, child lock, dry mode, oscillation, etc. |
| `number` | Favorite level, fan level, target humidity, oscillation angle, etc. |
| `select` | LED brightness, display orientation, PTC level, operation mode |
| `binary_sensor` | Water level, AC power, battery charging, PTC heater status |
| `button` | Reset filter counter |

---

## How to Get the Device Token

The token is required for local communication. You can obtain it in several ways:

- **Xiaomi Cloud Token Extractor** (recommended): [instructions on the Home Assistant website](https://www.home-assistant.io/integrations/xiaomi_miio/#xiaomi-cloud-tokens-extractor)
- Via the **MiHome** app using a traffic sniffer or backup extraction (Android)

---

## Debugging

To diagnose issues, enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.xiaomi_miio_airpurifier_ng: debug
    miio: debug
```

---

## Upgrading to 4.0.0

Home Assistant 2026.3.4+ and Python 3.14.2+ are required. Existing entity `unique_id` values are preserved. Reconfiguration and reauthentication verify the device MAC before saving connection details.

- Replace manual `Level 1`–`Level 4` presets in automations with `fan.set_percentage`. Actual automatic modes remain presets. Three-speed 1C levels map to 33/66/100% using HA utilities.
- `percentage: 0` turns the device off. `fan.turn_on` with `percentage` or `preset_mode` powers it on and applies that setting. A preset takes precedence when both are supplied.
- Motor RPM remains diagnostic data; the fan percentage uses the active speed setting.
- Panning is not blade reversal: `fan.set_direction` is no longer advertised. Oscillation and supported angle controls remain available.
- Device rejections and unsupported values raise HA action errors. Review error handling in your automations.

### Humidity limits

Ranges and prerequisite modes depend on the model: JSQS 40–80%, MIoT 30–80%, Mjjsq 0–99%, legacy 30–80% in steps of 10. Dehumidifiers accept 40/50/60%; in-range requests round to the nearest 10 (ties round to the even decade). JSQ001 supports power and modes without a target humidity setter. The main entity and auxiliary number use identical validation and select Auto/Humidity first when required.

### Verification and troubleshooting

Local polling defaults to 30 seconds and can be changed in Options. If a device is unavailable, check its local IP, token, and network reachability from HA. Unknown models require an explicit supported profile. Cloud setup can save a supported device while it is temporarily unreachable locally; HA retries during setup.

Tests exercise real drivers and packet codecs with network traffic substituted. Physical device validation is a separate step. Remove the integration through Settings → Devices & Services; its entities and dependent automations will then become unavailable.

### Development

```bash
uv venv --python 3.14.2 .venv
uv pip sync --python .venv/bin/python requirements_test_lock.txt
.venv/bin/python scripts/check_project.py
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check custom_components/ tests/ scripts/
.venv/bin/ruff format --check custom_components/ tests/ scripts/
```

Use a separate environment with `requirements_test_min_lock.txt` for HA 2026.3.4. The current matrix also tests HA 2026.11.2. Bump versions with `python scripts/bump_version.py MAJOR.MINOR.PATCH`, which synchronizes manifest and pyproject. These commands supersede the old environment examples in the preserved AGENTS.md.

Example manual speed action:

```yaml
action: fan.set_percentage
target:
  entity_id: fan.xiaomi_air_purifier
data:
  percentage: 66
```

---

## Breaking Changes in 3.0.0

### Humidifiers moved to `humidifier` platform

Humidifiers are no longer registered as `fan` entities. Entity IDs have changed:

- `fan.xiaomi_*` -> `humidifier.xiaomi_*`
- Service `fan.set_preset_mode` replaced with `humidifier.set_mode`
- New service `humidifier.set_humidity` for setting target humidity
- Automations using `fan.turn_on` / `fan.turn_off` for humidifiers must be updated to `humidifier.turn_on` / `humidifier.turn_off`

### All custom services removed

37 custom services like `xiaomi_miio_airpurifier_ng.fan_set_*` have been removed. Device control is now done via standard entity platforms: `switch`, `number`, `select`, `button`.

### Humidifier binary sensor entity IDs changed

- `binary_sensor.*_water_tank` -> `binary_sensor.*_water_level_low`
- `binary_sensor.*_water_shortage` -> `binary_sensor.*_water_tank_removed`

---

## Requirements

- Home Assistant 2026.3.4 or newer
- Python 3.14.2+
- `python-miio>=0.5.12,<0.6.0`, `construct>=2.10.68,<2.11.0`

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

---

Credits: [Rytilahti](https://github.com/rytilahti/python-miio) for the `python-miio` library, [syssi](https://github.com/syssi/xiaomi_airpurifier) for the original integration.
