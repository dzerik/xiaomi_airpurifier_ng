# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-03-09

### Fixed
- **coordinator**: «Unable to discover» (устройство недоступно по сети) больше не вызывает reauth flow — теперь корректно обрабатывается как временная недоступность (UpdateFailed). Reauth запрашивается только при реальных ошибках токена.

### Changed
- Полная переработка архитектуры интеграции (DataUpdateCoordinator, Config Flow, entity platforms)
- Увлажнители переведены на стандартную платформу `humidifier`
- Удалены 37 кастомных сервисов — управление через стандартные entity-платформы (switch, number, select, button)
- Покрытие тестами: 470 тестов, 94% coverage
- README на английском и русском языках

### Breaking Changes
- Entity ID увлажнителей: `fan.xiaomi_*` → `humidifier.xiaomi_*`
- Entity ID бинарных сенсоров: `binary_sensor.*_water_tank` → `binary_sensor.*_water_level_low`
- Все кастомные сервисы `xiaomi_miio_airpurifier_ng.fan_set_*` удалены

## [3.0.0-rc.1] - 2026-03-09

### Changed
- **Покрытие тестами**: 91% → 94% (316 → 469 тестов)
  - `entity.py`: 86% → 100%
  - `button.py`: 70% → 100%
  - `__init__.py`: 71% → 99%
  - `binary_sensor.py`: 77% → 98%
- README.md полностью переписан: поддерживаемые устройства, установка HACS, настройка, платформы, breaking changes

### Added
- Тесты для `_create_device()` (25 тестов, все ветки моделей)
- Тесты для `_create_coordinator()` (7 тестов, все категории)
- Тесты для `XiaomiMiioEntity` (is_on, extra_state_attributes, _async_device_on/off, device_info)
- Тесты для `button.py` (async_press, async_setup_entry)
- Тесты для `binary_sensor.py` (discovery, is_on)

## [3.0.0-alpha.20] - 2026-03-09

### Changed
- **entity.py**: Вынесены общие методы в базовый класс `XiaomiMiioEntity`:
  - `is_on` property — единая логика проверки power/is_on
  - `extra_state_attributes` property — единая логика с _available_attributes/_state_attrs
  - `_async_device_on()` / `_async_device_off()` — общие helpers для on/off с optimistic state update
- **fans/base.py**: Удалены дублированные `is_on`, `extra_state_attributes`, `async_turn_on`, `async_turn_off` (наследуются из entity.py)
- **humidifier.py**: Удалены дублированные `is_on`, `extra_state_attributes`, `async_turn_on`, `async_turn_off`
- **climates/dehumidifier.py**: Удалены дублированные `extra_state_attributes`, `async_set_hvac_mode` упрощён через `_async_device_on`/`_async_device_off`
- Дублирование Python кода снижено: 8 клонов → 3, 1.9% → 0.94%

## [3.0.0-alpha.19] - 2026-03-09

### Fixed
- **binary_sensor**: Исправлена инвертированная семантика датчиков воды для jsq2w/jsqs:
  - `water_tank` (CONNECTIVITY) → `water_level_low` (PROBLEM) — `tank_filed=True` означает мало воды
  - `water_shortage` → `water_tank_removed` (PROBLEM) — `water_shortage_fault=True` означает бак снят
- **jsq2w mapping**: Добавлен explicit MIOT mapping для `AirHumidifierJsqs`, подавляет warning "Unable to find mapping for deerma.humidifier.jsq2w"

### Changed
- Обновлены все 14 файлов переводов с новыми именами binary sensor

### Breaking Changes
- **Entity ID бинарных сенсоров изменился**: `binary_sensor.*_water_tank` → `binary_sensor.*_water_level_low`, `binary_sensor.*_water_shortage` → `binary_sensor.*_water_tank_removed`

## [3.0.0-alpha.18] - 2026-03-09

### Added
- **HUMIDIFIER PLATFORM**: Увлажнители теперь используют стандартную HA платформу `humidifier` вместо `fan`
  - `target_humidity` / `current_humidity` — стандартные свойства HA
  - `async_set_humidity()` — установка целевой влажности
  - `async_set_mode()` — переключение режимов (Auto, Silent, Medium, High и др.)
  - `HumidifierDeviceClass.HUMIDIFIER` — правильная классификация устройства
  - Поддержка всех 13 моделей увлажнителей (zhimi, deerma, shuii)
  - Совместимость со стандартной карточкой Humidifier и community cards (Mushroom, mini-humidifier)
- 41 новый тест для humidifier platform (338 тестов всего)

### Changed
- Увлажнители убраны из `_FAN_ENTITY_MAP` в `fan.py`
- Добавлен `Platform.HUMIDIFIER` в список платформ

### Breaking Changes
- **Entity ID увлажнителей изменился**: `fan.xiaomi_*` → `humidifier.xiaomi_*`
- Автоматизации, использующие `fan.turn_on`/`fan.turn_off` для увлажнителей, нужно обновить на `humidifier.turn_on`/`humidifier.turn_off`
- Сервис `fan.set_preset_mode` заменён на `humidifier.set_mode`
- Новый сервис `humidifier.set_humidity` для установки целевой влажности

## [3.0.0-alpha.17] - 2026-03-09

### Changed
- Удалены dead code методы из fan-классов (18 методов, 776 строк):
  - `air_fresh.py`: led_brightness, ptc on/off, ptc_level, display_orientation, reset_filter
  - `humidifier.py`: led on/off, led_brightness, motor_speed, wet_protection on/off
  - `standing.py`: oscillation_angle, delay_off, led_brightness, natural_mode on/off
  - `purifier.py`: led_brightness
- Очищены неиспользуемые импорты в исходных и тестовых файлах

### Removed
- 18 dead code методов, функциональность которых перенесена в entity-платформы (switch, number, select, button)
- 12 тестовых классов для удалённых методов

## [3.0.0-alpha.16] - 2026-03-09

### Changed
- Удалены legacy services, `DeviceServiceMixin` и `services.yaml`
- Удалён `service_mixin.py` (452 строки)
- Удалён `services.yaml` (476 строк)
- Удалены все `SERVICE_*` константы из `const.py`
- Очищены секции `"services"` из `strings.json` и всех 14 файлов переводов

### Added
- Switch entities для `clean_mode` и `extra_features`
- Dynamic entity discovery для всех вспомогательных платформ (sensor, switch, number, select, binary_sensor)

### Breaking Changes
- Все 37 custom services удалены — используйте стандартные entity-платформы (switch, number, select, button)

## [3.0.0-alpha.12] - 2026-03-09

### Changed
- **ARCHITECTURE**: Extract `DeviceServiceMixin` from God class `fans/base.py` (573→120 lines, 28 service methods moved to `service_mixin.py`)
- **ARCHITECTURE**: Unify model routing with `classify_model()` and `DeviceCategory` enum — single source of truth for model→category mapping (replaces 3 duplicated routing blocks)
- **ARCHITECTURE**: Type `coordinator.data` with TypedDict (`PurifierStatusData`, `HumidifierStatusData`, `FanStatusData`, `AirFreshStatusData`, `DehumidifierStatusData`)
- Remove 6 duplicated service methods from `climates/dehumidifier.py` (now inherited from mixin)

### Added
- 163 new unit tests (505 total) for `service_mixin.py` and `classify_model()`
- Test coverage: 89% → 93% overall, `service_mixin.py` 100%, `const.py` 100%

## [3.0.0-alpha.11] - 2026-03-09

### Changed
- Refactor coordinator.py: extract _extract_attrs/_extract_str_attrs helpers, eliminating all E-grade complexity blocks
- Replace magic numbers 33.33/6.25 with named constants MIOT_PERCENT_PER_LEVEL/LEGACY_PERCENT_PER_LEVEL
- Fix P8 flag confusion: P8 now exclusively _is_1c (not simultaneously _is_p5_style)
- Remove duplicated _attr_has_entity_name in fans/base.py and climates/dehumidifier.py

### Added
- 313 new unit tests (342 total), covering fans/*, climates/*, switch, select, number
- Test coverage: 58% → 89% overall

## [3.0.0-alpha.10] - 2026-03-09

### Fixed
- **CRITICAL**: Fix `bool("off") == True` bug — devices always appeared "on" (fans/base.py, climates/dehumidifier.py)
- Fix `filter_type` falsy check losing value 0 in coordinator
- Fix `FanMoveDirection` ValueError not caught in standing fan
- Fix dehumidifier enum conversion errors with falsy checks for mode and fan_speed
- Fix dehumidifier `supported_features` handling both raw and string mode values

### Added
- `XiaomiAirDehumidifierCoordinator` — dedicated coordinator for dehumidifier devices
- Dehumidifier coordinator routing in `_create_coordinator()` for `nwt.derh.*` models

## [3.0.0-alpha.9] - 2026-03-09

### Fixed
- Fix 4 failing tests (mock coordinator serialization errors)

### Added
- Coordinator test suite (13 tests, 96% coverage for coordinator.py)
- CHANGELOG.md

## [3.0.0-alpha.8] - 2026-03-09

### Fixed
- Add dehumidifier model (nwt.derh.*) to device factory
- Pin python-miio dependency to >=0.5.12,<1.0.0

### Changed
- Update .gitignore with standard Python/IDE entries

## [3.0.0-alpha.7] - 2026-03-09

### Added
- EntityCategory.CONFIG for all switch entities
- EntityCategory.DIAGNOSTIC for status/filter sensors
- Synchronized strings.json and translations/en.json with full entity coverage

## [3.0.0-alpha.6] - 2026-03-09

### Added
- Register 37 fan entity services (buzzer, LED, child lock, favorite level, etc.)
- Register 6 climate entity services (buzzer, LED, child lock)

### Fixed
- Protect all enum conversions in preset_mode handlers with try/except KeyError

## [3.0.0-alpha.5] - 2026-03-09

### Fixed
- Cache device.info() in coordinator to prevent blocking I/O in HA event loop
- Fix falsy value loss: led_brightness=0, ptc_level=0, display_orientation=0 no longer converted to None
- Remove dead code: DATA_KEY, DEFAULT_RETRIES, CONF_RETRIES, PLATFORMS constants

### Changed
- Extract _try_command and _extract_value_from_attribute to base entity class (DRY)
- Extract _parse_mode to base coordinator class (DRY)
- Remove duplicate methods from fans/base.py and climates/dehumidifier.py

## [3.0.0-alpha.4] - 2026-03-08

### Fixed
- Add relative_humidity support for JSQS humidifiers

## [3.0.0-alpha.3] - 2026-03-08

### Added
- Select entity for operation mode selection

## [3.0.0-alpha.2] - 2026-03-08

### Added
- Switch entities for JSQS humidifiers and new controls

### Fixed
- Fix OperationMode handling

## [3.0.0-alpha.1] - 2026-03-08

### Fixed
- Always convert number values to int

### Added
- All available sensors for all device types
- Binary sensors for humidifier water status
- Options Flow for polling interval configuration
- Integration icon

### Changed
- Use AirHumidifierJsqs for jsq2w and jsq5 models

## [3.0.0-alpha.0] - 2026-03-07

### Added
- Complete rewrite of Xiaomi Air Purifier NG integration
- Config Flow UI setup (host, token, model)
- DataUpdateCoordinator-based polling architecture
- Support for 50+ device models (air purifiers, humidifiers, fans, air fresh, dehumidifiers)
- Tests, reauthentication flow, and quality_scale

## [1.0.0] - 2026-03-07

### Added
- Initial release
