# 🔔 Система уведомлений SwiftDevBot-Lite

## Обзор

Система уведомлений SwiftDevBot-Lite предоставляет возможность отправки уведомлений через различные каналы связи для мониторинга и оповещения о важных событиях в системе.

## Поддерживаемые каналы

### 1. Telegram
- **Описание**: Отправка уведомлений в Telegram чат или канал
- **Требования**: Bot Token и Chat ID
- **Преимущества**: Быстрая доставка, поддержка HTML-форматирования
- **Использование**: Идеально для критических уведомлений и мониторинга

### 2. Email
- **Описание**: Отправка уведомлений по электронной почте
- **Требования**: SMTP сервер, учетные данные, адреса отправителя и получателя
- **Преимущества**: Надежная доставка, поддержка вложений
- **Использование**: Для детальных отчетов и архивных уведомлений

### 3. Slack
- **Описание**: Отправка уведомлений в Slack канал
- **Требования**: Webhook URL и название канала
- **Преимущества**: Интеграция с рабочими процессами, красивое форматирование
- **Использование**: Для командных уведомлений и интеграции с рабочими процессами

### 4. Webhook
- **Описание**: Отправка уведомлений на произвольный HTTP endpoint
- **Требования**: URL endpoint и опциональные заголовки
- **Преимущества**: Гибкость, интеграция с любыми системами
- **Использование**: Для интеграции с внешними системами мониторинга

## Команды CLI

### Основные команды

```bash
# Показать список каналов уведомлений
sdb notifications list [--status active|inactive|configured] [--format table|json]

# Отправить уведомление
sdb notifications send <channel> <message> [--priority low|normal|high|urgent] [--template <template>] [--subject <subject>]

# Настроить канал уведомлений
sdb notifications configure <channel> [--interactive] [--config <file>]

# Протестировать отправку уведомления
sdb notifications test <channel> [--message <message>] [--priority <priority>]
```

### Примеры использования

```bash
# Настроить Telegram канал интерактивно
sdb notifications configure telegram_admin --interactive

# Отправить критическое уведомление
sdb notifications send telegram_admin "Система перезагружена" --priority urgent

# Протестировать Slack канал
sdb notifications test slack_alerts --message "Тестовое уведомление"

# Показать активные каналы
sdb notifications list --status active
```

## Конфигурация

### Структура конфигурации

```json
{
  "channels": {
    "telegram_admin": {
      "type": "telegram",
      "status": "active",
      "description": "Уведомления администраторам",
      "config": {
        "chat_id": "123456789",
        "bot_token": "your_bot_token_here"
      }
    },
    "email_support": {
      "type": "email",
      "status": "active",
      "description": "Email уведомления",
      "config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "from_email": "your_email@gmail.com",
        "to_email": "support@company.com"
      }
    },
    "slack_alerts": {
      "type": "slack",
      "status": "active",
      "description": "Slack уведомления",
      "config": {
        "webhook_url": "https://hooks.slack.com/services/...",
        "channel": "#alerts"
      }
    },
    "webhook_monitoring": {
      "type": "webhook",
      "status": "active",
      "description": "Webhook для мониторинга",
      "config": {
        "url": "https://api.monitoring.com/webhook",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer token"
        }
      }
    }
  },
  "templates": {
    "system_alert": {
      "subject": "🚨 Системное уведомление",
      "body": "Сообщение: {message}\nВремя: {timestamp}\nПриоритет: {priority}"
    },
    "backup_complete": {
      "subject": "✅ Резервное копирование завершено",
      "body": "Резервное копирование успешно завершено в {timestamp}"
    },
    "error_report": {
      "subject": "❌ Ошибка системы",
      "body": "Произошла ошибка: {error}\nВремя: {timestamp}\nКомпонент: {component}"
    }
  }
}
```

## Настройка каналов

### Telegram

1. Создайте бота через @BotFather
2. Получите Bot Token
3. Найдите Chat ID (можно использовать @userinfobot)
4. Настройте канал:

```bash
sdb notifications configure telegram_admin --interactive
```

### Email (Gmail)

1. Включите двухфакторную аутентификацию
2. Создайте пароль приложения
3. Настройте канал:

```bash
sdb notifications configure email_support --interactive
```

### Slack

1. Создайте Incoming Webhook в настройках Slack
2. Скопируйте Webhook URL
3. Настройте канал:

```bash
sdb notifications configure slack_alerts --interactive
```

### Webhook

1. Подготовьте HTTP endpoint
2. Настройте канал:

```bash
sdb notifications configure webhook_monitoring --interactive
```

## Приоритеты уведомлений

- **low** (🔵): Информационные сообщения
- **normal** (⚪): Обычные уведомления
- **high** (🟡): Важные события
- **urgent** (🔴): Критические события

## Шаблоны уведомлений

Система поддерживает шаблоны для стандартизации уведомлений:

```bash
# Использование шаблона
sdb notifications send telegram_admin "Система работает" --template system_alert --priority normal
```

## Логирование

Все операции с уведомлениями логируются в:
- `project_data/notifications/notifications.log`
- Консольный вывод с цветовой индикацией

## Интеграция с мониторингом

Система уведомлений интегрирована с модулем мониторинга:

```bash
# Отправить уведомление о статусе системы
sdb monitor status --notify telegram_admin

# Отправить отчет о производительности
sdb monitor report --notify email_support
```

## Безопасность

- Пароли и токены хранятся в зашифрованном виде
- Поддерживается SSL/TLS для SMTP соединений
- Webhook URL должны использовать HTTPS
- Логи не содержат чувствительной информации

## Устранение неполадок

### Telegram
- Проверьте правильность Bot Token и Chat ID
- Убедитесь, что бот добавлен в чат
- Проверьте интернет-соединение

### Email
- Проверьте SMTP настройки
- Убедитесь, что используется правильный пароль приложения
- Проверьте настройки безопасности Gmail

### Slack
- Проверьте правильность Webhook URL
- Убедитесь, что канал существует
- Проверьте права доступа webhook'а

### Webhook
- Проверьте доступность endpoint
- Убедитесь в правильности HTTP метода
- Проверьте заголовки авторизации

## Расширение системы

Для добавления новых типов каналов:

1. Создайте функцию `_send_<type>_notification()`
2. Добавьте обработку в `_send_notification_by_type()`
3. Создайте функцию настройки `_configure_<type>_interactive()`
4. Обновите документацию

## Примеры интеграции

### Автоматические уведомления при ошибках

```python
# В коде приложения
from cli.notifications import _send_notification_by_type

async def notify_error(error_msg: str):
    config = _load_notifications_config()
    channel_info = config["channels"]["telegram_admin"]
    await _send_notification_by_type(channel_info, error_msg, "urgent")
```

### Планировщик уведомлений

```bash
# Cron задача для ежедневного отчета
0 9 * * * sdb notifications send email_support "Ежедневный отчет" --template daily_report
```

## Заключение

Система уведомлений SwiftDevBot-Lite предоставляет надежный и гибкий способ отправки уведомлений через различные каналы связи. Интеграция с CLI обеспечивает удобное управление и настройку, а поддержка шаблонов позволяет стандартизировать уведомления. 