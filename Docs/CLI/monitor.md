# 📊 Мониторинг и аналитика (monitor)

## Обзор

Модуль `monitor` предоставляет комплексные инструменты для мониторинга производительности, анализа логов, управления алертами и создания отчетов о состоянии системы SwiftDevBot.

## Основные команды

### `python sdb monitor status`

Показывает общий статус системы и всех компонентов.

**Опции:**
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON
- `--health` - только проверка здоровья

**Примеры:**

```bash
# Показать общий статус
python sdb monitor status

# Подробная информация
python sdb monitor status --detailed

# Только проверка здоровья
python sdb monitor status --health
```

**Результат:**
```
📊 Статус системы SwiftDevBot-Lite

🤖 Bot API: 🟢 Работает (uptime: 15d 8h 32m)
   📊 Запросов/мин: 45
   📈 Среднее время ответа: 120ms
   🔗 Активные соединения: 12

🗄️ Database: 🟢 Работает (connections: 12/50)
   📊 Размер БД: 2.1GB
   📈 Запросов/сек: 150
   🔗 Активные транзакции: 3

🧩 Modules: 🟢 8 активных модулей
   ✅ telegram_bot: Работает
   
   ✅ web_interface: Работает
   ⚠️ email_sender: Предупреждение (очередь: 15)

🔌 API: 🟢 Работает (requests/min: 45)
   📊 Endpoints: 25 активных
   📈 Среднее время ответа: 85ms
   🔗 Rate limiting: Активен

📊 Общая статистика:
   🟢 Все системы работают нормально
   📈 Uptime: 99.8%
   🔧 Последний перезапуск: 15 дней назад
```

### `python sdb monitor metrics --cpu --memory --disk`

Показывает метрики производительности системы.

**Опции:**
- `--cpu` - загрузка процессора
- `--memory` - использование памяти
- `--disk` - использование диска
- `--network` - сетевой трафик
- `--real-time` - обновление в реальном времени
- `--history` - исторические данные

**Примеры:**

```bash
# Показать все метрики
python sdb monitor metrics --cpu --memory --disk --network

# Метрики в реальном времени
python sdb monitor metrics --cpu --memory --real-time

# Исторические данные
python sdb monitor metrics --cpu --history
```

**Результат:**
```
📊 Метрики производительности системы

🖥️ CPU (Процессор):
   📊 Текущая загрузка: 23%
   📈 Средняя загрузка (1 час): 18%
   📈 Пиковая загрузка (24 часа): 45%
   🔧 4 ядра, 2.4GHz каждый

💾 Memory (Память):
   📊 Использовано: 1.2GB / 8GB (15%)
   📈 Доступно: 6.8GB
   📈 Свободно: 2.1GB
   🔧 Swap: 0GB / 2GB (0%)

💿 Disk (Диск):
   📊 Использовано: 45GB / 500GB (9%)
   📈 Свободно: 455GB
   📈 Скорость чтения: 120MB/s
   📈 Скорость записи: 85MB/s

🌐 Network (Сеть):
   📊 Входящий трафик: 2.1MB/s
   📊 Исходящий трафик: 1.8MB/s
   📈 Всего получено: 15.2GB
   📈 Всего отправлено: 12.8GB

📊 Рекомендации:
   ✅ Все метрики в норме
   ✅ Производительность оптимальная
   ⚠️ Рекомендуется мониторинг при росте нагрузки
```

### `python sdb monitor alerts --list --configure`

Управление системой оповещений.

**Опции:**
- `--list` - показать активные оповещения
- `--configure` - настроить правила оповещений
- `--test` - протестировать оповещения
- `--history` - история алертов

**Примеры:**

```bash
# Показать активные алерты
python sdb monitor alerts --list

# Настроить алерты
python sdb monitor alerts --configure

# Протестировать алерты
python sdb monitor alerts --test
```

**Результат:**
```
🔔 Управление системой оповещений

📋 Активные алерты:
   🟢 Все системы работают нормально
   ✅ Последняя проверка: 2 минуты назад

📋 Настроенные правила:
   🔴 CPU > 80%: Уведомление по email
   🔴 Memory > 90%: Уведомление в Telegram
   🔴 Disk > 95%: Критическое уведомление
   🟡 Response time > 2s: Предупреждение

📊 Статистика алертов (24 часа):
   🔴 Критических: 0
   🟡 Предупреждений: 2
   🟢 Информационных: 15

📧 Каналы уведомлений:
   ✅ Email: admin@example.com
   ✅ Telegram: @admin_bot
```

### `python sdb monitor logs --analyze --errors`

Анализ логов системы.

**Опции:**
- `--analyze` - анализ паттернов в логах
- `--errors` - показ только ошибок
- `--last N` - последние N записей
- `--since DATE` - логи с определенной даты
- `--search PATTERN` - поиск по паттерну

**Примеры:**

```bash
# Анализ всех логов
python sdb monitor logs --analyze

# Показать только ошибки
python sdb monitor logs --errors

# Последние 100 записей
python sdb monitor logs --last 100

# Поиск по паттерну
python sdb monitor logs --search "error"
```

**Результат:**
```
📋 Анализ логов системы

📊 Статистика за 24 часа:
   📝 Всего записей: 15,420
   ❌ Ошибок: 12
   ⚠️ Предупреждений: 45
   🟢 Информационных: 15,363

🔍 Топ ошибок:
   ❌ Connection timeout: 5 раз
   ❌ Database lock: 3 раза
   ❌ Memory allocation failed: 2 раза
   ❌ Invalid API key: 2 раза

📈 Паттерны активности:
   📊 Пиковая нагрузка: 14:00-16:00
   📊 Минимальная нагрузка: 02:00-06:00
   📊 Средняя активность: 45 запросов/мин

📋 Рекомендации:
   🔧 Оптимизировать подключения к БД
   🔧 Увеличить лимиты памяти
   🔧 Проверить валидность API ключей
```

### `python sdb monitor performance --slow-queries`

Анализ производительности системы.

**Опции:**
- `--slow-queries` - медленные запросы к БД
- `--response-time` - время ответа API
- `--memory-leaks` - поиск утечек памяти
- `--bottlenecks` - поиск узких мест

**Примеры:**

```bash
# Анализ медленных запросов
python sdb monitor performance --slow-queries

# Анализ времени ответа
python sdb monitor performance --response-time

# Поиск утечек памяти
python sdb monitor performance --memory-leaks
```

**Результат:**
```
⚡ Анализ производительности системы

🔍 Медленные запросы (>1 сек):
   ❌ SELECT * FROM messages WHERE user_id = ? (2.3 сек)
   ❌ UPDATE users SET last_seen = ? (1.8 сек)
   ❌ INSERT INTO logs VALUES (...) (1.5 сек)

📊 Время ответа API:
   📈 Среднее время: 120ms
   📈 95-й процентиль: 450ms
   📈 99-й процентиль: 1.2 сек
   📈 Максимальное время: 2.8 сек

🔧 Рекомендации по оптимизации:
   ✅ Добавить индексы на user_id и last_seen
   ✅ Оптимизировать запросы к таблице logs
   ✅ Настроить кэширование частых запросов
   ✅ Рассмотреть партиционирование больших таблиц

📊 Метрики производительности:
   🟢 CPU: Оптимальная нагрузка
   🟢 Memory: Нет утечек
   🟢 Disk I/O: В норме
   ⚠️ Network: Небольшие задержки
```

## Расширенные команды (в разработке)

### `python sdb monitor dashboard`

Запускает веб-интерфейс для мониторинга.

**Опции:**
- `--port PORT` - порт для веб-интерфейса
- `--host HOST` - хост для веб-интерфейса
- `--theme dark/light` - тема интерфейса

**Примеры:**

```bash
# Запустить дашборд
python sdb monitor dashboard

# Запустить на определенном порту
python sdb monitor dashboard --port 8080

# Запустить с темной темой
python sdb monitor dashboard --theme dark
```

**Результат:**
```
🌐 Веб-дашборд мониторинга запущен

🔗 URL: http://localhost:8080/monitor
📊 Доступные метрики: CPU, Memory, Disk, Network
🔔 Алерты: В реальном времени
📈 Графики: Интерактивные
🎨 Тема: Светлая

📋 Функции дашборда:
   📊 Графики производительности
   🔔 Управление алертами
   📋 Анализ логов
   📈 Отчеты
   ⚙️ Настройки мониторинга
```

### `python sdb monitor report --daily --weekly --monthly`

Генерирует отчеты о производительности.

**Опции:**
- `--daily` - ежедневный отчет
- `--weekly` - еженедельный отчет
- `--monthly` - ежемесячный отчет
- `--format html/pdf/json` - формат отчета
- `--email` - отправить по email

**Примеры:**

```bash
# Ежедневный отчет
python sdb monitor report --daily

# Еженедельный отчет в PDF
python sdb monitor report --weekly --format pdf

# Отправить отчет по email
python sdb monitor report --daily --email admin@example.com
```

**Результат:**
```
📄 Генерация отчета о производительности

📊 Период: 2024-01-14 00:00 - 2024-01-15 00:00
📈 Метрики: CPU, Memory, Disk, Network
📋 Содержание:
   📊 Производительность системы
   📊 Статистика безопасности
   📊 Использование ресурсов
   📊 Рекомендации по оптимизации

📄 Отчет создан: daily_report_2024-01-15.pdf
📧 Отправлен на: admin@example.com
📊 Размер файла: 2.3MB
```

### `python sdb monitor integrate --prometheus --grafana`

Интеграция с системами мониторинга.

**Опции:**
- `--prometheus` - интеграция с Prometheus
- `--grafana` - интеграция с Grafana
- `--datadog` - интеграция с DataDog
- `--newrelic` - интеграция с New Relic

**Примеры:**

```bash
# Интеграция с Prometheus и Grafana
python sdb monitor integrate --prometheus --grafana

# Интеграция с DataDog
python sdb monitor integrate --datadog
```

**Результат:**
```
🔗 Настройка интеграции с системами мониторинга

✅ Интеграция с Prometheus настроена
📊 Метрики экспортируются на: localhost:9090
🎨 Дашборд Grafana создан: http://localhost:3000
📈 Автоматические алерты настроены

📋 Настроенные метрики:
   📊 Системные метрики (CPU, Memory, Disk)
   📊 Метрики приложения (запросы, ошибки)
   📊 Метрики базы данных (соединения, запросы)
   📊 Метрики сети (трафик, задержки)

🔔 Алерты:
   🔴 CPU > 80%
   🔴 Memory > 90%
   🟡 Response time > 2s
   🟡 Error rate > 5%
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb monitor alerts --clear` - очистит все алерты
- `python sdb monitor logs --clear` - удалит логи

### ⚠️ Опасные команды:
- `python sdb monitor alerts --configure` - изменит настройки алертов
- `python sdb monitor logs --rotate` - перезапишет логи

### ✅ Безопасные команды:
- `python sdb monitor status` - только показывает статус
- `python sdb monitor metrics` - только собирает метрики
- `python sdb monitor alerts --list` - только показывает алерты
- `python sdb monitor logs --analyze` - только анализирует логи
- `python sdb monitor performance` - только анализирует производительность
- `python sdb monitor dashboard` - только показывает дашборд
- `python sdb monitor report` - только генерирует отчеты

## Рекомендации

1. **Регулярный мониторинг**: Настройте автоматические проверки
2. **Алерты**: Настройте уведомления о критических событиях
3. **Логи**: Регулярно анализируйте логи на предмет проблем
4. **Производительность**: Следите за метриками производительности
5. **Отчеты**: Генерируйте регулярные отчеты для анализа трендов

## Устранение проблем

### Проблема: "Высокая загрузка CPU"
```bash
# Проверить метрики
python sdb monitor metrics --cpu

# Анализ производительности
python sdb monitor performance --bottlenecks

# Проверить логи
python sdb monitor logs --errors
```

### Проблема: "Медленные запросы"
```bash
# Анализ медленных запросов
python sdb monitor performance --slow-queries

# Проверить время ответа API
python sdb monitor performance --response-time
```

### Проблема: "Утечки памяти"
```bash
# Поиск утечек памяти
python sdb monitor performance --memory-leaks

# Анализ использования памяти
python sdb monitor metrics --memory
```

## Интеграция с внешними системами

### Prometheus + Grafana
```bash
# Настройка экспорта метрик
python sdb monitor integrate --prometheus

# Создание дашбордов
python sdb monitor integrate --grafana
```

### DataDog
```bash
# Интеграция с DataDog
python sdb monitor integrate --datadog
```

### New Relic
```bash
# Интеграция с New Relic
python sdb monitor integrate --newrelic
```

## Метрики и алерты

### Системные метрики
- CPU загрузка
- Использование памяти
- Использование диска
- Сетевой трафик

### Метрики приложения
- Количество запросов
- Время ответа
- Количество ошибок
- Активные соединения

### Метрики базы данных
- Количество соединений
- Время выполнения запросов
- Размер базы данных
- Количество транзакций

### Настройка алертов
- Критические (>90% ресурсов)
- Предупреждения (>80% ресурсов)
- Информационные (важные события) 