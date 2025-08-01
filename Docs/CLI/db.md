# 🗄️ Управление базой данных (db)

## Обзор

Модуль `db` предоставляет команды для управления базой данных SwiftDevBot, включая миграции Alembic, оптимизацию и обслуживание.

## Основные команды

### `python sdb db upgrade`

Применяет миграции Alembic до указанной версии.

**Опции:**
- `revision` - ID ревизии для обновления (по умолчанию: head)

**Примеры:**

```bash
# Обновить до последней версии
python sdb db upgrade

# Обновить до конкретной ревизии
python sdb db upgrade abc123def456

# Обновить на одну версию вперед
python sdb db upgrade +1

# Обновить до базовой версии
python sdb db upgrade base
```

**Результат:**
```
🔄 Применение миграций Alembic до ревизии: head

📋 Миграции для применения:
   ✅ 001_initial_schema.py
   ✅ 002_add_user_roles.py
   ✅ 003_add_permissions.py
   ✅ 004_add_module_support.py

✅ Миграции успешно применены!
📊 Обновлено таблиц: 8
⏱️ Время выполнения: 2.1 секунды
```

### `python sdb db downgrade`

Откатывает миграции Alembic.

**Опции:**
- `revision` - ID ревизии для отката (по умолчанию: 1)

**Примеры:**

```bash
# Откатиться на одну версию назад
python sdb db downgrade

# Откатиться на две версии назад
python sdb db downgrade 2

# Откатиться до конкретной ревизии
python sdb db downgrade abc123def456

# Откатиться до базовой версии
python sdb db downgrade base
```

**Результат:**
```
⚠️ Откат миграций Alembic до ревизии: 1

📋 Миграции для отката:
   ❌ 004_add_module_support.py
   ❌ 003_add_permissions.py

⚠️ ВНИМАНИЕ: Это может привести к потере данных!

❓ Вы уверены, что хотите откатиться? [y/N]: y

✅ Откат успешно выполнен!
📊 Откачено таблиц: 2
⏱️ Время выполнения: 1.5 секунды
```

### `python sdb db revision`

Создает новый файл миграции Alembic.

**Опции:**
- `-m, --message` - описание изменений (обязательно)
- `--autogenerate/--no-autogenerate` - автоматическое определение изменений

**Примеры:**

```bash
# Создать миграцию с автоматическим определением изменений
python sdb db revision -m "Add user preferences table"

# Создать пустую миграцию
python sdb db revision -m "Custom migration" --no-autogenerate
```

**Результат:**
```
📝 Создание новой ревизии Alembic с сообщением: 'Add user preferences table'

🔍 Автоматическое определение изменений...
   ✅ Найдены изменения в моделях
   ✅ Создан SQL для новых таблиц
   ✅ Создан SQL для изменений в существующих таблицах

📄 Файл миграции создан: alembic_migrations/versions/005_add_user_preferences.py
📋 Содержимое:
   - Создание таблицы user_preferences
   - Добавление индексов
   - Добавление внешних ключей
```

### `python sdb db status`

Показывает текущий статус миграций.

**Опции:**
- `--verbose, -v` - показать подробную информацию

**Примеры:**

```bash
# Показать текущий статус
python sdb db status

# Показать подробную информацию
python sdb db status --verbose
```

**Результат:**
```
📊 Текущий статус миграций Alembic:

🟢 Текущая ревизия: 004_add_module_support (head)
📅 Применена: 2024-01-15 14:30:22
📋 Всего миграций: 4

📋 История миграций:
   ✅ 001_initial_schema (2024-01-15 10:00:00)
   ✅ 002_add_user_roles (2024-01-15 10:15:00)
   ✅ 003_add_permissions (2024-01-15 10:30:00)
   ✅ 004_add_module_support (2024-01-15 14:30:22)

📊 Статистика:
   📁 Применено миграций: 4/4
   📊 Размер БД: 2.1MB
   📈 Записи: 1,250
```

### `python sdb db init-core`

**⚠️ ОПАСНО!** Создает таблицы ядра напрямую, минуя Alembic.

**Примеры:**

```bash
# Создать таблицы ядра
python sdb db init-core
```

**Результат:**
```
⚠️ Инициализация таблиц ядра SDB и стандартных ролей напрямую

⚠️ ПРЕДУПРЕЖДЕНИЕ: Эта команда создаст таблицы ядра и роли напрямую, игнорируя Alembic.

❓ Вы уверены, что хотите создать таблицы ядра и стандартные роли напрямую? [y/N]: y

🗄️ Используется БД: sqlite (URL строится на основе настроек)

📋 Создание таблиц ядра...
   ✅ Таблица: sdb_users
   ✅ Таблица: sdb_roles
   ✅ Таблица: sdb_permissions
   ✅ Таблица: sdb_user_roles
   ✅ Таблица: sdb_role_permissions
   ✅ Таблица: sdb_user_permissions

📋 Создание стандартных ролей...
   ✅ Роль: admin
   ✅ Роль: user
   ✅ Роль: guest

✅ Команда 'db init-core' успешно завершена!
```

### `python sdb db stamp`

Устанавливает текущую ревизию Alembic в БД без применения миграций.

**Опции:**
- `revision` - ID ревизии для установки
- `--purge` - очистить таблицу версий перед установкой

**Примеры:**

```bash
# Установить текущую ревизию
python sdb db stamp head

# Установить конкретную ревизию
python sdb db stamp abc123def456

# Очистить таблицу версий и установить ревизию
python sdb db stamp head --purge
```

## Расширенные команды (в разработке)

### `python sdb db optimize`

Оптимизирует структуру базы данных для улучшения производительности.

**Опции:**
- `--rebuild-indexes` - перестроить все индексы
- `--update-stats` - обновить статистику
- `--vacuum` - выполнить VACUUM после оптимизации

**Примеры:**

```bash
# Полная оптимизация
python sdb db optimize

# Оптимизация с перестройкой индексов
python sdb db optimize --rebuild-indexes

# Оптимизация с обновлением статистики
python sdb db optimize --update-stats
```

### `python sdb db vacuum`

Освобождает неиспользуемое пространство в базе данных.

**Опции:**
- `--aggressive` - агрессивная очистка
- `--analyze` - обновить статистику после VACUUM

**Примеры:**

```bash
# Обычный VACUUM
python sdb db vacuum

# Агрессивный VACUUM
python sdb db vacuum --aggressive

# VACUUM с обновлением статистики
python sdb db vacuum --analyze
```

### `python sdb db analyze`

Собирает статистику для оптимизатора запросов.

**Опции:**
- `--full` - полный анализ всех таблиц
- `--table TABLE` - анализ конкретной таблицы

**Примеры:**

```bash
# Анализ всех таблиц
python sdb db analyze

# Анализ конкретной таблицы
python sdb db analyze --table users

# Полный анализ
python sdb db analyze --full
```

### `python sdb db size`

Показывает размер базы данных и отдельных таблиц.

**Опции:**
- `--human-readable` - размер в читаемом формате
- `--detailed` - подробная информация

**Примеры:**

```bash
# Показать размер БД
python sdb db size

# Размер в читаемом формате
python sdb db size --human-readable

# Подробная информация
python sdb db size --detailed
```

### `python sdb db tables`

Выводит список всех таблиц с информацией о них.

**Опции:**
- `--list` - подробная информация о структуре
- `--stats` - статистика по таблицам

**Примеры:**

```bash
# Показать все таблицы
python sdb db tables

# Подробная информация
python sdb db tables --list

# Статистика по таблицам
python sdb db tables --stats
```

### `python sdb db export`

Экспортирует данные из базы в различные форматы.

**Опции:**
- `--format json/csv` - формат экспорта
- `--table TABLE_NAME` - экспорт конкретной таблицы
- `--output FILE` - файл для сохранения

**Примеры:**

```bash
# Экспорт всех данных в JSON
python sdb db export --format json

# Экспорт конкретной таблицы в CSV
python sdb db export --format csv --table users

# Экспорт в файл
python sdb db export --format json --output data_export.json
```

### `python sdb db import`

Импортирует данные из файла в базу данных.

**Опции:**
- `--file FILE` - путь к файлу для импорта
- `--format json/csv` - формат файла
- `--table TABLE_NAME` - целевая таблица

**Примеры:**

```bash
# Импорт из JSON файла
python sdb db import --file data_export.json

# Импорт в конкретную таблицу
python sdb db import --file users.csv --table users

# Импорт с указанием формата
python sdb db import --file data.csv --format csv
```

### `python sdb db health-check`

Проверяет здоровье базы данных.

**Опции:**
- `--full` - полная проверка
- `--fix` - автоматическое исправление проблем

**Примеры:**

```bash
# Базовая проверка здоровья
python sdb db health-check

# Полная проверка
python sdb db health-check --full

# Проверка с автоматическим исправлением
python sdb db health-check --fix
```

### `python sdb db maintenance`

Автоматическое обслуживание БД.

**Опции:**
- `--auto` - автоматический режим
- `--schedule` - настроить расписание

**Примеры:**

```bash
# Автоматическое обслуживание
python sdb db maintenance --auto

# Настроить расписание обслуживания
python sdb db maintenance --schedule
```

## Структура миграций

```
alembic_migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_user_roles.py
│   ├── 003_add_permissions.py
│   └── 004_add_module_support.py
├── env.py
└── script.py.mako
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb db downgrade base` - удалит все данные
- `python sdb db init-core --force` - перезапишет таблицы
- `python sdb db stamp --purge` - удалит историю миграций

### ⚠️ Опасные команды:
- `python sdb db downgrade` - откат миграций
- `python sdb db vacuum --aggressive` - может заблокировать БД
- `python sdb db optimize --rebuild` - долгая операция

### ✅ Безопасные команды:
- `python sdb db status` - только показывает статус
- `python sdb db upgrade` - добавляет, не удаляет
- `python sdb db size` - только читает размеры
- `python sdb db tables` - только показывает таблицы

## Рекомендации

1. **Регулярные бэкапы**: Всегда делайте бэкап перед миграциями
2. **Тестирование**: Тестируйте миграции на копии данных
3. **Постепенные изменения**: Применяйте миграции по одной
4. **Мониторинг**: Следите за производительностью после изменений
5. **Документация**: Документируйте все изменения в миграциях

## Устранение проблем

### Проблема: "Миграция не применяется"
```bash
# Проверить статус
python sdb db status

# Проверить логи Alembic
python sdb db upgrade --verbose

# Откатиться и попробовать снова
python sdb db downgrade 1
python sdb db upgrade
```

### Проблема: "Конфликт миграций"
```bash
# Показать историю миграций
python sdb db status --verbose

# Создать новую миграцию для разрешения конфликта
python sdb db revision -m "Resolve migration conflict"
```

### Проблема: "Ошибка подключения к БД"
```bash
# Проверить настройки БД
python sdb config show

# Проверить доступность БД
python sdb db health-check
```

## Типы баз данных

### SQLite
- **Файл**: `Database_files/swiftdevbot.db`
- **Преимущества**: Простота, встроенная поддержка
- **Недостатки**: Ограниченная производительность при больших нагрузках

### PostgreSQL
- **DSN**: `postgresql://user:pass@localhost/dbname`
- **Преимущества**: Высокая производительность, расширенные возможности
- **Недостатки**: Требует отдельного сервера

### MySQL
- **DSN**: `mysql://user:pass@localhost/dbname`
- **Преимущества**: Хорошая производительность, широкое распространение
- **Недостатки**: Ограниченная поддержка некоторых функций SQLAlchemy 