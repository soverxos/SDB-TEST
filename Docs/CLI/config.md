# ⚙️ Управление конфигурацией (config)

## Обзор

Модуль `config` предоставляет инструменты для управления всеми настройками SwiftDevBot, включая конфигурационные файлы, переменные окружения, настройки ботов, базы данных и системы.

## Основные команды

### `python sdb config show`

Показывает текущую конфигурацию системы.

**Опции:**
- `--section SECTION` - показать конкретную секцию
- `--format json/yaml/toml` - формат вывода
- `--show-secrets` - показать секретные значения
- `--diff` - показать отличия от значений по умолчанию

**Примеры:**

```bash
# Показать всю конфигурацию
python sdb config show

# Показать только настройки бота
python sdb config show --section bot

# Показать в формате JSON
python sdb config show --format json

# Показать с секретами
python sdb config show --show-secrets

# Показать отличия от значений по умолчанию
python sdb config show --diff
```

**Результат:**
```
⚙️ Конфигурация SwiftDevBot-Lite

📱 Telegram Bot:
   ✅ Токен: ***hidden***
   ✅ Webhook URL: https://example.com/webhook
   ✅ Команды: 15 активных
   ✅ Плагины: 8 загружено
   ✅ Логирование: INFO

🗄️ База данных:
   ✅ Тип: SQLite
   ✅ Путь: /root/SDB/SwiftDevBot-Lite/data/swiftdevbot.db
   ✅ Размер: 45.2MB
   ✅ Записей: 1,250

🔧 Система:
   ✅ Режим: production
   ✅ Язык: ru
   ✅ Временная зона: UTC
   ✅ Логирование: INFO
   ✅ Отладка: False
```

### `python sdb config set`

Устанавливает значение конфигурации.

**Опции:**
- `KEY=VALUE` - ключ и значение для установки
- `--section SECTION` - секция конфигурации
- `--type TYPE` - тип значения (string/int/bool)
- `--validate` - проверить значение перед установкой

**Примеры:**

```bash
# Установить значение
python sdb config set "bot.telegram.token=YOUR_TOKEN"

# Установить в секции
python sdb config set --section database "url=sqlite:///new.db"

# Установить с типом
python sdb config set --type int "system.max_connections=100"

# Установить с проверкой
python sdb config set --validate "bot.telegram.webhook_url=https://example.com/webhook"
```

**Результат:**
```
✅ Конфигурация обновлена

📋 Изменения:
   🔧 bot.telegram.token: Обновлено
   🔧 bot.telegram.webhook_url: Установлено
   🔧 system.log_level: Изменено на INFO

📊 Результат:
   ✅ Все значения установлены успешно
   ✅ Конфигурация сохранена
   ⚠️ Требуется перезапуск для применения изменений
```

### `python sdb config get`

Получает значение конфигурации.

**Опции:**
- `KEY` - ключ для получения
- `--section SECTION` - секция конфигурации
- `--default VALUE` - значение по умолчанию
- `--format json/yaml` - формат вывода

**Примеры:**

```bash
# Получить значение
python sdb config get "bot.telegram.token"

# Получить из секции
python sdb config get --section database "url"

# Получить с значением по умолчанию
python sdb config get "unknown.key" --default "default_value"

# Получить в формате JSON
python sdb config get "bot" --format json
```

**Результат:**
```
📋 Значение конфигурации

🔑 Ключ: bot.telegram.token
📊 Значение: ***hidden***
📁 Тип: string
📅 Обновлено: 2024-01-15 14:30:22
```

### `python sdb config reset`

Сбрасывает конфигурацию к значениям по умолчанию.

**Опции:**
- `--section SECTION` - сбросить конкретную секцию
- `--backup` - создать бэкап перед сбросом
- `--force` - принудительный сброс
- `--dry-run` - показать что будет сброшено

**Примеры:**

```bash
# Сбросить всю конфигурацию
python sdb config reset

# Сбросить секцию бота
python sdb config reset --section bot

# Сброс с бэкапом
python sdb config reset --backup

# Показать что будет сброшено
python sdb config reset --dry-run
```

**Результат:**
```
🔄 Сброс конфигурации SwiftDevBot-Lite

📋 Что будет сброшено:
   🔧 bot.telegram.token: Сброшено к значению по умолчанию
   🔧 system.log_level: Сброшено к INFO
   🔧 database.url: Сброшено к sqlite:///swiftdevbot.db

⚠️ ВНИМАНИЕ: Это действие нельзя отменить!
❓ Вы уверены, что хотите сбросить конфигурацию? [y/N]: y

✅ Конфигурация сброшена успешно!
📊 Сброшено: 15 параметров
📁 Бэкап сохранен: config_backup_20240115_143022.yaml
```

### `python sdb config export`

Экспортирует конфигурацию в файл.

**Опции:**
- `--format yaml/json/toml/env` - формат экспорта
- `--file FILE` - имя файла
- `--include-secrets` - включить секретные значения
- `--template` - экспорт как шаблон

**Примеры:**

```bash
# Экспорт в YAML
python sdb config export --format yaml

# Экспорт в JSON
python sdb config export --format json --file config.json

# Экспорт с секретами
python sdb config export --include-secrets

# Экспорт как шаблон
python sdb config export --template
```

**Результат:**
```
📤 Экспорт конфигурации

📁 Файл: config_export_20240115_143022.yaml
📊 Формат: YAML
📊 Размер: 2.3KB
📊 Параметров: 45

✅ Конфигурация экспортирована успешно!
📋 Путь: /root/SDB/SwiftDevBot-Lite/config_export_20240115_143022.yaml
```

### `python sdb config import`

Импортирует конфигурацию из файла.

**Опции:**
- `FILE` - файл для импорта
- `--format yaml/json/toml/env` - формат файла
- `--backup` - создать бэкап перед импортом
- `--validate` - проверить конфигурацию перед импортом
- `--merge` - объединить с существующей конфигурацией

**Примеры:**

```bash
# Импорт из YAML файла
python sdb config import config.yaml

# Импорт с бэкапом
python sdb config import config.yaml --backup

# Импорт с проверкой
python sdb config import config.yaml --validate

# Объединение конфигураций
python sdb config import config.yaml --merge
```

**Результат:**
```
📥 Импорт конфигурации

📁 Файл: config.yaml
📊 Формат: YAML
📊 Размер: 2.1KB

📋 Импортированные параметры:
   ✅ bot.telegram.token: Импортировано
   ✅ system.log_level: Импортировано
   ✅ database.url: Импортировано

✅ Конфигурация импортирована успешно!
📊 Импортировано: 15 параметров
📁 Бэкап сохранен: config_backup_20240115_143022.yaml
```

## Расширенные команды (в разработке)

### `python sdb config validate`

Проверяет корректность конфигурации.

**Опции:**
- `--fix` - автоматически исправить ошибки
- `--strict` - строгая проверка
- `--section SECTION` - проверить конкретную секцию

**Примеры:**

```bash
# Проверить всю конфигурацию
python sdb config validate

# Проверить с исправлением
python sdb config validate --fix

# Строгая проверка
python sdb config validate --strict

# Проверить секцию бота
python sdb config validate --section bot
```

### `python sdb config diff`

Показывает различия между конфигурациями.

**Опции:**
- `FILE1` - первый файл конфигурации
- `FILE2` - второй файл конфигурации
- `--format unified/context` - формат вывода
- `--ignore-whitespace` - игнорировать пробелы

**Примеры:**

```bash
# Сравнить с файлом
python sdb config diff config_old.yaml config_new.yaml

# Сравнить с текущей конфигурацией
python sdb config diff config.yaml

# Сравнить в формате unified
python sdb config diff --format unified config1.yaml config2.yaml
```

### `python sdb config migrate`

Мигрирует конфигурацию между версиями.

**Опции:**
- `--from-version VERSION` - исходная версия
- `--to-version VERSION` - целевая версия
- `--backup` - создать бэкап
- `--dry-run` - показать изменения без применения

**Примеры:**

```bash
# Миграция конфигурации
python sdb config migrate --from-version 1.0 --to-version 2.0

# Миграция с бэкапом
python sdb config migrate --backup

# Показать изменения
python sdb config migrate --dry-run
```

### `python sdb config template`

Создает шаблон конфигурации.

**Опции:**
- `--format yaml/json/toml/env` - формат шаблона
- `--include-examples` - включить примеры
- `--output FILE` - файл для сохранения

**Примеры:**

```bash
# Создать шаблон YAML
python sdb config template --format yaml

# Создать шаблон с примерами
python sdb config template --include-examples

# Сохранить в файл
python sdb config template --output config_template.yaml
```

### `python sdb config backup`

Создает бэкап конфигурации.

**Опции:**
- `--name NAME` - имя бэкапа
- `--compress` - сжать бэкап
- `--encrypt` - зашифровать бэкап
- `--path PATH` - путь для сохранения

**Примеры:**

```bash
# Создать бэкап
python sdb config backup

# Создать бэкап с именем
python sdb config backup --name "before_update"

# Создать сжатый бэкап
python sdb config backup --compress

# Создать зашифрованный бэкап
python sdb config backup --encrypt
```

### `python sdb config restore`

Восстанавливает конфигурацию из бэкапа.

**Опции:**
- `BACKUP_NAME` - имя бэкапа
- `--force` - принудительное восстановление
- `--dry-run` - показать что будет восстановлено

**Примеры:**

```bash
# Восстановить из бэкапа
python sdb config restore config_backup_20240115_143022.yaml

# Принудительное восстановление
python sdb config restore backup_name --force

# Показать что будет восстановлено
python sdb config restore backup_name --dry-run
```

## Структура конфигурации

```yaml
# Основные настройки бота
bot:
  telegram:
    token: "YOUR_TELEGRAM_TOKEN"
    webhook_url: "https://example.com/webhook"
    commands: 15
    plugins: 8
    log_level: "INFO"

# Настройки базы данных
database:
  type: "sqlite"
  url: "sqlite:///swiftdevbot.db"
  pool_size: 10
  max_overflow: 20
  echo: false

# Системные настройки
system:
  mode: "production"
  language: "ru"
  timezone: "UTC"
  log_level: "INFO"
  debug: false
  max_connections: 100
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb config reset` - сброс всей конфигурации
- `python sdb config import --force` - перезапись конфигурации
- `python sdb config set "bot.telegram.token=WRONG_TOKEN"` - неправильный токен

### ⚠️ Опасные команды:
- `python sdb config export --include-secrets` - экспорт секретов
- `python sdb config import` - импорт может перезаписать настройки
- `python sdb config set` - изменение критических параметров

### ✅ Безопасные команды:
- `python sdb config show` - только показывает конфигурацию
- `python sdb config get` - только получает значения
- `python sdb config validate` - только проверяет
- `python sdb config template` - только создает шаблон

## Устранение проблем

### Проблема: "Конфигурация повреждена"
```bash
# Проверить конфигурацию
python sdb config validate

# Восстановить из бэкапа
python sdb config restore config_backup.yaml

# Сбросить к значениям по умолчанию
python sdb config reset
```

### Проблема: "Неверный токен"
```bash
# Проверить токен
python sdb config get "bot.telegram.token"

# Установить правильный токен
python sdb config set "bot.telegram.token=YOUR_TOKEN"

# Перезапустить бота
python sdb bot restart
```

### Проблема: "Файл конфигурации не найден"
```bash
# Создать шаблон
python sdb config template --output config.yaml

# Импортировать шаблон
python sdb config import config.yaml

# Проверить структуру
python sdb config show
```

## Рекомендации

1. **Бэкапы**: Регулярно создавайте бэкапы конфигурации
2. **Валидация**: Всегда проверяйте конфигурацию перед применением
3. **Секреты**: Храните токены в безопасном месте
4. **Версионирование**: Используйте систему контроля версий для конфигурации
5. **Документация**: Документируйте изменения конфигурации 