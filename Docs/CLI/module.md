# 📦 Управление модулями (module)

## Обзор

Модуль `module` предоставляет инструменты для управления плагинами и расширениями SwiftDevBot, включая установку, удаление, обновление, настройку и мониторинг модулей.

## Основные команды

### `python sdb module list`

Показывает список установленных модулей.

**Опции:**
- `--status active/inactive/all` - статус модулей
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON

**Примеры:**

```bash
# Показать все модули
python sdb module list

# Показать только активные модули
python sdb module list --status active

# Подробная информация
python sdb module list --detailed
```

**Результат:**
```
📦 Установленные модули SwiftDevBot-Lite

📱 Telegram модули:
   🟢 weather - Погода (v1.2.0)
      📊 Статус: Активен
      📊 Автор: @developer
      📊 Описание: Получение погоды по городу
      📊 Команды: /weather, /forecast

   🟢 translator - Переводчик (v2.1.0)
      📊 Статус: Активен
      📊 Автор: @translator_dev
      📊 Описание: Перевод текста между языками
      📊 Команды: /translate, /lang

   🔴 old_module - Старый модуль (v0.9.0)
      📊 Статус: Неактивен
      📊 Автор: @old_dev
      📊 Описание: Устаревший модуль
      📊 Команды: /old_command



📊 Общая статистика:
   🟢 Активных модулей: 3
   🔴 Неактивных модулей: 1
   📊 Всего модулей: 4
```

### `python sdb module install`

Устанавливает новый модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для установки
- `--source URL` - источник модуля
- `--version VERSION` - версия модуля
- `--force` - принудительная установка
- `--no-deps` - не устанавливать зависимости

**Примеры:**

```bash
# Установить модуль из репозитория
python sdb module install weather

# Установить конкретную версию
python sdb module install weather --version 1.2.0

# Установить из URL
python sdb module install custom_module --source https://github.com/user/module

# Принудительная установка
python sdb module install module_name --force
```

**Результат:**
```
📦 Установка модуля 'weather'...

📋 Информация о модуле:
   📊 Название: weather
   📊 Версия: 1.2.0
   📊 Автор: @developer
   📊 Размер: 2.3MB
   📊 Зависимости: 3 пакета

📥 Загрузка модуля...
   ✅ Файлы загружены
   ✅ Зависимости установлены
   ✅ Конфигурация создана
   ✅ Команды зарегистрированы

📊 Результат установки:
   ✅ Модуль установлен успешно
   📊 Добавлено команд: 2
   📊 Время установки: 15.2 секунды
   ⚠️ Требуется перезапуск бота для активации
```

### `python sdb module uninstall`

Удаляет модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для удаления
- `--force` - принудительное удаление
- `--keep-config` - сохранить конфигурацию
- `--backup` - создать бэкап перед удалением

**Примеры:**

```bash
# Удалить модуль
python sdb module uninstall old_module

# Принудительное удаление
python sdb module uninstall module_name --force

# Удалить с сохранением конфигурации
python sdb module uninstall module_name --keep-config

# Удалить с бэкапом
python sdb module uninstall module_name --backup
```

**Результат:**
```
🗑️ Удаление модуля 'old_module'...

📋 Информация о модуле:
   📊 Название: old_module
   📊 Версия: 0.9.0
   📊 Размер: 1.5MB
   📊 Команды: 3

📥 Процесс удаления:
   ✅ Модуль остановлен
   ✅ Команды удалены
   ✅ Файлы удалены
   ✅ Конфигурация очищена

📊 Результат удаления:
   ✅ Модуль удален успешно
   📊 Удалено команд: 3
   📊 Освобождено места: 1.5MB
   ⚠️ Требуется перезапуск бота
```

### `python sdb module update`

Обновляет модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для обновления
- `--version VERSION` - конкретная версия
- `--force` - принудительное обновление
- `--backup` - создать бэкап перед обновлением

**Примеры:**

```bash
# Обновить модуль
python sdb module update weather

# Обновить до конкретной версии
python sdb module update weather --version 1.3.0

# Принудительное обновление
python sdb module update module_name --force

# Обновление с бэкапом
python sdb module update module_name --backup
```

**Результат:**
```
🔄 Обновление модуля 'weather'...

📋 Информация об обновлении:
   📊 Текущая версия: 1.2.0
   📊 Новая версия: 1.3.0
   📊 Размер обновления: 500KB
   📊 Изменения: Исправления ошибок, новые функции

📥 Процесс обновления:
   ✅ Бэкап создан
   ✅ Старая версия удалена
   ✅ Новая версия установлена
   ✅ Конфигурация обновлена
   ✅ Команды перерегистрированы

📊 Результат обновления:
   ✅ Модуль обновлен успешно
   📊 Время обновления: 8.5 секунды
   ⚠️ Требуется перезапуск бота
```

### `python sdb module enable`

Включает модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для включения
- `--platform telegram` - платформа
- `--force` - принудительное включение

**Примеры:**

```bash
# Включить модуль
python sdb module enable weather

# Включить для конкретной платформы
python sdb module enable weather --platform telegram

# Принудительное включение
python sdb module enable module_name --force
```

**Результат:**
```
✅ Включение модуля 'weather'...

📋 Информация о модуле:
   📊 Название: weather
   📊 Версия: 1.2.0
   📊 Статус: Неактивен → Активен

📥 Процесс включения:
   ✅ Модуль загружен
   ✅ Команды зарегистрированы
   ✅ Конфигурация применена
   ✅ Проверка зависимостей

📊 Результат включения:
   ✅ Модуль включен успешно
   📊 Добавлено команд: 2
   📊 Статус: Активен
```

### `python sdb module disable`

Отключает модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для отключения
- `--platform telegram` - платформа
- `--keep-config` - сохранить конфигурацию

**Примеры:**

```bash
# Отключить модуль
python sdb module disable old_module

# Отключить для конкретной платформы
python sdb module disable module_name --platform telegram

# Отключить с сохранением конфигурации
python sdb module disable module_name --keep-config
```

**Результат:**
```
❌ Отключение модуля 'old_module'...

📋 Информация о модуле:
   📊 Название: old_module
   📊 Версия: 0.9.0
   📊 Статус: Активен → Неактивен

📥 Процесс отключения:
   ✅ Модуль остановлен
   ✅ Команды удалены
   ✅ Конфигурация сохранена
   ✅ Зависимости проверены

📊 Результат отключения:
   ✅ Модуль отключен успешно
   📊 Удалено команд: 3
   📊 Статус: Неактивен
```

### `python sdb module info`

Показывает информацию о модуле.

**Опции:**
- `MODULE_NAME` - имя модуля
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON

**Примеры:**

```bash
# Информация о модуле
python sdb module info weather

# Подробная информация
python sdb module info weather --detailed

# Информация в JSON
python sdb module info weather --json
```

**Результат:**
```
📦 Информация о модуле 'weather'

📋 Основная информация:
   📊 Название: weather
   📊 Версия: 1.2.0
   📊 Автор: @developer
   📊 Лицензия: MIT
   📊 Статус: Активен

📋 Описание:
   Модуль для получения информации о погоде.
   Поддерживает текущую погоду и прогноз на несколько дней.

📋 Команды:
   ✅ /weather [город] - Текущая погода
   ✅ /forecast [город] [дни] - Прогноз погоды

📋 Конфигурация:
   ✅ API ключ: Настроен
   ✅ Единицы измерения: Цельсий
   ✅ Язык: Русский

📋 Зависимости:
   ✅ requests (2.28.0)
   ✅ python-dateutil (2.8.2)

📋 Статистика:
   📊 Использований: 1,234
   📊 Ошибок: 0
   📊 Время работы: 15 дней
```

## Расширенные команды (в разработке)

### `python sdb module search`

Ищет модули в репозитории.

**Опции:**
- `QUERY` - поисковый запрос
- `--category CATEGORY` - категория модулей
- `--platform telegram` - платформа
- `--sort-by name/date/rating` - сортировка

**Примеры:**

```bash
# Поиск модулей
python sdb module search weather

# Поиск по категории
python sdb module search --category entertainment

# Поиск для Telegram
python sdb module search --platform telegram music

# Сортировка по рейтингу
python sdb module search weather --sort-by rating
```

### `python sdb module test`

Тестирует модуль.

**Опции:**
- `MODULE_NAME` - имя модуля для тестирования
- `--unit` - модульные тесты
- `--integration` - интеграционные тесты
- `--performance` - тесты производительности

**Примеры:**

```bash
# Тест модуля
python sdb module test weather

# Модульные тесты
python sdb module test weather --unit

# Интеграционные тесты
python sdb module test weather --integration

# Тесты производительности
python sdb module test weather --performance
```

### `python sdb module config`

Управляет конфигурацией модуля.

**Опции:**
- `MODULE_NAME` - имя модуля
- `--show` - показать конфигурацию
- `--set KEY=VALUE` - установить значение
- `--reset` - сбросить конфигурацию

**Примеры:**

```bash
# Показать конфигурацию
python sdb module config weather --show

# Установить значение
python sdb module config weather --set "api_key=YOUR_KEY"

# Сбросить конфигурацию
python sdb module config weather --reset
```

### `python sdb module logs`

Показывает логи модуля.

**Опции:**
- `MODULE_NAME` - имя модуля
- `--lines N` - количество строк
- `--level LEVEL` - уровень логирования
- `--follow` - следить за логами

**Примеры:**

```bash
# Логи модуля
python sdb module logs weather

# Последние 50 строк
python sdb module logs weather --lines 50

# Логи ошибок
python sdb module logs weather --level ERROR

# Следить за логами
python sdb module logs weather --follow
```

### `python sdb module backup`

Создает бэкап модуля.

**Опции:**
- `MODULE_NAME` - имя модуля
- `--include-data` - включить данные
- `--compress` - сжать бэкап
- `--path PATH` - путь для сохранения

**Примеры:**

```bash
# Бэкап модуля
python sdb module backup weather

# Бэкап с данными
python sdb module backup weather --include-data

# Сжатый бэкап
python sdb module backup weather --compress

# Бэкап в определенную папку
python sdb module backup weather --path /backup/
```

### `python sdb module restore`

Восстанавливает модуль из бэкапа.

**Опции:**
- `BACKUP_FILE` - файл бэкапа
- `--force` - принудительное восстановление
- `--overwrite` - перезаписать существующий модуль

**Примеры:**

```bash
# Восстановить модуль
python sdb module restore weather_backup.zip

# Принудительное восстановление
python sdb module restore backup_file --force

# Перезаписать модуль
python sdb module restore backup_file --overwrite
```

## Структура модуля

```
modules/
├── weather/
│   ├── __init__.py
│   ├── config.yaml
│   ├── commands.py
│   ├── handlers.py
│   ├── utils.py
│   ├── tests/
│   ├── docs/
│   └── requirements.txt
├── translator/
│   ├── __init__.py
│   ├── config.yaml
│   ├── commands.py
│   └── ...
└── music/
    ├── __init__.py
    ├── config.yaml
    ├── commands.py
    └── ...
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb module uninstall --force` - принудительное удаление
- `python sdb module install --force` - принудительная установка
- `python sdb module update --force` - принудительное обновление

### ⚠️ Опасные команды:
- `python sdb module disable` - отключение модуля
- `python sdb module config --reset` - сброс конфигурации
- `python sdb module restore --overwrite` - перезапись модуля

### ✅ Безопасные команды:
- `python sdb module list` - только показывает список
- `python sdb module info` - только показывает информацию
- `python sdb module search` - только ищет модули
- `python sdb module logs` - только показывает логи

## Устранение проблем

### Проблема: "Модуль не устанавливается"
```bash
# Проверить зависимости
python sdb module info module_name

# Принудительная установка
python sdb module install module_name --force

# Проверить логи
python sdb module logs module_name
```

### Проблема: "Модуль не работает"
```bash
# Проверить статус
python sdb module list --status active

# Перезапустить модуль
python sdb module disable module_name
python sdb module enable module_name

# Проверить конфигурацию
python sdb module config module_name --show
```

### Проблема: "Конфликт модулей"
```bash
# Список модулей
python sdb module list --detailed

# Отключить конфликтующий модуль
python sdb module disable conflicting_module

# Обновить модуль
python sdb module update module_name
```

## Рекомендации

1. **Тестирование**: Всегда тестируйте модули перед установкой
2. **Бэкапы**: Создавайте бэкапы перед обновлениями
3. **Зависимости**: Проверяйте совместимость зависимостей
4. **Конфигурация**: Настраивайте модули после установки
5. **Мониторинг**: Регулярно проверяйте логи модулей 