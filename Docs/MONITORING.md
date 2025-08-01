# 📊 Система мониторинга SwiftDevBot-Lite

## Обзор

Система мониторинга SwiftDevBot-Lite предоставляет комплексный мониторинг производительности системы, сервисов и автоматические алерты с интеграцией уведомлений.

## Возможности

### 🔍 Мониторинг системы
- **CPU**: Загрузка процессора, количество ядер, частота, load average
- **Memory**: Использование RAM и Swap
- **Disk**: Использование диска, I/O операции
- **Network**: Сетевой трафик, пакеты

### 🤖 Мониторинг сервисов
- **Bot API**: Статус Telegram Bot API, время ответа, username
- **Database**: Статус подключения к БД, время ответа, тип БД

### 🚨 Система алертов
- Настраиваемые пороги для CPU, Memory, Disk, Response Time
- Автоматические уведомления через Telegram, Email, Slack
- История алертов и статистика

### 📈 История метрик
- Сохранение метрик в SQLite базу данных
- Просмотр исторических данных
- Статистика (мин/макс/среднее)

## Команды CLI

### Основные команды

```bash
# Показать статус системы
sdb monitor status [--detailed] [--json] [--health] [--notify <channel>]

# Показать метрики производительности
sdb monitor metrics [--cpu] [--memory] [--disk] [--network] [--real-time] [--history] [--hours <n>]

# Управление алертами
sdb monitor alerts [--list] [--configure] [--test] [--history]

# Анализ логов
sdb monitor logs [--analyze] [--errors] [--last <n>] [--since <date>] [--search <pattern>]

# Анализ производительности
sdb monitor performance [--slow-queries] [--response-time] [--memory-leaks] [--bottlenecks]

# Веб-интерфейс
sdb monitor dashboard [--port <port>] [--host <host>] [--theme <theme>]

# Отчеты
sdb monitor report [--daily] [--weekly] [--monthly] [--format <format>] [--email <email>]

# Интеграция с внешними системами
sdb monitor integrate [--prometheus] [--grafana] [--datadog] [--newrelic]
```

### Примеры использования

```bash
# Проверить статус системы
sdb monitor status

# Показать метрики в реальном времени
sdb monitor metrics --real-time

# Показать историю метрик за последние 48 часов
sdb monitor metrics --history --hours 48

# Настроить алерты
sdb monitor alerts --configure

# Протестировать алерты
sdb monitor alerts --test

# Отправить статус в Telegram
sdb monitor status --notify telegram_admin
```

## Конфигурация

### Структура конфигурации алертов

```json
{
  "alerts": {
    "cpu": {
      "warning": 70,
      "critical": 90
    },
    "memory": {
      "warning": 80,
      "critical": 95
    },
    "disk": {
      "warning": 85,
      "critical": 95
    },
    "response_time": {
      "warning": 2.0,
      "critical": 5.0
    }
  },
  "notifications": {
    "enabled": true,
    "channels": ["telegram_admin"],
    "cooldown": 300
  },
  "history": {
    "enabled": true,
    "retention_days": 30
  }
}
```

### Файлы системы мониторинга

- `project_data/monitor/metrics.db` - База данных метрик
- `project_data/monitor/alerts_config.json` - Конфигурация алертов
- `project_data/monitor/metrics_history.json` - История метрик (устаревший)

## Мониторинг в реальном времени

Система поддерживает мониторинг в реальном времени с красивым интерфейсом:

```bash
sdb monitor metrics --real-time
```

Интерфейс показывает:
- Текущие метрики CPU, Memory, Disk, Network
- Статус алертов
- Время обновления
- Цветовую индикацию состояния

## Система алертов

### Типы алертов

- **Warning** (🟡): Предупреждение - превышен порог предупреждения
- **Critical** (🔴): Критический - превышен критический порог

### Настройка алертов

```bash
sdb monitor alerts --configure
```

Интерактивная настройка позволяет:
- Изменить пороги для CPU, Memory, Disk, Response Time
- Включить/отключить уведомления
- Настроить каналы уведомлений

### Тестирование алертов

```bash
sdb monitor alerts --test
```

Создает тестовые метрики и проверяет работу алертов:
- CPU: 95% (критический)
- Memory: 85% (предупреждение)
- Disk: 90% (критический)

## История метрик

### Просмотр истории

```bash
sdb monitor metrics --history --hours 24
```

Показывает:
- Таблицу с историческими данными
- Статистику (мин/макс/среднее)
- Графики трендов

### База данных метрик

Метрики сохраняются в SQLite базу данных со структурой:

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent REAL,
    memory_percent REAL,
    disk_percent REAL,
    network_bytes_sent INTEGER,
    network_bytes_recv INTEGER,
    response_time REAL,
    bot_status TEXT,
    db_status TEXT
);
```

## Интеграция с уведомлениями

Система мониторинга интегрирована с системой уведомлений:

### Автоматические уведомления

При срабатывании алертов автоматически отправляются уведомления:
- **Critical алерты**: Приоритет "urgent"
- **Warning алерты**: Приоритет "high"

### Ручные уведомления

```bash
# Отправить статус системы
sdb monitor status --notify telegram_admin

# Отправить отчет о производительности
sdb monitor report --daily --notify email_support
```

## Мониторинг сервисов

### Bot API

Проверяет:
- Доступность Telegram Bot API
- Время ответа API
- Username бота
- Статус подключения

### Database

Проверяет:
- Подключение к базе данных
- Время ответа на запросы
- Тип базы данных
- Путь к файлу БД

## Производительность

### Оптимизации

- **Асинхронные запросы**: Все HTTP и DB запросы асинхронные
- **Таймауты**: Настроены таймауты для всех внешних запросов
- **Кэширование**: Кэширование конфигурации и метрик
- **Логирование**: Структурированное логирование операций

### Метрики производительности

Система отслеживает:
- Время ответа Bot API
- Время ответа Database
- Использование ресурсов системы
- Сетевой трафик

## Устранение неполадок

### Проблемы с Bot API

1. **Проверьте BOT_TOKEN**:
   ```bash
   echo $BOT_TOKEN
   ```

2. **Проверьте интернет-соединение**:
   ```bash
   curl https://api.telegram.org
   ```

3. **Проверьте права бота**:
   - Бот должен быть создан через @BotFather
   - Токен должен быть действительным

### Проблемы с Database

1. **Проверьте файл БД**:
   ```bash
   ls -la project_data/Database_files/
   ```

2. **Проверьте права доступа**:
   ```bash
   chmod 644 project_data/Database_files/*.db
   ```

3. **Проверьте подключение**:
   ```bash
   sqlite3 project_data/Database_files/sdb_clean_test.db "SELECT 1;"
   ```

### Проблемы с метриками

1. **Проверьте директорию мониторинга**:
   ```bash
   ls -la project_data/monitor/
   ```

2. **Пересоздайте БД метрик**:
   ```bash
   rm project_data/monitor/metrics.db
   sdb monitor status
   ```

3. **Проверьте логи**:
   ```bash
   tail -f project_data/Logs/sdb.log
   ```

## Расширение системы

### Добавление новых метрик

1. Создайте функцию получения метрики
2. Добавьте сохранение в `_save_metrics_to_db()`
3. Обновите отображение в `_display_metrics()`

### Добавление новых алертов

1. Добавьте пороги в `DEFAULT_ALERTS`
2. Добавьте проверку в `_check_alerts()`
3. Обновите конфигурацию

### Интеграция с внешними системами

Система поддерживает интеграцию с:
- **Prometheus**: Экспорт метрик
- **Grafana**: Визуализация
- **DataDog**: Мониторинг
- **New Relic**: APM

## Заключение

Система мониторинга SwiftDevBot-Lite предоставляет:

- ✅ **Комплексный мониторинг** системы и сервисов
- ✅ **Автоматические алерты** с настраиваемыми порогами
- ✅ **Интеграцию с уведомлениями** через различные каналы
- ✅ **Историю метрик** с возможностью анализа
- ✅ **Веб-интерфейс** для удобного просмотра
- ✅ **Высокую производительность** с асинхронными запросами

Система готова для использования в продакшене и может быть расширена для интеграции с внешними системами мониторинга. 