# ⚙️ Системные настройки (system)

## Обзор

Модуль `system` предоставляет инструменты для управления системными настройками SwiftDevBot, включая переменные окружения, сервисы, логи и диагностику системы.

## Основные команды

### `python sdb system status`

Показывает общий статус системы и всех компонентов.

**Опции:**
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON
- `--health` - только проверка здоровья

**Примеры:**

```bash
# Показать общий статус
python sdb system status

# Подробная информация
python sdb system status --detailed

# Только проверка здоровья
python sdb system status --health
```

**Результат:**
```
⚙️ Статус системы SwiftDevBot-Lite

🖥️ Системная информация:
   📊 ОС: Linux 5.15.167.4-microsoft-standard-WSL2
   📊 Python: 3.11.0
   📊 Версия SDB: 1.0.0
   📊 Uptime: 15 дней 8 часов 32 минуты

🔧 Компоненты системы:
   ✅ Bot API: Работает (PID: 1234)
   ✅ Database: Подключена (SQLite)
   ✅ Cache: Активен (Redis)
   ✅ Web Server: Работает (порт 8000)

📊 Ресурсы:
   🖥️ CPU: 23% (4 ядра)
   💾 Memory: 1.2GB / 8GB (15%)
   💿 Disk: 45GB / 500GB (9%)
   🌐 Network: Активен

🔗 Сетевые порты:
   ✅ 8000: Web API
   ✅ 8001: WebSocket
   ✅ 5432: PostgreSQL (не используется)
   ✅ 6379: Redis

📊 Статистика:
   🟢 Все системы работают нормально
   📈 Uptime: 99.8%
   🔧 Последний перезапуск: 15 дней назад
```

### `python sdb system env list`

Показывает все переменные окружения системы.

**Опции:**
- `--show-secrets` - показать секретные значения
- `--json` - вывод в формате JSON
- `--filter PATTERN` - фильтр по паттерну

**Примеры:**

```bash
# Показать все переменные
python sdb system env list

# Показать с секретами
python sdb system env list --show-secrets

# Фильтр по паттерну
python sdb system env list --filter "DB_"
```

**Результат:**
```
🔧 Переменные окружения системы

📋 Основные настройки:
   ✅ DATABASE_URL=***hidden***
   ✅ API_KEY=***hidden***
   ✅ DEBUG=True
   ✅ LOG_LEVEL=INFO
   ✅ TIMEZONE=UTC

📋 Настройки бота:
   ✅ TELEGRAM_TOKEN=***hidden***
   ✅ WEBHOOK_URL=https://example.com/webhook

📋 Настройки базы данных:
   ✅ DB_HOST=localhost
   ✅ DB_PORT=5432
   ✅ DB_NAME=swiftdevbot
   ✅ DB_USER=***hidden***

📋 Настройки кэша:
   ✅ REDIS_URL=redis://localhost:6379
   ✅ CACHE_TTL=3600

📊 Статистика:
   📋 Всего переменных: 25
   🔒 Секретных переменных: 8
   ✅ Все переменные корректно настроены
```

### `python sdb system env set KEY=VALUE`

Устанавливает переменную окружения.

**Опции:**
- `--persistent` - сохранить в файл конфигурации
- `--temporary` - установить только для текущей сессии
- `--validate` - проверить корректность значения

**Примеры:**

```bash
# Установить переменную
python sdb system env set DEBUG=True

# Установить с сохранением
python sdb system env set DATABASE_URL=sqlite:///new.db --persistent

# Установить с проверкой
python sdb system env set LOG_LEVEL=DEBUG --validate
```

**Результат:**
```
🔧 Установка переменной окружения

✅ Переменная установлена: DEBUG=True
📋 Тип: Временная (только для текущей сессии)
🔍 Валидация: Успешно
📊 Влияние: Включен режим отладки

📋 Рекомендации:
   ⚠️ Для постоянного сохранения используйте --persistent
   ⚠️ Переменная будет сброшена после перезапуска
   ✅ Значение корректно и готово к использованию
```

### `python sdb system env unset KEY`

Удаляет переменную окружения.

**Опции:**
- `--persistent` - удалить из файла конфигурации
- `--all` - удалить все переменные (ОПАСНО!)

**Примеры:**

```bash
# Удалить переменную
python sdb system env unset OLD_API_KEY

# Удалить с сохранением
python sdb system env unset DEBUG --persistent

# Удалить все переменные (ОПАСНО!)
python sdb system env unset --all
```

**Результат:**
```
🔧 Удаление переменной окружения

✅ Переменная удалена: OLD_API_KEY
📋 Тип: Временная (только для текущей сессии)
🔍 Проверка: Переменная больше не доступна

📋 Рекомендации:
   ⚠️ Для постоянного удаления используйте --persistent
   ⚠️ Убедитесь, что переменная не используется в коде
   ✅ Удаление выполнено успешно
```

### `python sdb system service start/stop/restart/status`

Управляет системными сервисами SwiftDevBot.

**Опции:**
- `start` - запустить сервис
- `stop` - остановить сервис
- `restart` - перезапустить сервис
- `status` - показать статус сервиса
- `--all` - применить ко всем сервисам

**Примеры:**

```bash
# Показать статус всех сервисов
python sdb system service status

# Запустить все сервисы
python sdb system service start --all

# Остановить конкретный сервис
python sdb system service stop bot_api

# Перезапустить сервис
python sdb system service restart database
```

**Результат:**
```
🔧 Управление системными сервисами

📋 Статус сервисов:
   ✅ Bot API: Работает (PID: 1234)
   ✅ Database: Работает (PID: 1235)
   ✅ Cache: Работает (PID: 1236)
   ✅ Web Server: Работает (PID: 1237)

📊 Операции:
   🔄 Перезапуск сервиса: database
   ⏱️ Время выполнения: 2.3 секунды
   ✅ Сервис успешно перезапущен

📋 Новый статус:
   ✅ Bot API: Работает (PID: 1234)
   ✅ Database: Работает (PID: 1240) - перезапущен
   ✅ Cache: Работает (PID: 1236)
   ✅ Web Server: Работает (PID: 1237)

📊 Статистика:
   🟢 Все сервисы работают нормально
   📈 Uptime: 99.8%
   🔧 Последний перезапуск: 2 минуты назад
```

### `python sdb system logs --tail --follow`

Показывает логи системы.

**Опции:**
- `--tail N` - последние N строк
- `--follow` - следить за новыми записями
- `--level DEBUG/INFO/WARNING/ERROR` - уровень логирования
- `--service SERVICE` - логи конкретного сервиса
- `--since TIME` - логи с определенного времени

**Примеры:**

```bash
# Показать последние 50 строк
python sdb system logs --tail 50

# Следить за логами в реальном времени
python sdb system logs --follow

# Показать только ошибки
python sdb system logs --level ERROR

# Логи конкретного сервиса
python sdb system logs --service bot_api
```

**Результат:**
```
📋 Логи системы SwiftDevBot-Lite

📊 Последние 50 записей:

[2024-01-15 14:30:15] INFO - Bot API: Запрос получен от пользователя 12345
[2024-01-15 14:30:16] INFO - Database: Выполнен запрос SELECT * FROM users
[2024-01-15 14:30:17] INFO - Cache: Кэш обновлен для ключа user:12345
[2024-01-15 14:30:18] INFO - Bot API: Ответ отправлен пользователю 12345
[2024-01-15 14:30:19] WARNING - Database: Медленный запрос (1.2 сек)
[2024-01-15 14:30:20] ERROR - Cache: Ошибка подключения к Redis
[2024-01-15 14:30:21] INFO - Cache: Подключение восстановлено
[2024-01-15 14:30:22] INFO - Web Server: Новое подключение с IP 192.168.1.100

📊 Статистика логов:
   📝 Всего записей: 15,420
   🟢 INFO: 15,363
   ⚠️ WARNING: 45
   ❌ ERROR: 12

📋 Уровни логирования:
   🔧 Текущий уровень: INFO
   📊 Доступные уровни: DEBUG, INFO, WARNING, ERROR
```

### `python sdb system health-check`

Проверяет состояние всех компонентов системы.

**Опции:**
- `--full` - полная проверка
- `--fix` - автоматическое исправление проблем
- `--report` - создать отчет

**Примеры:**

```bash
# Базовая проверка здоровья
python sdb system health-check

# Полная проверка
python sdb system health-check --full

# Проверка с автоматическим исправлением
python sdb system health-check --fix
```

**Результат:**
```
🔍 Проверка здоровья системы

📋 Проверка компонентов:
   ✅ Database connection: Подключение активно
   ✅ Bot API connection: API доступен
   ✅ Cache connection: Redis работает
   ✅ Web Server: Сервер отвечает
   ⚠️ External API: Таймаут (5 сек)

📊 Проверка ресурсов:
   ✅ CPU: Нормальная нагрузка (23%)
   ✅ Memory: Достаточно свободной памяти (85%)
   ✅ Disk: Много свободного места (91%)
   ✅ Network: Соединение стабильное

📋 Проверка конфигурации:
   ✅ Все обязательные переменные установлены
   ✅ Права доступа корректны
   ✅ SSL сертификаты валидны
   ⚠️ Некоторые настройки можно оптимизировать

📊 Общий результат:
   🟢 Система работает нормально
   ⚠️ 1 предупреждение (External API)
   📈 Уровень здоровья: 95%
```

## Расширенные команды (в разработке)

### `python sdb system diagnose --full`

Полная диагностика системы.

**Опции:**
- `--full` - полная диагностика
- `--performance` - диагностика производительности
- `--security` - диагностика безопасности
- `--network` - диагностика сети

**Примеры:**

```bash
# Полная диагностика
python sdb system diagnose --full

# Диагностика производительности
python sdb system diagnose --performance

# Диагностика безопасности
python sdb system diagnose --security
```

**Результат:**
```
🔍 Полная диагностика системы

📊 Системная информация:
   🖥️ ОС: Linux 5.15.167.4-microsoft-standard-WSL2
   📊 Архитектура: x86_64
   📊 Ядра: 4
   📊 Память: 8GB

📋 Проверка производительности:
   ✅ CPU: Оптимальная нагрузка
   ✅ Memory: Нет утечек
   ✅ Disk I/O: В норме
   ⚠️ Network: Небольшие задержки

📋 Проверка безопасности:
   ✅ Права доступа корректны
   ✅ SSL сертификаты валидны
   ⚠️ Некоторые файлы имеют избыточные права
   ✅ Брандмауэр активен

📋 Проверка сети:
   ✅ DNS работает корректно
   ✅ Пинг до внешних серверов успешен
   ⚠️ Некоторые порты открыты избыточно
   ✅ SSL/TLS соединения безопасны

📊 Рекомендации:
   🔧 Оптимизировать права доступа к файлам
   🔧 Закрыть неиспользуемые порты
   🔧 Настроить мониторинг сети
   ✅ Общий уровень безопасности: Хороший
```

### `python sdb system troubleshoot --auto-fix`

Автоматическое устранение проблем.

**Опции:**
- `--auto-fix` - автоматическое исправление
- `--dry-run` - показать что будет исправлено
- `--backup` - создать бэкап перед исправлением

**Примеры:**

```bash
# Автоматическое исправление
python sdb system troubleshoot --auto-fix

# Показать что будет исправлено
python sdb system troubleshoot --dry-run

# Исправление с бэкапом
python sdb system troubleshoot --auto-fix --backup
```

**Результат:**
```
🔧 Автоматическое устранение проблем

📋 Найденные проблемы:
   ❌ Права доступа к config.yaml слишком открыты (644)
   ❌ Старые логи занимают много места (500MB)
   ❌ Зависший процесс cache_service (PID: 1236)
   ⚠️ Некоторые переменные окружения не оптимизированы

📊 Исправления:
   ✅ Исправлены права доступа к config.yaml (600)
   ✅ Очищены старые логи (освобождено 500MB)
   ✅ Перезапущен зависший процесс cache_service
   ✅ Оптимизированы переменные окружения

📊 Результат:
   🟢 Все проблемы исправлены
   📈 Производительность улучшена
   🔧 Система оптимизирована
   ⏱️ Время выполнения: 3.2 секунды
```

### `python sdb system update --check --install`

Управление обновлениями системы.

**Опции:**
- `--check` - проверить доступные обновления
- `--install` - установить обновления
- `--backup` - создать бэкап перед обновлением
- `--force` - принудительное обновление

**Примеры:**

```bash
# Проверить обновления
python sdb system update --check

# Установить обновления
python sdb system update --install

# Обновление с бэкапом
python sdb system update --install --backup
```

**Результат:**
```
🔄 Управление обновлениями системы

📋 Проверка обновлений:
   ✅ SwiftDevBot: Доступна версия 1.1.0 (текущая: 1.0.0)
   ✅ Python packages: 5 обновлений доступно
   ✅ System packages: 3 обновления доступно
   ✅ Security updates: 2 критических обновления

📊 Установка обновлений:
   ✅ SwiftDevBot обновлен до версии 1.1.0
   ✅ Python packages обновлены
   ✅ System packages обновлены
   ✅ Security updates установлены

📋 Бэкап создан:
   📁 backup_before_update_20240115_143022
   📊 Размер: 45.2MB
   ✅ Бэкап успешно создан

📊 Результат:
   🟢 Все обновления установлены успешно
   🔧 Система перезапущена
   📈 Новая версия: 1.1.0
   ⏱️ Время обновления: 5.3 минуты
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb system service stop --all` - остановит все сервисы
- `python sdb system env unset --all` - удалит все переменные
- `python sdb system logs --clear` - удалит логи

### ⚠️ Опасные команды:
- `python sdb system service restart --all` - перезапустит все сервисы
- `python sdb system env set` - изменит переменные окружения
- `python sdb system update --install` - установит обновления

### ✅ Безопасные команды:
- `python sdb system status` - только показывает статус
- `python sdb system env list` - только показывает переменные
- `python sdb system service status` - только показывает статус сервисов
- `python sdb system logs --tail` - только читает логи
- `python sdb system health-check` - только проверяет здоровье

## Рекомендации

1. **Регулярные проверки**: Выполняйте health-check еженедельно
2. **Мониторинг логов**: Следите за логами на предмет ошибок
3. **Обновления**: Регулярно проверяйте и устанавливайте обновления
4. **Бэкапы**: Создавайте бэкапы перед важными изменениями
5. **Переменные**: Используйте безопасные значения для секретных переменных

## Устранение проблем

### Проблема: "Сервис не запускается"
```bash
# Проверить статус
python sdb system service status

# Проверить логи
python sdb system logs --service SERVICE_NAME

# Проверить конфигурацию
python sdb system health-check
```

### Проблема: "Ошибка подключения к БД"
```bash
# Проверить переменные окружения
python sdb system env list --filter "DB_"

# Проверить здоровье системы
python sdb system health-check

# Проверить логи
python sdb system logs --level ERROR
```

### Проблема: "Высокая загрузка системы"
```bash
# Проверить статус
python sdb system status

# Диагностика производительности
python sdb system diagnose --performance

# Автоматическое исправление
python sdb system troubleshoot --auto-fix
```

## Интеграция с внешними системами

### Мониторинг
```bash
# Интеграция с Prometheus
python sdb system integrate --monitoring prometheus

# Интеграция с Nagios
python sdb system integrate --monitoring nagios
```

### Логирование
```bash
# Интеграция с ELK Stack
python sdb system integrate --logging elk

# Интеграция с Splunk
python sdb system integrate --logging splunk
```

## Переменные окружения

### Обязательные переменные
- `DATABASE_URL` - URL базы данных
- `API_KEY` - ключ API
- `DEBUG` - режим отладки

### Опциональные переменные
- `LOG_LEVEL` - уровень логирования
- `TIMEZONE` - временная зона
- `REDIS_URL` - URL Redis

### Секретные переменные
- `TELEGRAM_TOKEN` - токен Telegram бота

- `WEBHOOK_URL` - URL webhook 