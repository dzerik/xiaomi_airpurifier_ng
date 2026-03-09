# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
