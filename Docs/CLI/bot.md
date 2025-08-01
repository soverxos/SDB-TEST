# 🤖 Управление Telegram ботом (bot)

## Обзор

Модуль `bot` предоставляет полный набор команд для управления Telegram ботом SwiftDevBot, включая запуск, остановку, перезапуск, мониторинг и настройку.

## Основные команды

### `python sdb bot start`

Запускает бота в указанном режиме.

**Опции:**
- `--mode production/development/debug` - режим работы
- `--daemon` - запуск в фоновом режиме
- `--config FILE` - файл конфигурации
- `--log-level LEVEL` - уровень логирования

**Примеры:**

```bash
# Запустить Telegram бота
python sdb bot start

# Запустить в режиме разработки
python sdb bot start --mode development

# Запустить в фоновом режиме
python sdb bot start --daemon

# Запустить с кастомной конфигурацией
python sdb bot start --config custom_config.yaml
```

**Результат:**
```
🤖 Запуск Telegram бота SwiftDevBot-Lite...

📱 Telegram Bot:
   ✅ Токен: Проверен
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: production

📊 Общая статистика:
   🟢 Бот запущен успешно
   ⏱️ Время запуска: 2.3 секунды
   📈 Готов к работе
```

### `python sdb bot stop`

Останавливает бота.

**Опции:**
- `--force` - принудительная остановка
- `--timeout SECONDS` - таймаут остановки

**Примеры:**

```bash
# Остановить Telegram бота
python sdb bot stop

# Принудительная остановка
python sdb bot stop --force

# Остановка с таймаутом
python sdb bot stop --timeout 30
```

**Результат:**
```
🛑 Остановка Telegram бота SwiftDevBot-Lite...

📱 Telegram Bot:
   ✅ Процесс найден (PID: 1234)
   ✅ Сигнал остановки отправлен
   ✅ Процесс остановлен
   ⏱️ Время остановки: 1.2 секунды

📊 Результат:
   🟢 Бот остановлен успешно
```

### `python sdb bot restart`

Перезапускает бота.

**Опции:**
- `--mode production/development/debug` - режим работы
- `--config FILE` - файл конфигурации

**Примеры:**

```bash
# Перезапустить Telegram бота
python sdb bot restart

# Перезапустить в режиме разработки
python sdb bot restart --mode development
```

**Результат:**
```
🔄 Перезапуск Telegram бота SwiftDevBot-Lite...

📱 Telegram Bot:
   ✅ Остановка: Успешно
   ✅ Запуск: Успешно
   ✅ Статус: Работает (PID: 1236)

📊 Результат:
   🟢 Бот перезапущен успешно
   ⏱️ Общее время: 3.5 секунды
```

### `python sdb bot status`

Показывает статус ботов.

**Опции:**
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON

**Примеры:**

```bash
# Показать статус Telegram бота
python sdb bot status

# Подробная информация
python sdb bot status --detailed
```

**Результат:**
```
🤖 Статус Telegram бота SwiftDevBot-Lite

📱 Telegram Bot:
   🟢 Статус: Работает
   📊 PID: 1234
   📊 Uptime: 2 часа 15 минут
   📊 Сообщений: 1,234
   📊 Команд: 567
   📊 Ошибок: 0

📊 Общая статистика:
   🟢 Бот работает нормально
   📈 Uptime: 99.8%
   📊 Всего сообщений: 1,234
```

### `python sdb bot config`

Управляет конфигурацией ботов.

**Опции:**
- `--show` - показать текущую конфигурацию
- `--set KEY=VALUE` - установить значение
- `--reset` - сбросить к значениям по умолчанию
- `--export FILE` - экспортировать конфигурацию

**Примеры:**

```bash
# Показать конфигурацию Telegram бота
python sdb bot config --show

# Установить значение
python sdb bot config --set "telegram.webhook_url=https://example.com/webhook"

# Сбросить конфигурацию
python sdb bot config --reset

# Экспортировать конфигурацию
python sdb bot config --export config_backup.yaml
```

**Результат:**
```
⚙️ Конфигурация Telegram бота

📱 Telegram Bot:
   ✅ Токен: ***hidden***
   ✅ Webhook URL: https://example.com/webhook
   ✅ Команды: 15 активных
   ✅ Плагины: 8 загружено
   ✅ Логирование: INFO

📊 Общие настройки:
   ✅ Режим: production
   ✅ Язык: ru
   ✅ Временная зона: UTC
```

## Расширенные команды (в разработке)

### `python sdb bot logs`

Показывает логи Telegram бота.

**Опции:**
- `--lines N` - количество строк
- `--follow` - следить за логами в реальном времени
- `--level LEVEL` - уровень логирования
- `--grep PATTERN` - фильтр по паттерну

**Примеры:**

```bash
# Показать последние 50 строк логов
python sdb bot logs --lines 50

# Следить за логами в реальном времени
python sdb bot logs --follow

# Логи только ошибок
python sdb bot logs --level ERROR

# Поиск по паттерну
python sdb bot logs --grep "webhook"
```

### `python sdb bot test`

Тестирует подключение Telegram бота.

**Опции:**
- `--webhook` - тест webhook
- `--commands` - тест команд
- `--permissions` - тест прав доступа

**Примеры:**

```bash
# Тест Telegram бота
python sdb bot test

# Тест webhook
python sdb bot test --webhook

# Тест команд
python sdb bot test --commands
```

### `python sdb bot update`

Обновляет Telegram бота.

**Опции:**
- `--force` - принудительное обновление
- `--backup` - создать бэкап перед обновлением

**Примеры:**

```bash
# Обновить Telegram бота
python sdb bot update

# Принудительное обновление
python sdb bot update --force

# Обновление с бэкапом
python sdb bot update --backup
```

### `python sdb bot webhook`

Управляет webhook для Telegram бота.

**Опции:**
- `--set URL` - установить webhook URL
- `--delete` - удалить webhook
- `--info` - информация о webhook
- `--test` - тест webhook

**Примеры:**

```bash
# Установить webhook
python sdb bot webhook --set "https://example.com/webhook"

# Удалить webhook
python sdb bot webhook --delete

# Информация о webhook
python sdb bot webhook --info

# Тест webhook
python sdb bot webhook --test
```

### `python sdb bot commands`

Управляет командами Telegram бота.

**Опции:**
- `--list` - список команд
- `--enable COMMAND` - включить команду
- `--disable COMMAND` - отключить команду
- `--reload` - перезагрузить команды

**Примеры:**

```bash
# Список всех команд
python sdb bot commands --list

# Включить команду
python sdb bot commands --enable "help"

# Отключить команду
python sdb bot commands --disable "admin"

# Перезагрузить команды
python sdb bot commands --reload
```

### `python sdb bot plugins`

Управляет плагинами Telegram бота.

**Опции:**
- `--list` - список плагинов
- `--install PLUGIN` - установить плагин
- `--uninstall PLUGIN` - удалить плагин
- `--update PLUGIN` - обновить плагин

**Примеры:**

```bash
# Список плагинов
python sdb bot plugins --list

# Установить плагин
python sdb bot plugins --install "weather"

# Удалить плагин
python sdb bot plugins --uninstall "old_plugin"

# Обновить плагин
python sdb bot plugins --update "weather"
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb bot stop --force` - принудительная остановка может повредить данные
- `python sdb bot config --reset` - сброс конфигурации

### ⚠️ Опасные команды:
- `python sdb bot restart` - перезапуск прерывает работу
- `python sdb bot update --force` - принудительное обновление
- `python sdb bot webhook --delete` - удаление webhook

### ✅ Безопасные команды:
- `python sdb bot status` - только показывает статус
- `python sdb bot config --show` - только показывает конфигурацию
- `python sdb bot logs` - только показывает логи

## Устранение проблем

### Проблема: "Telegram бот не запускается"
```bash
# Проверить токены
python sdb bot config --show

# Проверить логи
python sdb bot logs --level ERROR

# Тест подключения
python sdb bot test
```

### Проблема: "Webhook не работает"
```bash
# Проверить webhook
python sdb bot webhook --info

# Тест webhook
python sdb bot webhook --test

# Переустановить webhook
python sdb bot webhook --set "https://example.com/webhook"
```

### Проблема: "Команды не работают"
```bash
# Список команд
python sdb bot commands --list

# Перезагрузить команды
python sdb bot commands --reload

# Проверить права
python sdb bot test --permissions
```

## Рекомендации

1. **Мониторинг**: Регулярно проверяйте статус Telegram бота
2. **Логи**: Настройте правильный уровень логирования
3. **Бэкапы**: Создавайте бэкапы перед обновлениями
4. **Тестирование**: Тестируйте изменения в режиме разработки
5. **Безопасность**: Храните токены в безопасном месте 