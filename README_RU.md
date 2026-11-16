# Xiaomi Air Purifier NG

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2026.3.4%2B-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](CHANGELOG.md)

Кастомная интеграция для Home Assistant для управления устройствами Xiaomi: очистителями воздуха, увлажнителями, вентиляторами, устройствами Air Fresh и осушителями воздуха.

Устройства опрашиваются локально по WiFi через протокол miIO — без облака и интернета.

> Форк [syssi/xiaomi_airpurifier](https://github.com/syssi/xiaomi_airpurifier) с переработанной архитектурой, UI-конфигурацией и поддержкой актуальных версий Home Assistant.

> **Примечание:** Для новых установок рекомендуем рассмотреть [Xiaomi Miot Auto](https://github.com/al-one/hass-xiaomi-miot) — более универсальную интеграцию, которая поддерживает практически все устройства Xiaomi через протокол MIoT, включая Wi-Fi, BLE и ZigBee. Данная интеграция (Xiaomi Air Purifier NG) поддерживается для пользователей, которым важно **полностью локальное** управление без облака и аккаунта Xiaomi, или которым нужна стабильная работа **старых miIO-устройств**. Проект находится в режиме поддержки — исправления багов и PR от сообщества приветствуются, но новые крупные функции не планируются.

---

## Поддерживаемые устройства

### Очистители воздуха (платформа `fan`)

| Название | Модель |
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

### Увлажнители воздуха (платформа `humidifier`)

| Название | Модель |
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

### Приточная вентиляция (платформа `fan`)

| Название | Модель |
| --- | --- |
| Mi Fresh Air Ventilator A1 | dmaker.airfresh.a1 |
| Smartmi Fresh Air System | zhimi.airfresh.va2 |
| Smartmi Fresh Air System PTC | zhimi.airfresh.va4 |
| Mi Fresh Air Ventilator T2017 | dmaker.airfresh.t2017 |

### Напольные вентиляторы (платформа `fan`)

| Название | Модель |
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

### Осушитель воздуха (платформа `climate`)

| Название | Модель |
| --- | --- |
| New Widetech Internet Dehumidifier | nwt.derh.wdh318efw1 |

---

## Установка через HACS

1. Откройте HACS в Home Assistant.
2. Перейдите в раздел **Integrations**.
3. Нажмите меню (три точки) -> **Custom repositories**.
4. Добавьте репозиторий: `https://github.com/dzerik/xiaomi_airpurifier_ng`, категория — **Integration**.
5. Найдите **Xiaomi Air Purifier NG** и нажмите **Download**.
6. Перезапустите Home Assistant.

## Ручная установка

1. Скопируйте папку `custom_components/xiaomi_miio_airpurifier_ng` в директорию `config/custom_components/` вашей установки Home Assistant.
2. Перезапустите Home Assistant.

---

## Настройка

Интеграция настраивается через UI — YAML-конфигурация не используется.

1. Перейдите в **Settings** -> **Devices & Services**.
2. Нажмите **+ Add Integration**.
3. Найдите **Xiaomi Air Purifier NG**.
4. Введите параметры:

| Параметр | Описание |
| --- | --- |
| Host | IP-адрес устройства в локальной сети |
| Token | 32-символьный токен устройства |
| Model | Модель устройства (например, `zhimi.airpurifier.ma4`) |

После добавления интервал опроса можно изменить через **Options** (по умолчанию 30 секунд).

---

## Платформы и сущности

Интеграция автоматически создает сущности в зависимости от возможностей конкретной модели устройства.

| Платформа | Описание |
| --- | --- |
| `fan` | Очистители воздуха, Air Fresh, напольные вентиляторы — включение, скорость, режимы |
| `humidifier` | Увлажнители — включение, целевая влажность, режимы |
| `climate` | Осушитель — включение, целевая влажность, режим HVAC |
| `sensor` | Температура, влажность, AQI, CO2, скорость мотора, состояние фильтра и другие |
| `switch` | Зуммер, LED, детский замок, сухой режим, осциллятор и другие |
| `number` | Любимый уровень, уровень вентилятора, целевая влажность, угол осцилляции и другие |
| `select` | Яркость LED, ориентация дисплея, уровень PTC, режим работы |
| `binary_sensor` | Уровень воды, питание от сети, заряд батареи, статус PTC-нагревателя |
| `button` | Сброс счетчика фильтра |

---

## Как получить токен устройства

Токен необходим для локального подключения. Получить его можно несколькими способами:

- **Xiaomi Cloud Token Extractor** — рекомендуемый способ: [инструкция на сайте Home Assistant](https://www.home-assistant.io/integrations/xiaomi_miio/#xiaomi-cloud-tokens-extractor)
- Через приложение **MiHome** с помощью сниффера трафика или резервной копии (для Android)

---

## Отладка

Для диагностики проблем включите debug-логирование в `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.xiaomi_miio_airpurifier_ng: debug
    miio: debug
```

---

## Переход на 4.0.0

Требуется Home Assistant 2026.3.4+ с Python 3.14.2+. Существующие `unique_id` сущностей сохраняются; перенастройка и повторная авторизация проверяют MAC устройства до сохранения параметров.

- Замените ручные пресеты `Level 1`–`Level 4` в автоматизациях на `fan.set_percentage`. Настоящие автоматические режимы остаются пресетами. Для трёхскоростного 1C уровни отображаются как 33/66/100% по правилам HA.
- `percentage: 0` выключает устройство; `fan.turn_on` с `percentage` или `preset_mode` включает его и применяет параметр. Если заданы оба, приоритет у пресета.
- RPM остаётся диагностическим значением. В стандартном состоянии fan используются проценты активной скорости, а не обороты двигателя.
- Поворот корпуса не считается реверсом лопастей: `fan.set_direction` больше не предлагается. Автоматическое качание и доступный угол поворота сохраняются.
- Отказы устройства и неподдерживаемые значения возвращают ошибку действия HA. Проверьте обработку ошибок в автоматизациях.

### Ограничения влажности

Диапазон и режим зависят от модели: JSQS — 40–80%, MIoT — 30–80%, Mjjsq — 0–99%, legacy — 30–80% с шагом 10. Осушитель поддерживает 40/50/60%; значения внутри диапазона округляются до ближайших 10 (ровно посередине — к чётному десятку). JSQ001 поддерживает питание и режимы, без установки целевой влажности. Основная сущность и дополнительный number используют одинаковые правила; при необходимости сначала включается Auto/Humidity.

### Проверка и диагностика

Данные опрашиваются локально каждые 30 секунд по умолчанию; интервал меняется в настройках. Если устройство недоступно, проверьте локальный IP, токен и доступ HA к сети устройства. Неизвестные модели не добавляются автоматически; нужна явная поддержка профиля. Облачная настройка может сохранить поддерживаемое устройство, временно недоступное в локальной сети; HA повторит подключение при загрузке.

Проверки используют настоящие драйверы и кодеки с подменой сетевого обмена. Проверка на физических устройствах остаётся отдельным этапом. Для удаления используйте меню интеграции в «Настройки → Устройства и службы»; её сущности и автоматизации после этого станут недоступны.

### Разработка

```bash
uv venv --python 3.14.2 .venv
uv pip sync --python .venv/bin/python requirements_test_lock.txt
.venv/bin/python scripts/check_project.py
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check custom_components/ tests/ scripts/
.venv/bin/ruff format --check custom_components/ tests/ scripts/
```

Для HA 2026.3.4 создайте отдельное окружение и используйте `requirements_test_min_lock.txt`. Текущая матрица проверяет HA 2026.11.2. Обновляйте версию командой `python scripts/bump_version.py MAJOR.MINOR.PATCH`, синхронизирующей manifest и pyproject. Актуальные команды этого раздела заменяют устаревшие примеры окружения в сохранённом AGENTS.md.

Пример ручной скорости:

```yaml
action: fan.set_percentage
target:
  entity_id: fan.xiaomi_air_purifier
data:
  percentage: 66
```

---

## Breaking Changes в версии 3.0.0

### Увлажнители переведены на платформу `humidifier`

Увлажнители больше не регистрируются как `fan`-сущности. Entity ID изменились:

- `fan.xiaomi_*` -> `humidifier.xiaomi_*`
- Сервис `fan.set_preset_mode` заменен на `humidifier.set_mode`
- Добавлен сервис `humidifier.set_humidity` для установки целевой влажности
- Автоматизации с `fan.turn_on` / `fan.turn_off` для увлажнителей необходимо обновить на `humidifier.turn_on` / `humidifier.turn_off`

### Удалены все кастомные сервисы

37 кастомных сервисов вида `xiaomi_miio_airpurifier_ng.fan_set_*` удалены. Управление устройствами осуществляется через стандартные entity-платформы: `switch`, `number`, `select`, `button`.

### Изменены Entity ID бинарных сенсоров увлажнителей

- `binary_sensor.*_water_tank` -> `binary_sensor.*_water_level_low`
- `binary_sensor.*_water_shortage` -> `binary_sensor.*_water_tank_removed`

---

## Требования

- Home Assistant 2026.3.4 или новее
- Python 3.14.2+
- `python-miio>=0.5.12,<0.6.0`, `construct>=2.10.68,<2.11.0`

---

## Лицензия

Apache License 2.0. Подробнее см. файл [LICENSE](LICENSE).

---

Благодарности: [Rytilahti](https://github.com/rytilahti/python-miio) за библиотеку `python-miio`, [syssi](https://github.com/syssi/xiaomi_airpurifier) за оригинальную интеграцию.
