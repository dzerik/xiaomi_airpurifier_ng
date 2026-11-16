# Repository Guidelines

## Структура проекта

Xiaomi Air Purifier NG — интеграция Home Assistant для локального управления устройствами Xiaomi через `python-miio`. Проект находится в режиме поддержки: отдавайте приоритет исправлениям и совместимости.

- `custom_components/xiaomi_miio_airpurifier_ng/` — исходный код интеграции; далее пути модулей указаны относительно этого каталога.
- `__init__.py`, `config_flow.py` — жизненный цикл и настройка; `coordinator.py`, `entity.py` — опрос устройств и базовые сущности.
- `fans/`, `climates/` — реализации семейств устройств; платформы датчиков и переключателей находятся рядом.
- `strings.json`, `translations/` — интерфейсные строки; `brand/` — изображения бренда.
- `tests/` — тесты и общие фикстуры в `conftest.py`; `docs/` — исследования, архитектура и иллюстрации.

## Подготовка и команды разработки

Для разработки используйте Python 3.12+ согласно `pyproject.toml`; CI проверяет Python 3.12 и 3.13. Выполняйте команды из корня репозитория в виртуальном окружении:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements_test.txt
python -m pip install 'construct==2.10.68' 'python-miio>=0.5.12,<1.0.0' ruff
python -m pytest tests/ -v
ruff check custom_components/ tests/
ruff format --check custom_components/ tests/
```

`pytest` запускает тесты; Ruff проверяет стиль и форматирование. Для применения форматирования выполните `ruff format custom_components/ tests/`. Дополнительные pre-commit проверки включают Flake8.

Отдельной сборки нет. Для ручной проверки скопируйте каталог интеграции в `config/custom_components/` тестового Home Assistant, перезапустите его и добавьте интеграцию через интерфейс.

## Стиль и архитектура

Используйте отступы в четыре пробела, `snake_case` для функций и модулей, `PascalCase` для классов, `UPPER_SNAKE_CASE` для констант. Ruff настроен на строки длиной 100 символов и сортировку импортов. Создавайте логгер через `logging.getLogger(__name__)`.

Сохраняйте централизованный опрос через `DataUpdateCoordinator` и общую базу сущностей. Английские строки редактируйте в `strings.json`, согласовывая переводы.

## Тестирование

Используются `pytest`, `pytest-asyncio`, `pytest-homeassistant-custom-component` и `pytest-cov`. Называйте файлы `test_<module>.py`, функции — `test_<behavior>`. Переиспользуйте фикстуры и подменяйте обращения к устройствам.

При исправлении ошибки добавляйте регрессионную проверку. Для отчёта покрытия:

```bash
python -m pytest tests/ --cov=custom_components/xiaomi_miio_airpurifier_ng --cov-report=term-missing
```

Числовой порог покрытия не установлен. Перед PR обеспечьте прохождение тестов, Ruff, HACS и Hassfest в CI.

## Коммиты и Pull Request

Следуйте истории: `fix: описание`, `feat: описание`, `refactor: описание`, `docs: описание`, `chore: описание`. Используйте ветки `fix/<name>`, `feat/<name>` или `chore/<name>` от `main`.

Согласно `CLAUDE.md`, при каждом коммите повышайте SemVer в `manifest.json`. В PR опишите проблему, изменения и проверки; приложите связанную задачу, если она есть, и снимки экрана при изменениях интерфейса.

## Конфигурация и безопасность

Храните токены устройств, пароли Xiaomi и настройки подключения вне Git. Используйте обезличенные данные в тестах, логах и диагностических примерах.
