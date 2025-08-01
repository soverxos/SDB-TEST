# 🧪 Тестирование команд Monitor и Utils

Этот набор тестов предназначен для проверки всех команд `monitor` и `utils` в SwiftDevBot CLI.

## 📋 Содержание

- [Обзор](#обзор)
- [Файлы тестов](#файлы-тестов)
- [Быстрый старт](#быстрый-старт)
- [Безопасные команды](#безопасные-команды)
- [Опасные команды](#опасные-команды)
- [Детальное тестирование](#детальное-тестирование)
- [Интерпретация результатов](#интерпретация-результатов)

## 🎯 Обзор

Тесты проверяют все команды из вашего списка:

### 📊 Monitor команды:
- `status` - статус системы
- `metrics` - метрики производительности
- `alerts` - управление алертами
- `logs` - анализ логов
- `performance` - анализ производительности
- `report` - генерация отчетов
- `integrate` - интеграция с системами мониторинга

### 🛠️ Utils команды:
- `diagnose` - диагностика системы
- `check` - проверка целостности
- `cleanup` - очистка файлов
- `convert` - конвертация файлов
- `encrypt/decrypt` - шифрование/расшифровка

## 📁 Файлы тестов

### 1. `test_monitor_utils_commands.py` - Полный тест
- **Назначение**: Комплексное тестирование всех команд
- **Особенности**: 
  - Детальный отчет в JSON
  - Проверка всех опций команд
  - Создание и удаление тестовых файлов
  - Безопасное тестирование

### 2. `quick_test_commands.py` - Быстрый тест
- **Назначение**: Быстрое тестирование основных команд
- **Особенности**:
  - Показывает вывод каждой команды
  - Быстрая проверка функциональности
  - Интерактивный вывод результатов

## 🚀 Быстрый старт

### Предварительные требования:
```bash
# Убедитесь что вы в корне проекта SwiftDevBot
cd /path/to/SwiftDevBot-Lite

# Проверьте что виртуальное окружение существует
ls -la .venv/

# Активируйте виртуальное окружение
source .venv/bin/activate
```

### Запуск быстрого теста:
```bash
# Быстрый тест с выводом результатов
python quick_test_commands.py
```

### Запуск полного теста:
```bash
# Полный тест с детальным отчетом
python test_monitor_utils_commands.py
```

## ✅ Безопасные команды

Все тесты используют только безопасные команды:

### Monitor (БЕЗОПАСНЫЕ):
```bash
# Статус системы
source .venv/bin/activate && python sdb.py monitor status
source .venv/bin/activate && python sdb.py monitor status --detailed
source .venv/bin/activate && python sdb.py monitor status --json
source .venv/bin/activate && python sdb.py monitor status --health

# Метрики
source .venv/bin/activate && python sdb.py monitor metrics
source .venv/bin/activate && python sdb.py monitor metrics --cpu --memory
source .venv/bin/activate && python sdb.py monitor metrics --disk --network

# Алерты (только просмотр)
source .venv/bin/activate && python sdb.py monitor alerts --list
source .venv/bin/activate && python sdb.py monitor alerts --history

# Логи (только чтение)
source .venv/bin/activate && python sdb.py monitor logs --analyze
source .venv/bin/activate && python sdb.py monitor logs --errors
source .venv/bin/activate && python sdb.py monitor logs --last 10
source .venv/bin/activate && python sdb.py monitor logs --search error

# Производительность
source .venv/bin/activate && python sdb.py monitor performance
source .venv/bin/activate && python sdb.py monitor performance --slow-queries
source .venv/bin/activate && python sdb.py monitor performance --response-time
source .venv/bin/activate && python sdb.py monitor performance --memory-leaks

# Отчеты
source .venv/bin/activate && python sdb.py monitor report --daily
source .venv/bin/activate && python sdb.py monitor report --weekly --format html
source .venv/bin/activate && python sdb.py monitor report --monthly

# Интеграция
source .venv/bin/activate && python sdb.py monitor integrate --prometheus --grafana
source .venv/bin/activate && python sdb.py monitor integrate --datadog
source .venv/bin/activate && python sdb.py monitor integrate --newrelic
```

### Utils (БЕЗОПАСНЫЕ):
```bash
# Диагностика
source .venv/bin/activate && python sdb.py utils diagnose
source .venv/bin/activate && python sdb.py utils diagnose --system
source .venv/bin/activate && python sdb.py utils diagnose --network
source .venv/bin/activate && python sdb.py utils diagnose --database
source .venv/bin/activate && python sdb.py utils diagnose --security
source .venv/bin/activate && python sdb.py utils diagnose --detailed

# Проверка целостности
source .venv/bin/activate && python sdb.py utils check --files
source .venv/bin/activate && python sdb.py utils check --database
source .venv/bin/activate && python sdb.py utils check --config
source .venv/bin/activate && python sdb.py utils check --permissions
source .venv/bin/activate && python sdb.py utils check --all

# Безопасная очистка
source .venv/bin/activate && python sdb.py utils cleanup --temp
source .venv/bin/activate && python sdb.py utils cleanup --cache

# Конвертация (с тестовыми файлами)
source .venv/bin/activate && python sdb.py utils convert test.json test.yaml
source .venv/bin/activate && python sdb.py utils convert test.csv test.json --format json

# Шифрование (с тестовыми файлами)
source .venv/bin/activate && python sdb.py utils encrypt secret.txt secret.enc --password mypassword
source .venv/bin/activate && python sdb.py utils decrypt secret.enc decrypted.txt --password mypassword
```

## ⚠️ Опасные команды

Следующие команды НЕ тестируются автоматически, так как они могут быть опасными:

```bash
# ❌ ОПАСНО - удалит ВСЕ временные файлы
# source .venv/bin/activate && python sdb.py utils cleanup --all

# ❌ ОПАСНО - может удалить важные логи
# source .venv/bin/activate && python sdb.py utils cleanup --logs

# ❌ ОПАСНО - может удалить важные бэкапы
# source .venv/bin/activate && python sdb.py utils cleanup --backups

# ❌ ОПАСНО - может сломать данные при неправильном использовании
# source .venv/bin/activate && python sdb.py utils convert важный_файл.json output.yaml
```

## 🔍 Детальное тестирование

### Тестирование справки:
```bash
python quick_test_commands.py
# Проверяет все команды --help
```

### Тестирование monitor:
```bash
# Все команды monitor
python test_monitor_utils_commands.py
```

### Тестирование utils:
```bash
# Все команды utils
python test_monitor_utils_commands.py
```

### Тестирование конвертации:
```bash
# Создает тестовые файлы, конвертирует их, проверяет результат
python quick_test_commands.py
```

### Тестирование шифрования:
```bash
# Создает тестовый файл, шифрует, расшифровывает, сравнивает
python quick_test_commands.py
```

## 📊 Интерпретация результатов

### Успешный тест:
```
✅ Status Базовый статус: Команда выполнена успешно
✅ Metrics Базовые метрики: Команда выполнена успешно
✅ Diagnose Полная диагностика: Команда выполнена успешно
```

### Неудачный тест:
```
❌ Status Базовый статус: Команда завершилась с ошибкой
   Детали: ModuleNotFoundError: No module named 'core'
```

### Отчет о результатах:
```
📈 Общая статистика:
   Всего тестов: 45
   Успешных: 42
   Неудачных: 3
   Процент успеха: 93.3%
```

## 🎯 Рекомендации по безопасности

1. **Всегда делайте бэкап перед тестированием**
2. **Сначала запускайте команды с `--help` для понимания**
3. **Тестируйте на копиях файлов, не на оригиналах**
4. **Используйте `--detailed` для получения полной информации**
5. **Проверяйте что будет удалено перед очисткой**

## 🔧 Устранение проблем

### Проблема: "ModuleNotFoundError"
```bash
# Убедитесь что виртуальное окружение активировано
source .venv/bin/activate

# Проверьте что зависимости установлены
pip install -r requirements.txt
```

### Проблема: "Permission denied"
```bash
# Проверьте права доступа к файлам
chmod +x test_monitor_utils_commands.py
chmod +x quick_test_commands.py
```

### Проблема: "Timeout expired"
```bash
# Увеличьте таймаут в коде теста
timeout=60  # вместо 30
```

## 📄 Файлы отчетов

После выполнения полного теста создается файл:
- `test_monitor_utils_report.json` - Детальный отчет в JSON формате

## 🎉 Заключение

Эти тесты обеспечивают безопасную проверку всех команд monitor и utils в SwiftDevBot CLI. Они помогут убедиться, что все команды работают корректно без риска повреждения данных.

Для получения дополнительной помощи используйте:
```bash
source .venv/bin/activate && python sdb.py --help
``` 