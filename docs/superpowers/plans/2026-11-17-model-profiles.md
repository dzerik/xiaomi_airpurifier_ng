# Model Profiles 4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution or superpowers:subagent-driven-development if the user selects delegation. Track steps with the checkboxes below.

**Goal:** Исправить все подтверждённые дефекты аудита и выпустить согласованную реализацию управления устройствами Xiaomi.

**Architecture:** Неизменяемый профиль описывает возможности конкретной модели. Координатор последовательно выполняет операции с устройством и нормализует ответы. Сущности реализуют контракты HA, сохраняя существующие entity unique_id.

**Tech Stack:** Python 3.14.2+, HA 2026.3.4/2026.11.2, python-miio 0.5.12, construct 2.10.70, pytest-homeassistant/pytest-homeassistant-custom-component в отдельных окружениях, Ruff 0.17.5.

**Spec:** [2026-11-17-model-profiles-design.md](../specs/2026-11-17-model-profiles-design.md).

## Global Constraints

- Home Assistant **2026.3.4+**, Python **3.14.2+**.
- Итоговый релиз **4.0.0**; manifest и pyproject всегда имеют одинаковую версию.
- Транспорт: python-miio 0.5.12 в test lock; manifest использует **python-miio>=0.5.12,<0.6.0**, **construct>=2.10.68,<2.11.0** по требованиям Hassfest. Codec проверяется на construct 2.10.68 и 2.10.70.
- Entity unique_id сохраняются; device registry не раздваивается при позднем info.
- Команды и polling одного устройства разделяют один замок; refresh выполняется вне замка.
- Неподдерживаемые значения отклоняются до сетевого вызова; ошибки устройства видны вызывающему коду.
- AGENTS.md не редактировать; существующий `.hypothesis/` не трогать.
- Исходные checkpoint-коммиты уже созданы. Задачи 1–6 составляют один проверяемый changeset; итоговый код коммитится вместе с повышением версии до 4.0.0 после review.
- CLAUDE.md локально исключён из Git: обновить рабочую копию, не менять правило игнорирования и не добавлять принудительно.

## Review Focus

- Прерывание/отмена команды во время executor I/O: следующий запрос не пересекается с ещё работающим потоком; проверяет задача 3.
- Отрицательный MIoT code среди успешных результатов: весь вызов завершается ошибкой; проверяет задача 3.
- Устройство выключено, но помнит прежнюю скорость: HA показывает 0%, а включение с параметрами применяет их; проверяет задача 4.
- MAC записан с дефисами, двоеточиями или другим регистром: identity одинакова, другой MAC отклоняется; проверяет задача 5.
- Необязательное поле отсутствует в первом статусе, появляется позже: создаётся ровно одна поддерживаемая сущность, без второго устройства; проверяют задачи 4 и 5.

## Общие интерфейсы

`device_profiles.py` предоставляет следующие имена:

- `UnsupportedModelError(ValueError)`.
- `SpeedKind(StrEnum)` со значениями `NONE`, `LEGACY`, `LEVELS`, `PERCENTAGE`, `PURIFIER`.
- `HumidityControl`: frozen dataclass с полями `minimum: int`, `maximum: int`, `step: int`, `mode: Enum | None`, `mode_delay: float`; метод `normalize(value: int) -> int`.
- `DeviceProfile`: frozen dataclass с полями `category: DeviceCategory`, `driver: type[Device]`, `features: int`, `attributes: Mapping[str, str]`, `mode_enum: type[Enum] | None`, `speed_kind: SpeedKind`, `speed_range: tuple[int, int] | None`, `humidity: HumidityControl | None`, `select_enums: Mapping[str, type[Enum]]`, `commands: frozenset[str]`, `device_options: Mapping[str, Any]`.
- `get_device_profile(model: str | None) -> DeviceProfile`: возвращает профиль только известной модели, иначе `UnsupportedModelError`.
- `create_device(host: str, token: str, model: str) -> Device`: создаёт драйвер профиля с его явными параметрами, включая специальную JSQS mapping.

`coordinator.py` предоставляет:

- `DeviceCommand`: frozen dataclass, `name: str`, `args: tuple[Any, ...] = ()`, `delay_after: float = 0`.
- `validate_command_result(result: Any) -> None`: принимает успешные miIO/MIoT-ответы, иначе поднимает `HomeAssistantError`.
- `XiaomiMiioDataUpdateCoordinator.profile: DeviceProfile`.
- `async_execute_commands(commands: Sequence[DeviceCommand]) -> None`: выполняет всю последовательность под общим замком, затем обновляет состояние и запрашивает refresh.
- `async_execute_command(name: str, *args: Any) -> None`: однооперационный вариант.
- `async_set_humidity(value: int) -> None`: проверяет профиль и атомарно переключает режим/устанавливает влажность.

`entity.py` предоставляет `_async_command(name: str, *args: Any) -> None`, делегирующий координатору. Все платформы используют его вместо передачи произвольных bound methods в `_try_command`.

### Task 1: Воспроизводимое окружение и управление версиями

**Files:** создать `requirements_test_common.txt`, `requirements_test_min.txt`, `requirements_test_lock.txt`, `requirements_test_min_lock.txt`, `tests/ha_helpers.py`, `scripts/bump_version.py`, `scripts/check_project.py`, `tests/test_project_metadata.py`; изменить `requirements_test.txt`, `pyproject.toml`, `pytest.ini`, `.pre-commit-config.yaml`, `.github/workflows/{tests,lint,release}.yml`, `hacs.json`, `manifest.json` и импорты помощников в тестах.

**Interfaces:** `tests.ha_helpers.MockConfigEntry` выбирает установленный fixture backend. Скрипт `bump_version.py VERSION` обновляет manifest и pyproject одной операцией; `check_project.py` проверяет их равенство, минимальную платформу и runtime requirements.

- [x] Добавить контракт метаданных и тест bump на временной копии файлов; исходные версии репозитория в тесте не менять.

```python
def test_runtime_requirements_match_manifest():
    manifest = json.loads(Path("custom_components/xiaomi_miio_airpurifier_ng/manifest.json").read_text())
    requirements = Path("requirements_test_common.txt").read_text().splitlines()
    assert set(manifest["requirements"]) <= set(requirements)
```

- [x] Запустить `pytest tests/test_project_metadata.py -v` в существующем audit env; зафиксировать отсутствие common requirements как красный результат.
- [x] Вынести общие runtime requirements; текущие тесты используют `pytest-homeassistant==2026.11.2`, минимальные — `pytest-homeassistant-custom-component==0.13.320`. Не фиксировать поверх них несовместимые pytest/asyncio/cov. Общий допустимый cov — `pytest-cov>=7,<8`; lock-файлы фиксируют конкретный результат каждого resolver.
- [x] Заменить импорты MockConfigEntry через один модуль:

```python
try:
    from pytest_homeassistant.common import MockConfigEntry
except ModuleNotFoundError as exc:
    if exc.name != "pytest_homeassistant":
        raise
    from pytest_homeassistant_custom_component.common import MockConfigEntry
```

- [x] Убрать повторную конфигурацию pytest из `pytest.ini`; в pyproject задать `addopts = "-p no:respx"`. Настроить plugin/enable_custom_integrations без двойной регистрации. Использовать Python 3.14.2+, Ruff 0.17.5, pre-commit 4.7.0 и одну конфигурацию линтинга. CI не устанавливает проект через подавляемый `pip install -e .`.
- [x] Проверить обновлённый construct на настоящем miIO codec: собрать ответ с тестовыми token/device_id/payload, разобрать его и сравнить исходный payload. Использовать тестовые константы и codec API установленной версии, без доступа к устройству.
- [x] Создать отдельные окружения и lock-файлы:

```bash
uv pip compile --python-version 3.14.2 requirements_test.txt -o requirements_test_lock.txt
uv pip compile --python-version 3.14.2 requirements_test_min.txt -o requirements_test_min_lock.txt
uv venv --python 3.14 /tmp/xiaomi-ha-current
uv pip sync --python /tmp/xiaomi-ha-current/bin/python requirements_test_lock.txt
uv venv --python 3.14 /tmp/xiaomi-ha-min
uv pip sync --python /tmp/xiaomi-ha-min/bin/python requirements_test_min_lock.txt
/tmp/xiaomi-ha-current/bin/python -m pytest tests/ -q
/tmp/xiaomi-ha-min/bin/python -m pytest tests/ -q
```

Ожидание: исходные тесты и метаданные проходят на обеих HA; ошибки несовместимости нового fixture backend исправляются в `tests/ha_helpers.py`/conftest, без изменения поведения продукта.

### Task 2: Реестр профилей и создание устройств

**Files:** создать `device_profiles.py`, `tests/test_device_profiles.py`; изменить `const.py`, `__init__.py`, `fan.py`, `humidifier.py`, `climate.py`, `fans/{standing,purifier,air_fresh}.py`, `tests/test_init.py`, `tests/test_classify_model.py`.

**Interfaces:** реализовать объявленные выше `DeviceProfile`, `HumidityControl`, `SpeedKind`, `UnsupportedModelError`, `get_device_profile`, `create_device`. Сохранить `_create_device` как совместимый внутренний вход, делегирующий factory профиля.

- [x] Добавить проверки полноты реестра, правильного реального класса драйвера и отсутствия произвольного fallback:

```python
@pytest.mark.parametrize("model", SUPPORTED_MODELS)
def test_profile_factory(model):
    profile = get_device_profile(model)
    device = create_device("192.0.2.1", "0" * 32, model)
    assert type(device) is profile.driver
    assert profile.category is not DeviceCategory.UNKNOWN

def test_unknown_model_is_rejected():
    with pytest.raises(UnsupportedModelError):
        create_device("192.0.2.1", "0" * 32, "unknown.model")
```

- [x] Запустить `pytest tests/test_device_profiles.py -v`; убедиться в красном результате до создания нового модуля.
- [x] Перенести текущие явные группы factory и UI ModelConfig в профили семейств; перечислить исключения известных моделей. Mapping-псевдонимы разрешать только явно, сохранять `_JSQS_MAPPING` как именованную проверяемую mapping.
- [x] Реализовать factory через `profile.driver(ip=host, token=token, model=model, **profile.device_options)`. Классификацию и платформы связать с профилем; избежать циклического импорта const → profiles → const, переместив реализацию классификации в profiles и оставив совместимый lazy-wrapper, если старые потребители ещё используют const.
- [x] Публичные платформы читают features/attributes/mode enum из профиля. Удалить освободившиеся ModelConfig-таблицы только после поиска всех ссылок Serena.
- [x] Выполнить `pytest tests/test_device_profiles.py tests/test_init.py tests/test_classify_model.py -q`; старые тесты, закреплявшие generic fallback, заменить проверками ожидаемого отказа.

### Task 3: Команды, ответы, оптимистическое состояние и сериализация I/O

**Files:** изменить `coordinator.py`, `entity.py`, все вызовы `_try_command` в платформах; создать `tests/test_device_commands.py`; обновить `tests/test_entity.py`, `tests/test_coordinator.py`.

**Interfaces:** реализовать `DeviceCommand`, `validate_command_result`, `async_execute_command(s)` и `_async_command` из общего раздела. `DeviceException` преобразуется в HomeAssistantError; отсутствие команды/возможности — ServiceValidationError.

- [x] Написать контракт результатов:

```python
@pytest.mark.parametrize("response", [["ok"], [{"did": "power", "code": 0}]])
def test_successful_response(response):
    validate_command_result(response)

@pytest.mark.parametrize("response", [[], None, ["error"], [{"code": -4004}], [{"code": 0}, {"code": -1}]])
def test_failed_response(response):
    with pytest.raises(HomeAssistantError):
        validate_command_result(response)
```

- [x] Добавить проверки, использующие `threading.Event` для блокировки fake network call: вторая команда и polling не входят в fake transport до завершения первой; отмена coroutine не освобождает доступ к ещё работающему executor; исключение освобождает замок. В async-тестах ожидание threading.Event выполнять через executor, чтобы не блокировать event loop.
- [x] Запустить новые тесты и получить красный результат.
- [x] Реализовать один замок I/O и единый нормализатор. При отмене shield-ить и дождаться активной executor future до освобождения замка, затем повторно поднять CancelledError. Между командами batch соблюдать `delay_after` под замком. Refresh запрашивать после `async with`.

```python
def validate_command_result(result: Any) -> None:
    if result == ["ok"]:
        return
    if isinstance(result, list) and result and all(
        isinstance(item, dict) and type(item.get("code")) is int and item["code"] == 0
        for item in result
    ):
        return
    raise HomeAssistantError("Device rejected the command")
```

- [x] После принятой команды on/off публиковать новую копию coordinator.data через `async_set_updated_data`, не мутировать словарь без уведомления слушателей. При отказе не публиковать оптимистический успех. Все setters возвращают ошибку вызывающему коду.
- [x] Прогнать `pytest tests/test_device_commands.py tests/test_entity.py tests/test_coordinator.py -q` и полный набор. Переписать старые ожидания `False` на ожидаемые исключения.

### Task 4: Контракты Fan/Humidifier/Climate и дополнительных контролов

**Files:** изменить `fans/{base,standing,purifier,air_fresh}.py`, `humidifier.py`, `climates/dehumidifier.py`, `number.py`, `select.py`, `switch.py`, `button.py`, `coordinator.py`; создать `tests/test_device_contracts.py`; обновить соответствующие платформенные тесты.

**Interfaces:** профиль задаёт поддерживаемые команды и enum; `coordinator.async_set_humidity(value)` используется основной сущностью и number. Поле `speed` остаётся исходным диагностическим значением; нормализованный процент хранить отдельно как `speed_percentage`.

- [x] Перенести воспроизведения из `/tmp/xiaomi-audit-probes.py` в постоянные контрактные тесты с настоящими Device/Status. Подменять `send`/`set_property`, не заменять реальные setters неограниченным MagicMock.

```python
@pytest.mark.parametrize("level, expected", [(1, 33), (2, 66), (3, 100)])
def test_three_speed_levels(hass, level, expected):
    model = "dmaker.fan.1c"
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="aabbccddeeff",
        data={"host": "192.0.2.1", "token": "0" * 32, "model": model},
    )
    device = create_device("192.0.2.1", "0" * 32, model)
    raw = dict.fromkeys(device._get_mapping(), 0)
    raw.update(power=True, fan_level=level, mode=0)
    device.status = Mock(return_value=FanStatus1C(raw))
    coordinator = XiaomiFanCoordinator(hass, entry, device)
    coordinator.data = coordinator._get_status()
    assert XiaomiStandingFan(coordinator).percentage == expected
```

Импорты: Mock из unittest.mock, FanStatus1C из miio.integrations.fan.dmaker.fan_miot, MockConfigEntry из tests.ha_helpers, остальные классы из профилей/coordinator/fans.standing. Аналогично проверить Legacy FanStatus(speed=850, direct_speed=35) → 35%, выключенное устройство → 0%.

- [x] До исправлений получить красные результаты: реальные setters LED/PTC/orientation принимают правильные enum, JSQ001 не вызывает отсутствующий метод, осушитель не получает 30/70/80, `set_percentage(0)` вызывает off, `turn_on(percentage=75)` включает и задаёт скорость.
- [x] Реализовать преобразования по SpeedKind и стандартным утилитам HA; проверить границы 0/1/33/34/66/67/99/100. У purifier выбрать поддерживаемый setter и Fan/Favorite, не применять неподдерживаемый fan_level.
- [x] Удалить ручные Level-presets, согласовать preset_mode/preset_modes с реальными enum. Для ручной скорости применить соответствующий Direct/Normal/Fan/Favorite режим там, где драйвер его предоставляет; у legacy протокола использовать direct/natural setters.
- [x] Реализовать общую влажность: проверка диапазона, округление осушителя до шага 10 и batch переключения Auto/установки target. Для JSQ001 не создавать number, а public setter отклоняет команду ServiceValidationError.
- [x] Дополнительные контролы создаются по capabilities профиля и данным. Late discovery остаётся идемпотентным; enum преобразуются профилем конкретного драйвера. Неправильные option/number значения отклоняются до executor.
- [x] Запустить `pytest tests/test_device_contracts.py tests/test_fan_*.py tests/test_humidifier.py tests/test_climate_dehumidifier.py tests/test_select.py tests/test_number.py tests/test_switch.py tests/test_button.py -q`, затем полный набор.

### Task 5: Валидация конфигурации и стабильность реестра устройств

**Files:** изменить `config_flow.py`, `entity.py`, `coordinator.py`, `__init__.py`; обновить `tests/test_config_flow.py`, `tests/test_entity.py`, `tests/test_init.py`; создать `tests/test_device_identity.py`.

**Interfaces:** локальная функция `normalize_mac(value: str) -> str` применяется ко всем flows/идентификаторам. Config entry unique_id и entity unique_id не перезаписываются при обычной перезагрузке.

- [x] Добавить точные проверки нормализации и reconfigure с другим MAC:

```python
@pytest.mark.parametrize("mac", ["AA:BB:CC:DD:EE:FF", "aa-bb-cc-dd-ee-ff", "AABBCCDDEEFF"])
def test_normalized_identity(mac):
    assert normalize_mac(mac) == "aabbccddeeff"
```

В интеграционном flow-тесте сохранить исходный entry.data, вернуть из device.info другой MAC, выполнить reconfigure и проверить отказ и неизменность entry.data. Повторить для reauth.

- [x] Добавить тесты неизвестной autodetected/manual/cloud модели и пустого supported cloud списка; entry не создаётся. Добавить тест reconfigure без выбранной модели, использующий обнаруженную поддерживаемую модель.
- [x] Получить красный результат; затем валидировать профиль до создания entry, убрать fallback всех облачных устройств и сравнивать MAC до update/reload.
- [x] Добавить registry-тест: сначала info отсутствует, после успешного polling появляется MAC и новый sensor; device registry содержит прежнее единственное устройство, entity unique_id совпадают до/после reload.
- [x] В device_info использовать стабильный entry.unique_id и существующие registry aliases; обновлять firmware/hardware/model существующего DeviceEntry после late info. В этом пути не создавать новое устройство независимо от сущностей.
- [x] Выполнить `pytest tests/test_device_identity.py tests/test_config_flow.py tests/test_entity.py tests/test_init.py -q` и полный набор.

### Task 6: Документация, переводы, release и итоговое review

**Files:** изменить `README.md`, `README_RU.md`, `CHANGELOG.md`, локальный `CLAUDE.md`, `quality_scale.yaml`, `strings.json`, `translations/*.json`, `.github/workflows/validate.yml`; добавить `tests/test_translations.py`; завершить scripts/check_project.py и обновить чекбоксы плана.

**Interfaces:** новые ошибки имеют translation_key и одинаковые placeholders во всех переводах; итоговый `scripts/check_project.py` возвращает ненулевой exit code при рассогласованной версии, runtime dependency или metadata.

- [x] Добавить проверку ключей и placeholders всех языков:

```python
def leaf_keys(value, path=()):
    if not isinstance(value, dict):
        return {path}
    return set().union(*(leaf_keys(child, (*path, key)) for key, child in value.items()))

def test_all_translations_have_source_keys():
    root = Path("custom_components/xiaomi_miio_airpurifier_ng")
    expected = leaf_keys(json.loads((root / "strings.json").read_text()))
    for translation in (root / "translations").glob("*.json"):
        assert leaf_keys(json.loads(translation.read_text())) == expected, translation.name
```

- [x] Запустить тест и подтвердить существующие пропуски. Затем заполнить отсутствующие строки полноценными переводами, добавить ошибки команд/unsupported_model/wrong_device и проверить placeholders.
- [x] Обновить README: HA2026.3.4+/Python3.14.2+, установка и тестовые команды, переход Level-presets → percentages, реальные ограничения влажности и новая семантика отказов. В quality_scale отмечать done только подтверждённые пункты; обновить устаревшие пути/описания локального CLAUDE.md.
- [x] Повысить версию штатным новым скриптом и проверить:

```bash
python scripts/bump_version.py 4.0.0
python scripts/check_project.py
/tmp/xiaomi-ha-current/bin/python -m pytest tests/ --cov=custom_components/xiaomi_miio_airpurifier_ng --cov-report=term-missing -q
/tmp/xiaomi-ha-min/bin/python -m pytest tests/ -q
/tmp/xiaomi-ha-current/bin/ruff check custom_components/ tests/ scripts/
/tmp/xiaomi-ha-current/bin/ruff format --check custom_components/ tests/ scripts/
git diff --check
```

- [x] Выполнить доступные HACS/Hassfest-проверки. Если внешний checker недоступен локально, явно зафиксировать это и оставить обязательный workflow; не заявлять прохождение неисполненной проверки.
- [x] Использовать `requesting-code-review` для независимой проверки всего changeset относительно checkpoint, устранить подтверждённые замечания и повторить затронутые проверки. Делегация разрешена только этим применимым skill либо явным выбором пользователя.
- [x] Сверить все восемь критериев приёмки spec с тестами и выводом команд. Зафиксировать конечный changeset одним коммитом `feat: согласовать профили устройств и управление для Home Assistant 2026` вместе с версией 4.0.0. Не включать `.hypothesis/`, секреты, подпись агента или Co-Authored-By.

## Execution Handoff

Рекомендуемый метод: **native в текущей папке и существующей ветке** — интерфейсы задач тесно связаны, исходный checkpoint уже есть, пользовательские исходники не изменены. Реализатор проходит задачи последовательно, затем запрашивает независимое review целого changeset.

Альтернатива: subagent-driven с отдельной проверкой каждой задачи, если пользователь явно выберет делегацию. Создавать worktree только при выбранной пользователем изоляции; текущий checkout — обычный репозиторий, не worktree.
