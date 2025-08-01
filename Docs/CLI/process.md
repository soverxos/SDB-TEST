# 🔄 Управление процессами (process)

## Обзор

Модуль `process` предоставляет инструменты для управления процессами SwiftDevBot, включая мониторинг, управление ресурсами, диагностику производительности и оптимизацию работы системы.

## Основные команды

### `python sdb process list`

Показывает список всех процессов SwiftDevBot.

**Опции:**
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON
- `--sort-by cpu/memory/pid` - сортировка
- `--filter PATTERN` - фильтр по паттерну

**Примеры:**

```bash
# Показать все процессы
python sdb process list

# Подробная информация
python sdb process list --detailed

# Сортировка по использованию CPU
python sdb process list --sort-by cpu

# Фильтр по имени
python sdb process list --filter "bot"
```

**Результат:**
```
🔄 Процессы SwiftDevBot-Lite

📱 Telegram Bot:
   🟢 PID: 1234
   📊 CPU: 2.3%
   📊 Memory: 45.2MB
   📊 Uptime: 2 часа 15 минут
   📊 Статус: Работает



🌐 Web Server:
   🟢 PID: 1236
   📊 CPU: 0.5%
   📊 Memory: 12.3MB
   📊 Uptime: 2 часа 15 минут
   📊 Статус: Работает

🗄️ Database:
   🟢 PID: 1237
   📊 CPU: 0.2%
   📊 Memory: 8.9MB
   📊 Uptime: 2 часа 15 минут
   📊 Статус: Работает

📊 Общая статистика:
   🟢 Всего процессов: 3
   📊 Общий CPU: 3.0%
   📊 Общая память: 66.4MB
   📊 Все процессы работают нормально
```

### `python sdb process status`

Показывает статус конкретного процесса.

**Опции:**
- `PID` - ID процесса
- `--detailed` - подробная информация
- `--monitor` - мониторинг в реальном времени
- `--json` - вывод в формате JSON

**Примеры:**

```bash
# Статус процесса по PID
python sdb process status 1234

# Подробная информация
python sdb process status 1234 --detailed

# Мониторинг в реальном времени
python sdb process status 1234 --monitor
```

**Результат:**
```
📊 Статус процесса PID: 1234

📋 Основная информация:
   📊 Имя: telegram_bot
   📊 PID: 1234
   📊 PPID: 1000
   📊 Пользователь: root
   📊 Статус: S (спящий)

📋 Ресурсы:
   📊 CPU: 2.3% (0.23 ядра)
   📊 Memory: 45.2MB (RSS: 42.1MB)
   📊 Virtual Memory: 128.5MB
   📊 Shared Memory: 12.3MB

📋 Время работы:
   📊 Запущен: 2024-01-15 12:15:30
   📊 Uptime: 2 часа 15 минут 32 секунды
   📊 CPU время: 1 минута 23 секунды

📋 Сетевые соединения:
   📊 TCP соединений: 3
   📊 UDP соединений: 1
   📊 Открытые файлы: 15

📋 Потоки:
   📊 Всего потоков: 8
   📊 Активных потоков: 6
   📊 Спящих потоков: 2
```

### `python sdb process kill`

Завершает процесс.

**Опции:**
- `PID` - ID процесса для завершения
- `--signal SIGNAL` - сигнал для отправки
- `--force` - принудительное завершение
- `--timeout SECONDS` - таймаут завершения

**Примеры:**

```bash
# Завершить процесс
python sdb process kill 1234

# Отправить сигнал SIGTERM
python sdb process kill 1234 --signal SIGTERM

# Принудительное завершение
python sdb process kill 1234 --force

# Завершение с таймаутом
python sdb process kill 1234 --timeout 30
```

**Результат:**
```
🛑 Завершение процесса PID: 1234

📋 Информация о процессе:
   📊 Имя: telegram_bot
   📊 PID: 1234
   📊 Статус: Работает

📥 Процесс завершения:
   ✅ Сигнал SIGTERM отправлен
   ✅ Процесс остановлен
   ✅ Ресурсы освобождены
   ✅ Файлы закрыты

📊 Результат:
   ✅ Процесс завершен успешно
   ⏱️ Время завершения: 1.2 секунды
   📊 Освобождено памяти: 45.2MB
```

### `python sdb process restart`

Перезапускает процесс.

**Опции:**
- `PID` - ID процесса для перезапуска
- `--wait SECONDS` - время ожидания между остановкой и запуском
- `--force` - принудительный перезапуск
- `--config FILE` - файл конфигурации

**Примеры:**

```bash
# Перезапустить процесс
python sdb process restart 1234

# Перезапуск с ожиданием
python sdb process restart 1234 --wait 5

# Принудительный перезапуск
python sdb process restart 1234 --force

# Перезапуск с конфигурацией
python sdb process restart 1234 --config custom_config.yaml
```

**Результат:**
```
🔄 Перезапуск процесса PID: 1234

📋 Информация о процессе:
   📊 Имя: telegram_bot
   📊 PID: 1234
   📊 Статус: Работает

📥 Процесс перезапуска:
   ✅ Процесс остановлен
   ⏱️ Ожидание: 3 секунды
   ✅ Процесс запущен
   ✅ Проверка статуса

📊 Результат:
   ✅ Процесс перезапущен успешно
   📊 Новый PID: 1238
   ⏱️ Время перезапуска: 4.5 секунды
   📊 Статус: Работает
```

### `python sdb process monitor`

Мониторит процессы в реальном времени.

**Опции:**
- `--interval SECONDS` - интервал обновления
- `--pid PID` - мониторинг конкретного процесса
- `--cpu` - показывать только CPU
- `--memory` - показывать только память

**Примеры:**

```bash
# Мониторинг всех процессов
python sdb process monitor

# Мониторинг с интервалом 5 секунд
python sdb process monitor --interval 5

# Мониторинг конкретного процесса
python sdb process monitor --pid 1234

# Мониторинг только CPU
python sdb process monitor --cpu
```

**Результат:**
```
📊 Мониторинг процессов SwiftDevBot-Lite
⏱️ Обновление каждые: 3 секунды

PID     Имя              CPU    Memory   Статус
1234    telegram_bot     2.3%   45.2MB   🟢 Работает

1236    web_server       0.5%   12.3MB   🟢 Работает
1237    database         0.2%   8.9MB    🟢 Работает

📊 Общие ресурсы:
   📊 CPU: 4.8% / 100%
   📊 Memory: 105.1MB / 8GB
   📊 Все процессы работают нормально

Нажмите Ctrl+C для выхода...
```

## Расширенные команды (в разработке)

### `python sdb process analyze`

Анализирует производительность процессов.

**Опции:**
- `--pid PID` - анализировать конкретный процесс
- `--duration SECONDS` - продолжительность анализа
- `--output FILE` - файл для сохранения результатов
- `--cpu-profile` - профилирование CPU

**Примеры:**

```bash
# Анализ всех процессов
python sdb process analyze

# Анализ конкретного процесса
python sdb process analyze --pid 1234

# Анализ в течение 60 секунд
python sdb process analyze --duration 60

# Анализ с профилированием CPU
python sdb process analyze --cpu-profile
```

### `python sdb process optimize`

Оптимизирует процессы.

**Опции:**
- `--pid PID` - оптимизировать конкретный процесс
- `--memory` - оптимизация памяти
- `--cpu` - оптимизация CPU
- `--auto` - автоматическая оптимизация

**Примеры:**

```bash
# Автоматическая оптимизация
python sdb process optimize --auto

# Оптимизация конкретного процесса
python sdb process optimize --pid 1234

# Оптимизация памяти
python sdb process optimize --memory

# Оптимизация CPU
python sdb process optimize --cpu
```

### `python sdb process debug`

Отлаживает процессы.

**Опции:**
- `PID` - ID процесса для отладки
- `--attach` - подключиться к процессу
- `--trace` - трассировка вызовов
- `--log` - включить подробное логирование

**Примеры:**

```bash
# Отладка процесса
python sdb process debug 1234

# Подключение к процессу
python sdb process debug 1234 --attach

# Трассировка вызовов
python sdb process debug 1234 --trace

# Подробное логирование
python sdb process debug 1234 --log
```

### `python sdb process resource`

Управляет ресурсами процессов.

**Опции:**
- `--pid PID` - ID процесса
- `--limit-cpu PERCENT` - ограничить CPU
- `--limit-memory MB` - ограничить память
- `--priority LEVEL` - установить приоритет

**Примеры:**

```bash
# Ограничить CPU
python sdb process resource --pid 1234 --limit-cpu 50

# Ограничить память
python sdb process resource --pid 1234 --limit-memory 100

# Установить приоритет
python sdb process resource --pid 1234 --priority high

# Показать ограничения
python sdb process resource --pid 1234
```

### `python sdb process snapshot`

Создает снимок состояния процессов.

**Опции:**
- `--output FILE` - файл для сохранения
- `--format json/yaml` - формат вывода
- `--include-stacks` - включить стеки вызовов
- `--compress` - сжать снимок

**Примеры:**

```bash
# Создать снимок
python sdb process snapshot

# Сохранить в файл
python sdb process snapshot --output snapshot.json

# Снимок в YAML
python sdb process snapshot --format yaml

# Снимок со стеками
python sdb process snapshot --include-stacks
```

### `python sdb process compare`

Сравнивает состояния процессов.

**Опции:**
- `SNAPSHOT1` - первый снимок
- `SNAPSHOT2` - второй снимок
- `--output FILE` - файл для сохранения
- `--detailed` - подробное сравнение

**Примеры:**

```bash
# Сравнить снимки
python sdb process compare snapshot1.json snapshot2.json

# Подробное сравнение
python sdb process compare snapshot1.json snapshot2.json --detailed

# Сохранить результат
python sdb process compare snapshot1.json snapshot2.json --output diff.txt
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb process kill --force` - принудительное завершение может повредить данные
- `python sdb process restart --force` - принудительный перезапуск
- `python sdb process resource --limit-memory 0` - полное ограничение памяти

### ⚠️ Опасные команды:
- `python sdb process kill` - завершение процесса
- `python sdb process restart` - перезапуск процесса
- `python sdb process debug --attach` - подключение к процессу

### ✅ Безопасные команды:
- `python sdb process list` - только показывает процессы
- `python sdb process status` - только показывает статус
- `python sdb process monitor` - только мониторит
- `python sdb process snapshot` - только создает снимок

## Устранение проблем

### Проблема: "Процесс не отвечает"
```bash
# Проверить статус
python sdb process status PID

# Попробовать перезапустить
python sdb process restart PID

# Принудительно завершить
python sdb process kill PID --force
```

### Проблема: "Высокое использование ресурсов"
```bash
# Анализ процессов
python sdb process analyze

# Ограничить ресурсы
python sdb process resource --pid PID --limit-cpu 50

# Оптимизировать
python sdb process optimize --auto
```

### Проблема: "Процесс завис"
```bash
# Проверить статус
python sdb process status PID

# Отладить процесс
python sdb process debug PID

# Принудительно завершить
python sdb process kill PID --force
```

## Рекомендации

1. **Мониторинг**: Регулярно проверяйте состояние процессов
2. **Ресурсы**: Следите за использованием CPU и памяти
3. **Логи**: Анализируйте логи для выявления проблем
4. **Оптимизация**: Периодически оптимизируйте процессы
5. **Бэкапы**: Создавайте снимки состояния системы 