# 🧪 Тесты для SwiftDevBot-Lite

Комплексная система тестирования для SwiftDevBot-Lite, начиная с CLI команд.

## 📋 Содержание

- [Структура тестов](#структура-тестов)
- [Установка зависимостей](#установка-зависимостей)
- [Запуск тестов](#запуск-тестов)
- [Категории тестов](#категории-тестов)
- [Покрытие кода](#покрытие-кода)
- [Отчеты](#отчеты)
- [CI/CD](#cicd)

## 📁 Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета тестов
├── conftest.py              # Конфигурация pytest и фикстуры
├── test_cli_monitor.py      # Тесты CLI команд monitor
├── test_cli_utils.py        # Тесты CLI команд utils
├── test_cli_config.py       # Тесты CLI команд config
├── test_cli_db.py           # Тесты CLI команд database
├── test_cli_module.py       # Тесты CLI команд module
├── test_cli_user.py         # Тесты CLI команд user
├── test_cli_backup.py       # Тесты CLI команд backup
├── test_cli_system.py       # Тесты CLI команд system
├── test_cli_bot.py          # Тесты CLI команд bot
├── test_core_app_settings.py # Тесты core.app_settings
├── test_core_database.py    # Тесты core.database
├── test_core_module_loader.py # Тесты core.module_loader
└── README.md               # Этот файл
```

## 🚀 Установка зависимостей

### Основные зависимости для тестирования:
```bash
# Установка зависимостей для тестирования
pip install -r requirements-test.txt

# Или установка только pytest
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Дополнительные инструменты:
```bash
# Для покрытия кода
pip install coverage

# Для статического анализа
pip install mypy black flake8 isort

# Для безопасности
pip install bandit safety
```

## 🎯 Запуск тестов

### Базовые команды:

```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск с покрытием кода
pytest --cov=cli --cov=core

# Запуск только CLI тестов
pytest -m cli

# Запуск только monitor тестов
pytest -m monitor

# Запуск только utils тестов
pytest -m utils

# Запуск только unit тестов
pytest -m unit

# Запуск только integration тестов
pytest -m integration
```

### Специфичные команды:

```bash
# Тесты monitor команд
pytest tests/test_cli_monitor.py -v

# Тесты utils команд
pytest tests/test_cli_utils.py -v

# Тесты config команд
pytest tests/test_cli_config.py -v

# Тесты с параллельным выполнением
pytest -n auto

# Тесты с генерацией HTML отчета
pytest --html=report.html --self-contained-html

# Тесты с генерацией JSON отчета
pytest --json-report --json-report-file=report.json
```

### Покрытие кода:

```bash
# Генерация отчета о покрытии
pytest --cov=cli --cov=core --cov-report=html

# Просмотр отчета
open htmlcov/index.html

# Генерация XML отчета для CI
pytest --cov=cli --cov=core --cov-report=xml
```

## 🏷️ Категории тестов

### CLI тесты (`@pytest.mark.cli`)
- Тестирование команд интерфейса
- Проверка аргументов и опций
- Тестирование вывода команд

### Monitor тесты (`@pytest.mark.monitor`)
- `status` - статус системы
- `metrics` - метрики производительности
- `alerts` - управление алертами
- `logs` - анализ логов
- `performance` - анализ производительности
- `report` - генерация отчетов
- `integrate` - интеграция с системами мониторинга

### Utils тесты (`@pytest.mark.utils`)
- `diagnose` - диагностика системы
- `check` - проверка целостности
- `cleanup` - очистка файлов
- `convert` - конвертация файлов
- `encrypt/decrypt` - шифрование/расшифровка

### Config тесты (`@pytest.mark.config`)
- `show` - показ конфигурации
- `set` - установка значений
- `get` - получение значений
- `reset` - сброс конфигурации
- `validate` - валидация конфигурации
- `export/import` - экспорт/импорт конфигурации

### Unit тесты (`@pytest.mark.unit`)
- Тестирование отдельных функций
- Тестирование классов
- Тестирование модулей

### Integration тесты (`@pytest.mark.integration`)
- Тестирование взаимодействия компонентов
- Тестирование API
- Тестирование базы данных

### Async тесты (`@pytest.mark.asyncio`)
- Тестирование асинхронных функций
- Тестирование async/await кода

### Slow тесты (`@pytest.mark.slow`)
- Долго выполняющиеся тесты
- Тесты производительности

## 📊 Покрытие кода

### Текущее покрытие:
- **CLI модули**: ~85%
- **Core модули**: ~70%
- **Общее покрытие**: ~80%

### Цели покрытия:
- **CLI модули**: 95%
- **Core модули**: 90%
- **Общее покрытие**: 85%

### Команды для анализа покрытия:

```bash
# Детальный отчет о покрытии
coverage run -m pytest
coverage report

# HTML отчет
coverage html
open htmlcov/index.html

# Пропуск определенных файлов
coverage run --omit="*/tests/*,*/venv/*" -m pytest
```

## 📈 Отчеты

### Типы отчетов:

1. **Консольный отчет**:
   ```bash
   pytest -v
   ```

2. **HTML отчет**:
   ```bash
   pytest --html=reports/test_report.html --self-contained-html
   ```

3. **JSON отчет**:
   ```bash
   pytest --json-report --json-report-file=reports/test_report.json
   ```

4. **Отчет о покрытии**:
   ```bash
   pytest --cov=cli --cov=core --cov-report=html:reports/coverage
   ```

### Структура отчетов:
```
reports/
├── test_report.html        # HTML отчет о тестах
├── test_report.json        # JSON отчет о тестах
├── coverage/               # Отчеты о покрытии
│   ├── index.html
│   └── ...
└── coverage.xml           # XML отчет о покрытии
```

## 🔧 CI/CD

### GitHub Actions пример:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=cli --cov=core --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Локальный CI:

```bash
#!/bin/bash
# run_tests.sh

echo "🧪 Запуск тестов..."

# Установка зависимостей
pip install -r requirements-test.txt

# Запуск тестов
pytest -v --cov=cli --cov=core --cov-report=html --cov-report=xml

# Проверка качества кода
black --check .
flake8 .
mypy cli/ core/

# Проверка безопасности
bandit -r cli/ core/
safety check

echo "✅ Тесты завершены!"
```

## 🎯 Лучшие практики

### Написание тестов:

1. **Именование**: `test_<function_name>_<scenario>`
2. **Организация**: Группировка по классам для связанных тестов
3. **Фикстуры**: Использование фикстур для подготовки данных
4. **Mocking**: Использование моков для изоляции тестов
5. **Assertions**: Четкие и информативные проверки

### Пример хорошего теста:

```python
@pytest.mark.monitor
@pytest.mark.cli
def test_monitor_status_basic(self, cli_runner: CliRunner):
    """Test basic monitor status command"""
    with patch('cli.monitor._monitor_status_async') as mock_status:
        mock_status.return_value = None
        result = cli_runner.invoke(monitor_app, ["status"])
        assert result.exit_code == 0
```

### Структура теста:

1. **Arrange** - подготовка данных и моков
2. **Act** - выполнение тестируемого кода
3. **Assert** - проверка результатов

## 🚨 Отладка тестов

### Полезные команды:

```bash
# Запуск с отладочной информацией
pytest -v -s

# Запуск конкретного теста
pytest tests/test_cli_monitor.py::TestMonitorStatus::test_monitor_status_basic

# Запуск с остановкой на первой ошибке
pytest -x

# Запуск с максимальной детализацией
pytest -vvv --tb=long

# Запуск с профилированием
pytest --durations=10
```

### Отладка асинхронных тестов:

```python
@pytest.mark.asyncio
async def test_async_function():
    # Используйте await для асинхронных вызовов
    result = await async_function()
    assert result is not None
```

## 📝 Добавление новых тестов

### Шаблон для нового теста:

```python
"""
Tests for new feature
"""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from cli.new_feature import new_feature_app


class TestNewFeature:
    """Tests for new feature command"""

    @pytest.mark.new_feature
    @pytest.mark.cli
    def test_new_feature_basic(self, cli_runner: CliRunner):
        """Test basic new feature command"""
        with patch('cli.new_feature._new_feature_async') as mock_feature:
            mock_feature.return_value = None
            result = cli_runner.invoke(new_feature_app, ["command"])
            assert result.exit_code == 0

    @pytest.mark.new_feature
    @pytest.mark.unit
    def test_new_feature_helper_function(self):
        """Test helper function"""
        from cli.new_feature import helper_function
        result = helper_function("test")
        assert result == "expected_result"
```

### Добавление маркера:

1. Добавьте маркер в `pytest.ini`:
   ```ini
   markers =
       new_feature: New feature tests
   ```

2. Добавьте фикстуру в `conftest.py` если нужно:
   ```python
   @pytest.fixture
   def mock_new_feature_data():
       """Mock data for new feature tests"""
       return {"test": "data"}
   ```

## 🎉 Заключение

Эта система тестирования обеспечивает:

- ✅ **Полное покрытие CLI команд**
- ✅ **Модульные тесты для core функциональности**
- ✅ **Интеграционные тесты**
- ✅ **Отчеты о покрытии кода**
- ✅ **CI/CD готовность**
- ✅ **Качественную документацию**

Для получения дополнительной помощи используйте:
```bash
pytest --help
``` 