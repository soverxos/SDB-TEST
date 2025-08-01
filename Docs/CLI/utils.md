# 🛠️ Утилиты (utils)

## Обзор

Модуль `utils` предоставляет различные утилитарные инструменты для работы с SwiftDevBot, включая диагностику, очистку, проверку, конвертацию и другие вспомогательные функции.

## Основные команды

### `python sdb utils diagnose`

Выполняет полную диагностику системы.

**Опции:**
- `--system` - диагностика системы
- `--network` - диагностика сети
- `--database` - диагностика базы данных
- `--security` - диагностика безопасности
- `--detailed` - подробная диагностика

**Примеры:**

```bash
# Полная диагностика
python sdb utils diagnose

# Диагностика системы
python sdb utils diagnose --system

# Диагностика сети
python sdb utils diagnose --network

# Подробная диагностика
python sdb utils diagnose --detailed
```

**Результат:**
```
🔍 Диагностика SwiftDevBot-Lite...

📋 Системная диагностика:
   ✅ ОС: Linux 5.15.167.4-microsoft-standard-WSL2
   ✅ Python: 3.11.0
   ✅ Память: 8GB доступно
   ✅ Диск: 500GB свободно
   ✅ CPU: 4 ядра, 23% загрузка

📋 Сетевая диагностика:
   ✅ Интернет: Доступен
   ✅ Telegram API: Доступен
   ✅ Webhook: Настроен
   ✅ Порт 8000: Свободен

📋 База данных:
   ✅ SQLite: Подключена
   ✅ Таблицы: Все созданы
   ✅ Индексы: Оптимизированы
   ✅ Размер: 45.2MB
   ✅ Записей: 1,250

📋 Безопасность:
   ✅ Токены: Защищены
   ✅ SSL: Настроен
   ✅ Firewall: Активен
   ✅ Логирование: Включено

📊 Общий результат:
   🟢 Система работает нормально
   ⚠️ Рекомендации: 2
   📈 Оценка: 95/100
```

### `python sdb utils cleanup`

Очищает временные файлы и кэш.

**Опции:**
- `--temp` - очистить временные файлы
- `--cache` - очистить кэш
- `--logs` - очистить старые логи
- `--backups` - очистить старые бэкапы
- `--all` - полная очистка

**Примеры:**

```bash
# Очистить временные файлы
python sdb utils cleanup --temp

# Очистить кэш
python sdb utils cleanup --cache

# Очистить логи
python sdb utils cleanup --logs

# Полная очистка
python sdb utils cleanup --all
```

**Результат:**
```
🧹 Очистка SwiftDevBot-Lite...

📋 Временные файлы:
   ✅ Удалено файлов: 45
   ✅ Освобождено места: 12.3MB
   ✅ Очищено папок: 3

📋 Кэш:
   ✅ Очищен кэш модулей: 8
   ✅ Очищен кэш API: 15
   ✅ Очищен кэш изображений: 23
   ✅ Освобождено места: 8.7MB

📋 Логи:
   ✅ Удалено старых логов: 12
   ✅ Сжато логов: 5
   ✅ Освобождено места: 5.2MB

📋 Бэкапы:
   ✅ Удалено старых бэкапов: 3
   ✅ Освобождено места: 45.1MB

📊 Общий результат:
   ✅ Очистка завершена успешно
   📊 Освобождено места: 71.3MB
   📊 Удалено файлов: 83
   ⏱️ Время очистки: 2.1 секунды
```

### `python sdb utils check`

Проверяет целостность системы.

**Опции:**
- `--files` - проверить файлы
- `--database` - проверить базу данных
- `--config` - проверить конфигурацию
- `--permissions` - проверить права доступа
- `--all` - полная проверка

**Примеры:**

```bash
# Проверить файлы
python sdb utils check --files

# Проверить базу данных
python sdb utils check --database

# Проверить конфигурацию
python sdb utils check --config

# Полная проверка
python sdb utils check --all
```

**Результат:**
```
✅ Проверка целостности SwiftDevBot-Lite...

📋 Проверка файлов:
   ✅ Основные файлы: Целы
   ✅ Конфигурация: Корректна
   ✅ Модули: Все загружены
   ✅ Логи: Доступны для записи

📋 Проверка базы данных:
   ✅ Подключение: Успешно
   ✅ Таблицы: Все существуют
   ✅ Индексы: Оптимизированы
   ✅ Целостность: Проверена

📋 Проверка конфигурации:
   ✅ Основные настройки: Корректны
   ✅ Токены: Валидны
   ✅ Пути: Существуют
   ✅ Права доступа: Правильные

📋 Проверка прав доступа:
   ✅ Файлы: Чтение/запись
   ✅ Папки: Создание/удаление
   ✅ База данных: Полный доступ
   ✅ Логи: Запись

📊 Общий результат:
   🟢 Все проверки пройдены
   ✅ Целостность системы: 100%
   📈 Статус: Отлично
```

### `python sdb utils convert`

Конвертирует данные между форматами.

**Опции:**
- `--input FILE` - входной файл
- `--output FILE` - выходной файл
- `--format json/yaml/csv/xml` - формат
- `--encoding utf-8/utf-16` - кодировка

**Примеры:**

```bash
# Конвертировать JSON в YAML
python sdb utils convert --input data.json --output data.yaml

# Конвертировать CSV в JSON
python sdb utils convert --input users.csv --output users.json --format json

# Конвертировать с кодировкой
python sdb utils convert --input file.txt --output file_utf8.txt --encoding utf-8
```

**Результат:**
```
🔄 Конвертация файла 'data.json' в 'data.yaml'...

📋 Информация о файле:
   📊 Входной файл: data.json
   📊 Выходной файл: data.yaml
   📊 Формат: JSON → YAML
   📊 Размер: 2.3KB

📥 Процесс конвертации:
   ✅ Файл прочитан
   ✅ Данные распарсены
   ✅ Формат изменен
   ✅ Файл сохранен

📊 Результат конвертации:
   ✅ Конвертация завершена успешно
   📊 Размер выходного файла: 2.1KB
   📊 Сжатие: 8.7%
   ⏱️ Время конвертации: 0.3 секунды
```

### `python sdb utils encrypt`

Шифрует файлы и данные.

**Опции:**
- `--input FILE` - файл для шифрования
- `--output FILE` - выходной файл
- `--algorithm aes/des/rsa` - алгоритм шифрования
- `--password PASSWORD` - пароль

**Примеры:**

```bash
# Зашифровать файл
python sdb utils encrypt --input config.yaml --output config.enc

# Зашифровать с паролем
python sdb utils encrypt --input data.json --output data.enc --password secret123

# Зашифровать с алгоритмом
python sdb utils encrypt --input file.txt --output file.enc --algorithm aes
```

**Результат:**
```
🔒 Шифрование файла 'config.yaml'...

📋 Информация о файле:
   📊 Входной файл: config.yaml
   📊 Выходной файл: config.enc
   📊 Алгоритм: AES-256
   📊 Размер: 1.2KB

📥 Процесс шифрования:
   ✅ Файл прочитан
   ✅ Данные зашифрованы
   ✅ Ключ сгенерирован
   ✅ Файл сохранен

📊 Результат шифрования:
   ✅ Файл зашифрован успешно
   📊 Размер зашифрованного файла: 1.5KB
   📊 Увеличение размера: 25%
   🔑 Ключ сохранен в безопасном месте
```

### `python sdb utils decrypt`

Расшифровывает файлы.

**Опции:**
- `--input FILE` - зашифрованный файл
- `--output FILE` - выходной файл
- `--password PASSWORD` - пароль
- `--key-file FILE` - файл с ключом

**Примеры:**

```bash
# Расшифровать файл
python sdb utils decrypt --input config.enc --output config.yaml

# Расшифровать с паролем
python sdb utils decrypt --input data.enc --output data.json --password secret123

# Расшифровать с ключом
python sdb utils decrypt --input file.enc --output file.txt --key-file key.key
```

**Результат:**
```
🔓 Расшифрование файла 'config.enc'...

📋 Информация о файле:
   📊 Входной файл: config.enc
   📊 Выходной файл: config.yaml
   📊 Алгоритм: AES-256
   📊 Размер: 1.5KB

📥 Процесс расшифрования:
   ✅ Файл прочитан
   ✅ Ключ найден
   ✅ Данные расшифрованы
   ✅ Файл сохранен

📊 Результат расшифрования:
   ✅ Файл расшифрован успешно
   📊 Размер расшифрованного файла: 1.2KB
   📊 Сжатие: 20%
   ✅ Целостность проверена
```

## Расширенные команды (в разработке)

### `python sdb utils benchmark`

Выполняет бенчмарки системы.

**Опции:**
- `--cpu` - тест CPU
- `--memory` - тест памяти
- `--disk` - тест диска
- `--network` - тест сети
- `--output FILE` - файл для результатов

**Примеры:**

```bash
# Полный бенчмарк
python sdb utils benchmark

# Тест CPU
python sdb utils benchmark --cpu

# Тест памяти
python sdb utils benchmark --memory

# Сохранение результатов
python sdb utils benchmark --output benchmark_results.json
```

### `python sdb utils monitor`

Мониторит систему в реальном времени.

**Опции:**
- `--interval SECONDS` - интервал обновления
- `--cpu` - показывать только CPU
- `--memory` - показывать только память
- `--disk` - показывать только диск

**Примеры:**

```bash
# Мониторинг системы
python sdb utils monitor

# Мониторинг с интервалом 5 секунд
python sdb utils monitor --interval 5

# Мониторинг только CPU
python sdb utils monitor --cpu

# Мониторинг памяти
python sdb utils monitor --memory
```

### `python sdb utils backup`

Создает резервные копии.

**Опции:**
- `--type full/incremental` - тип бэкапа
- `--compress` - сжать бэкап
- `--encrypt` - зашифровать бэкап
- `--path PATH` - путь для сохранения

**Примеры:**

```bash
# Создать бэкап
python sdb utils backup

# Полный бэкап
python sdb utils backup --type full

# Сжатый бэкап
python sdb utils backup --compress

# Зашифрованный бэкап
python sdb utils backup --encrypt
```

### `python sdb utils restore`

Восстанавливает из бэкапа.

**Опции:**
- `BACKUP_FILE` - файл бэкапа
- `--force` - принудительное восстановление
- `--dry-run` - показать что будет восстановлено
- `--selective` - выборочное восстановление

**Примеры:**

```bash
# Восстановить из бэкапа
python sdb utils restore backup.zip

# Принудительное восстановление
python sdb utils restore backup.zip --force

# Показать что будет восстановлено
python sdb utils restore backup.zip --dry-run

# Выборочное восстановление
python sdb utils restore backup.zip --selective
```

### `python sdb utils optimize`

Оптимизирует систему.

**Опции:**
- `--database` - оптимизация базы данных
- `--files` - оптимизация файлов
- `--cache` - оптимизация кэша
- `--auto` - автоматическая оптимизация

**Примеры:**

```bash
# Автоматическая оптимизация
python sdb utils optimize --auto

# Оптимизация базы данных
python sdb utils optimize --database

# Оптимизация файлов
python sdb utils optimize --files

# Оптимизация кэша
python sdb utils optimize --cache
```

### `python sdb utils report`

Генерирует отчеты.

**Опции:**
- `--type system/usage/security` - тип отчета
- `--period DAYS` - период отчета
- `--format html/pdf/json` - формат отчета
- `--output FILE` - файл для сохранения

**Примеры:**

```bash
# Системный отчет
python sdb utils report --type system

# Отчет об использовании
python sdb utils report --type usage --period 30

# Отчет по безопасности
python sdb utils report --type security

# Отчет в HTML
python sdb utils report --type system --format html --output report.html
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb utils cleanup --all` - полная очистка может удалить важные данные
- `python sdb utils restore --force` - принудительное восстановление
- `python sdb utils decrypt` - расшифровка может сломать данные

### ⚠️ Опасные команды:
- `python sdb utils cleanup` - очистка файлов
- `python sdb utils convert` - конвертация может повредить данные
- `python sdb utils optimize --auto` - автоматическая оптимизация

### ✅ Безопасные команды:
- `python sdb utils diagnose` - только проверяет систему
- `python sdb utils check` - только проверяет целостность
- `python sdb utils monitor` - только мониторит
- `python sdb utils report` - только генерирует отчеты

## Устранение проблем

### Проблема: "Система работает медленно"
```bash
# Диагностика системы
python sdb utils diagnose

# Очистка временных файлов
python sdb utils cleanup --temp

# Оптимизация
python sdb utils optimize --auto

# Мониторинг
python sdb utils monitor
```

### Проблема: "Недостаточно места"
```bash
# Очистка системы
python sdb utils cleanup --all

# Проверка использования диска
python sdb utils diagnose --system

# Удаление старых бэкапов
python sdb utils cleanup --backups
```

### Проблема: "Ошибки в файлах"
```bash
# Проверка целостности
python sdb utils check --files

# Восстановление из бэкапа
python sdb utils restore backup.zip

# Конвертация файлов
python sdb utils convert --input broken.json --output fixed.json
```

## Рекомендации

1. **Регулярность**: Выполняйте диагностику регулярно
2. **Очистка**: Периодически очищайте временные файлы
3. **Бэкапы**: Создавайте резервные копии перед изменениями
4. **Мониторинг**: Следите за производительностью системы
5. **Безопасность**: Используйте шифрование для важных данных 