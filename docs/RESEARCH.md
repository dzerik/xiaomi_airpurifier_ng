# Исследование: новые устройства, HVAC платформы, HACS submission

Дата: 2026-03-09

---

## 1. Новые устройства — кандидаты на добавление

### 1.1 Air Purifier — новые модели

python-miio `AirPurifierMiot` уже поддерживает эти модели, но наша интеграция их не включает:

| Устройство | Model ID | Протокол | Статус в python-miio | Приоритет |
|---|---|---|---|---|
| Air Purifier 3C | `zhimi.airpurifier.mb4` | MIoT | Supported | Высокий |
| Air Purifier 3C (rev) | `zhimi.airp.mb4a` | MIoT | Supported | Высокий |
| Air Purifier 3C (rev2) | `zhimi.airp.mb5` / `mb5a` | MIoT | Supported | Высокий |
| Air Purifier Pro H | `zhimi.airp.va2` | MIoT | Supported | Высокий |
| Air Purifier 4 Pro | `zhimi.airp.vb4` | MIoT | Supported | Высокий |
| Air Purifier 4 Lite | `zhimi.airp.rmb1` | MIoT | Supported (частично) | Средний |
| Air Purifier 4 Lite (v2) | `zhimi.airp.rma2` | MIoT | Не в списке | Низкий |
| Air Purifier 4 Lite (v3) | `zhimi.airp.rma3` | MIoT | Не в списке | Низкий |
| Air Purifier 3H (alt) | `zhimi.airpurifier.mb3a` / `zhimi.airp.mb3a` | MIoT | Supported | Средний |
| Air Purifier (rma1) | `zhimi.airpurifier.rma1` | MIoT | Supported | Средний |
| Air Purifier 4 Compact | `zhimi.airp.cpa4` | MIoT | Не в списке (тестирован) | Низкий |
| Air Purifier Elite (Y-600) | `zhimi.airp.meb1` / `dmaker.airpurifier.y600` | MIoT | PR в HA core | Средний |

**Вывод:** 7 моделей уже поддерживаются `AirPurifierMiot` — достаточно добавить model ID в маппинг.
Ещё 4-5 моделей требуют тестирования / создания новых маппингов.

### 1.2 Standing Fan — новые модели

| Устройство | Model ID | Протокол | Статус в python-miio | Приоритет |
|---|---|---|---|---|
| Smart Standing Fan 2 | `dmaker.fan.p30` | MIoT | FanMiot | Средний |
| Smart Standing Fan 2 Pro | `dmaker.fan.p33` | MIoT | FanMiot | Высокий |
| Smart Standing Fan Pro EU | `dmaker.fan.p15` | MIoT | FanMiot | Средний |
| Smart Tower Fan | `dmaker.fan.p39` | MIoT | FanMiot | Средний |
| Smart Tower Fan 2 | `dmaker.fan.p45` / `xiaomi.fan.p45` | MIoT | FanMiot | Средний |
| Smart Fan E | `dmaker.fan.1e` | MIoT | Fan1C? | Низкий |
| Mijia Circulation Fan | `dmaker.fan.p28` | MIoT | FanMiot | Низкий |
| Mijia DC Circulation Fan | `dmaker.fan.p220` | MIoT | Неизвестно | Низкий |
| Air Circulation Fan | `xiaomi.fan.p51` | MIoT | Неизвестно | Низкий |
| Smartmi Standing Fan 3 | `zhimi.fan.za5` | MIoT | FanZA5 (dedicated) | Высокий |
| Smart Purifying Fan | `dreame.fan.p2018` | MIoT | Dreame, не miio | Низкий |

**Вывод:** p33, p15, p39, p45, za5 — наиболее востребованные. Все MIoT, работают через `FanMiot` / `FanZA5`.

### 1.3 Humidifier — новые модели

| Устройство | Model ID | Протокол | Статус в python-miio | Приоритет |
|---|---|---|---|---|
| Smart Evaporative Humidifier | `xiaomi.humidifier.3lite` | MIoT | Не поддерживается | Средний |
| Mijia Evaporative Humidifier Pro | Неизвестен | MIoT | Не поддерживается | Низкий |
| Smartmi Evaporative Humidifier 3 | Неизвестен | MIoT | Не поддерживается | Низкий |

**Вывод:** Новых humidifier моделей, поддерживаемых python-miio, мало. `xiaomi.humidifier.3lite` — главный кандидат, но потребуется реализация через genericmiot или новый класс.

### 1.4 Air Fresh — новые модели

| Устройство | Model ID | Протокол | Статус в python-miio | Приоритет |
|---|---|---|---|---|
| Mi Fresh Air Ventilator C1-80 | `zhimi.airfresh.ua1` | MIoT | genericmiot only | Низкий |

Существующие 4 модели покрывают основные устройства.

### 1.5 Dehumidifier — новые модели

| Устройство | Model ID | Протокол | Статус в python-miio | Приоритет |
|---|---|---|---|---|
| Widetech Dehumidifier 312EN | `nwt.derh.312en` | MIoT | Supported (PR #1581) | Средний |
| Mijia Smart Dehumidifier 22L | `dmaker.derh.22l` | MIoT | Нет (custom integration) | Низкий |
| Mijia Smart Dehumidifier 50L | `dmaker.derh.50l` | MIoT | Нет (custom integration) | Низкий |
| Xiaomi Smart Dehumidifier Lite | `xiaomi.derh.lite` | MIoT | Нет (community patch) | Низкий |

### 1.6 Сводная таблица приоритетов

**Высокий приоритет (просто добавить model ID):**
- `zhimi.airpurifier.mb4`, `zhimi.airp.mb4a`, `zhimi.airp.mb5`, `zhimi.airp.mb5a` — Air Purifier 3C
- `zhimi.airp.va2` — Air Purifier Pro H
- `zhimi.airp.vb4` — Air Purifier 4 Pro
- `dmaker.fan.p33` — Standing Fan 2 Pro

**Средний приоритет (требует небольшой работы):**
- `zhimi.airp.rmb1` — Air Purifier 4 Lite
- `zhimi.airp.mb3a` / `zhimi.airpurifier.mb3a` — Air Purifier 3H alt
- `zhimi.airpurifier.rma1` — Air Purifier variant
- `dmaker.fan.p15`, `dmaker.fan.p39`, `dmaker.fan.p45` — новые вентиляторы
- `zhimi.airp.meb1` — Air Purifier Elite

**Низкий приоритет (требует исследования):**
- `zhimi.airp.rma2`, `zhimi.airp.rma3`, `zhimi.airp.cpa4`
- `xiaomi.humidifier.3lite`
- `dmaker.fan.p28`, `dmaker.fan.p220`, `xiaomi.fan.p51`

---

## 2. HVAC платформы — анализ целесообразности

### Текущее состояние

| Тип устройства | Текущая платформа | Стандарт HA |
|---|---|---|
| Air Purifier | `fan` | `fan` — корректно |
| Standing Fan | `fan` | `fan` — корректно |
| Air Fresh | `fan` | `fan` — корректно |
| Humidifier | `humidifier` | `humidifier` — корректно (уже мигрировали в 3.0.0) |
| Dehumidifier | `climate` | `climate` — допустимо |

### Анализ по типам

#### Air Purifier на платформе `fan` — ОСТАВИТЬ
- `fan` — правильная платформа. HA core использует `fan` для air purifiers.
- Очистители воздуха — это по сути вентиляторы с фильтром.
- `climate` не подходит: нет управления температурой, нет HVAC modes в привычном смысле.
- Preset modes (Auto, Silent, Favorite) — стандартная фича fan entity.

#### Standing Fan на платформе `fan` — ОСТАВИТЬ
- Абсолютно правильная платформа.
- FanEntity поддерживает: speed percentage, preset_modes, oscillate, direction — всё что нужно.

#### Air Fresh на платформе `fan` — ОСТАВИТЬ
- Приточная вентиляция — по сути вентилятор.
- `climate` мог бы подойти (есть PTC-нагреватель), но:
  - Основная функция — вентиляция, а не обогрев/охлаждение
  - Нет термостата (нельзя задать целевую температуру)
  - PTC — это вспомогательная функция, управляется через switch entity

#### Humidifier на платформе `humidifier` — УЖЕ МИГРИРОВАЛИ
- Мигрировали в 3.0.0-alpha.18. Всё корректно.

#### Dehumidifier на платформе `climate` — ДОПУСТИМО
- `climate` — единственная стандартная платформа HA для осушителей.
- HVACMode.DRY — стандартный режим.
- Поддержка target_humidity, current_humidity — всё есть.
- Альтернативы нет: `humidifier` с `HumidifierDeviceClass.DEHUMIDIFIER` тоже возможен, но `climate` лучше поддерживается UI.

### Рекомендация

**Никаких миграций не нужно.** Все устройства используют правильные платформы:
- `fan` для purifier/fan/airfresh
- `humidifier` для humidifier
- `climate` для dehumidifier

---

## 3. Подача в HACS Default Repository

### 3.1 Что такое HACS Default

HACS Default — это список репозиториев, которые отображаются в HACS по умолчанию, без необходимости вручную добавлять custom repository URL. Попадание в default = максимальная видимость.

### 3.2 Предварительные требования

#### Репозиторий на GitHub
- [x] Публичный репозиторий
- [x] Описание (description) заполнено
- [x] Topics заданы (home-assistant, hacs, xiaomi, miio, и т.д.)
- [x] Issues включены
- [x] Не архивирован

#### Структура репозитория
- [x] `custom_components/xiaomi_miio_airpurifier_ng/` — правильная структура
- [x] `manifest.json` — со всеми обязательными полями (domain, name, documentation, issue_tracker, codeowners, version)
- [x] `hacs.json` — НУЖНО СОЗДАТЬ! Минимально: `{"name": "Xiaomi Air Purifier NG"}`
- [x] README.md с описанием

#### Brand images (HA 2026.3+)
- [x] `brand/icon.png` — уже есть! В HA 2026.3+ custom integration может хранить brand images локально.
- [ ] Для HACS validation нужно ЛИБО локальные brand images, ЛИБО PR в home-assistant/brands.

#### CI/CD
- [x] HACS validation action (`hacs/action@main` с `category: integration`)
- [x] Hassfest validation (`home-assistant/actions/hassfest@master`)
- [x] Все checks проходят (Lint, Tests, Validate — все зелёные)

#### Релизы
- [x] Как минимум 1 GitHub release (у нас v3.0.0)

### 3.3 Создание hacs.json

В корне репозитория нужен файл `hacs.json`:

```json
{
  "name": "Xiaomi Air Purifier NG",
  "homeassistant": "2024.8.0",
  "render_readme": true
}
```

### 3.4 Процесс подачи (пошаговый)

1. **Убедиться что все checks зелёные** — HACS action, hassfest, тесты

2. **Создать `hacs.json`** в корне репозитория

3. **Форкнуть `hacs/default`** — https://github.com/hacs/default

4. **Создать новую ветку** (НЕ из master напрямую)

5. **Добавить репозиторий** в файл `integration` (JSON):
   - Открыть файл `integration`
   - Добавить `"dzerik/xiaomi_airpurifier_ng"` в **алфавитном порядке**
   - НЕ в конец файла!

6. **Создать PR** по шаблону:
   - Заполнить чеклист:
     - [x] Прочитал документацию по публикации
     - [x] Добавил HACS action в репозиторий
     - [x] Добавил hassfest action в репозиторий
     - [x] Все actions проходят без отключённых checks
     - [x] Ссылка на успешный action run
     - [x] Создал релиз после успешных validation actions
   - PR должен быть editable (подавать от личного аккаунта, не от organization)

7. **Дождаться автоматических проверок**:
   - Check brands (integration → brands images)
   - Check HACS (HACS validation)
   - Check HACS manifest (hacs.json)
   - Check archived (не архивирован)
   - Check releases (есть релиз)
   - Check owner (подающий = owner/contributor)
   - Check JSON (PR файлы валидный JSON)
   - Check sorted (алфавитный порядок)

8. **Дождаться review** — HACS растёт, обзор может занять МЕСЯЦЫ

### 3.5 Автоматические CI-проверки на PR в hacs/default

При подаче PR автоматически запускаются 11 проверок:

| # | Проверка | Что проверяет |
|---|----------|---------------|
| 1 | Preflight | Определяет репозиторий и категорию из diff |
| 2 | JQ | Валидность JSON |
| 3 | JSON schema | Структура JSON |
| 4 | Editable PR | PR позволяет maintainerам редактировать |
| 5 | Sorted | Алфавитный порядок записей |
| 6 | Owner | Автор PR = owner/contributor репозитория |
| 7 | Releases | Есть хотя бы один GitHub release |
| 8 | Removed repository | Репозиторий не был ранее удалён из HACS |
| 9 | Existing repository | Репозиторий ещё не в HACS default |
| 10 | Hassfest | Docker-контейнер hassfest проверяет код |
| 11 | HACS action | Полная HACS-валидация репозитория |

ВСЕ 11 должны быть SUCCESS.

### 3.6 Частые причины отказа

- PR шаблон не заполнен
- Запись добавлена не в алфавитном порядке
- hacs.json отсутствует или без поля `name`
- Нет releases
- Нет description/topics на GitHub repo
- Отключённые checks в CI или `ignore` ключ в HACS action
- Brand images отсутствуют (нет ни локальных brand/, ни PR в home-assistant/brands)
- PR подан от organization аккаунта (не editable)
- Комментирование PR или запрос review — maintainers закроют PR
- Дублирование PR (нельзя открывать несколько PR)

### 3.8 home-assistant/brands — нужно ли?

С HA 2026.3 custom integrations могут хранить brand images локально в `brand/` директории.
Однако HACS validation check "Check brands" проверяет наличие в home-assistant/brands ИЛИ локально.

**Наш статус:** у нас есть `brand/icon.png` — HACS validation уже проходит.

Для полноты можно также подать PR в home-assistant/brands, но это НЕ обязательно с HA 2026.3+.

### 3.9 Что нам осталось сделать

1. **Создать `hacs.json`** в корне репозитория
2. **Убедиться что все CI checks зелёные** (уже зелёные!)
3. **Форкнуть hacs/default и создать PR**
4. **Ждать review**

---

## Источники

- [python-miio docs](https://python-miio.readthedocs.io/)
- [python-miio GitHub](https://github.com/rytilahti/python-miio)
- [syssi/xiaomi_airpurifier issues](https://github.com/syssi/xiaomi_airpurifier/issues)
- [HACS Publisher docs](https://www.hacs.xyz/docs/publish/include/)
- [HACS General docs](https://www.hacs.xyz/docs/publish/start/)
- [hacs/default repo](https://github.com/hacs/default)
- [HA Developer Docs — Climate](https://developers.home-assistant.io/docs/core/entity/climate)
- [HA Developer Docs — Fan](https://developers.home-assistant.io/docs/core/entity/fan)
- [HA Developer Docs — Humidifier](https://developers.home-assistant.io/docs/core/entity/humidifier)
- [HA Brands proxy API (2026.3)](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/)
- [Xiaomi MIoT Spec](https://home.miot-spec.com/)
- [hacs/default PR #3122](https://github.com/hacs/default/pull/3122)
