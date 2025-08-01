# 🚀 CLI команды SwiftDevBot-Lite

## Обзор

SwiftDevBot-Lite предоставляет мощный набор CLI команд для управления всеми аспектами системы. Каждая команда оптимизирована для конкретных задач и включает подробную документацию.

## 📋 Список команд

### 🔧 Основные команды

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb run` | Запуск системы | ✅ Готово |
| `python sdb bot` | Управление Telegram ботом | ✅ Готово |
| `python sdb config` | Управление конфигурацией | ✅ Готово |
| `python sdb system` | Системные настройки | ✅ Готово |
| `python sdb db` | Управление базой данных | ✅ Готово |

### 💾 Команды бэкапа

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb backup` | Обычные бэкапы | ✅ Готово |
| `python sdb backup_smart` | Умные бэкапы | ✅ Готово |

### 📦 Команды модулей

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb module` | Управление модулями | ✅ Готово |

### 🔄 Команды процессов

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb process` | Управление процессами | ✅ Готово |

### 👥 Команды пользователей

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb user` | Управление пользователями | ✅ Готово |

### 🛠️ Утилиты

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb utils` | Утилитарные команды | ✅ Готово |

### 🔍 Мониторинг и аналитика

| Команда | Описание | Статус |
|---------|----------|--------|
| `python sdb monitor` | Мониторинг системы | ✅ Готово |
| `python sdb cache` | Управление кэшем | ✅ Готово |
| `python sdb api` | API управление | ✅ Готово |
| `python sdb dev` | Инструменты разработки | ✅ Готово |
| `python sdb tasks` | Управление задачами | ✅ Готово |
| `python sdb notifications` | Уведомления | ✅ Готово |
| `python sdb security` | Безопасность | ✅ Готово |

## 🚀 Быстрый старт

### 1. Запуск системы

```bash
# Запустить в продакшн режиме
python sdb run

# Запустить в режиме разработки
python sdb run dev

# Запустить с отладкой
python sdb run debug
```

### 2. Проверка статуса

```bash
# Статус системы
python sdb system status

# Статус ботов
python sdb bot status

# Статус процессов
python sdb process list
```

### 3. Управление конфигурацией

```bash
# Показать конфигурацию
python sdb config show

# Установить значение
python sdb config set "bot.telegram.token=YOUR_TOKEN"

# Экспорт конфигурации
python sdb config export
```

## 📚 Подробная документация

### 🔧 Основные команды

- **[run.md](run.md)** - Запуск системы в различных режимах
- **[bot.md](bot.md)** - Управление Telegram ботом
- **[config.md](config.md)** - Управление конфигурацией системы
- **[system.md](system.md)** - Системные настройки и диагностика
- **[db.md](db.md)** - Управление базой данных

### 💾 Бэкапы

- **[backup.md](backup.md)** - Создание и управление обычными бэкапами
- **[backup_smart.md](backup_smart.md)** - Умные бэкапы с хешированием

### 📦 Модули

- **[module.md](module.md)** - Управление плагинами и расширениями

### 🔄 Процессы

- **[process.md](process.md)** - Мониторинг и управление процессами

### 👥 Пользователи

- **[user.md](user.md)** - Управление пользователями и правами доступа

### 🛠️ Утилиты

- **[utils.md](utils.md)** - Диагностика, очистка, конвертация и другие утилиты

### 🔍 Мониторинг

- **[monitor.md](monitor.md)** - Мониторинг системы в реальном времени
- **[cache.md](cache.md)** - Управление кэшем и производительностью
- **[api.md](api.md)** - Управление API и веб-сервером
- **[dev.md](dev.md)** - Инструменты для разработчиков
- **[tasks.md](tasks.md)** - Управление фоновыми задачами
- **[notifications.md](notifications.md)** - Система уведомлений
- **[security.md](security.md)** - Безопасность и аудит

## 🛡️ Классификация по безопасности

### ❌ Критически опасные команды

Команды, которые могут повредить систему или данные:

```bash
# Удаление данных
python sdb user delete --force
python sdb module uninstall --force
python sdb backup restore --force

# Сброс конфигурации
python sdb config reset
python sdb system reset

# Принудительное завершение
python sdb process kill --force
python sdb bot stop --force
```

### ⚠️ Опасные команды

Команды, которые могут повлиять на работу системы:

```bash
# Перезапуск компонентов
python sdb bot restart
python sdb process restart
python sdb system restart

# Изменение конфигурации
python sdb config set
python sdb config import

# Управление пользователями
python sdb user ban
python sdb user edit --role admin
```

### ✅ Безопасные команды

Команды только для просмотра и мониторинга:

```bash
# Просмотр информации
python sdb system status
python sdb bot status
python sdb user list
python sdb config show

# Мониторинг
python sdb process monitor
python sdb utils diagnose
python sdb utils check
```

## 🔧 Примеры использования

### Управление Telegram ботом

```bash
# Запустить Telegram бота
python sdb bot start

# Проверить статус
python sdb bot status

# Перезапустить бота
python sdb bot restart

# Показать логи
python sdb bot logs --follow
```

### Управление модулями

```bash
# Список модулей
python sdb module list

# Установить модуль
python sdb module install weather

# Обновить модуль
python sdb module update weather

# Включить модуль
python sdb module enable weather
```

### Управление пользователями

```bash
# Список пользователей
python sdb user list

# Создать пользователя
python sdb user create @new_user --platform telegram

# Информация о пользователе
python sdb user info @user_name

# Заблокировать пользователя
python sdb user ban @user_name --reason "Нарушение правил"
```

### Системное администрирование

```bash
# Диагностика системы
python sdb utils diagnose

# Очистка временных файлов
python sdb utils cleanup --temp

# Проверка целостности
python sdb utils check --all

# Создать бэкап
python sdb backup create --name "before_update"
```

## 🚨 Устранение проблем

### Система не запускается

```bash
# Проверить статус
python sdb system status

# Диагностика
python sdb utils diagnose

# Проверить конфигурацию
python sdb config show

# Запустить в режиме отладки
python sdb run debug
```

### Telegram бот не отвечает

```bash
# Проверить статус бота
python sdb bot status

# Перезапустить бота
python sdb bot restart

# Проверить логи
python sdb bot logs --level ERROR

# Тест подключения
python sdb bot test
```

### Проблемы с базой данных

```bash
# Проверить БД
python sdb db status

# Создать бэкап
python sdb backup create

# Восстановить из бэкапа
python sdb backup restore backup_name

# Оптимизировать БД
python sdb db optimize
```

## 📊 Мониторинг производительности

```bash
# Мониторинг процессов
python sdb process monitor

# Мониторинг системы
python sdb utils monitor

# Анализ производительности
python sdb process analyze

# Бенчмарки
python sdb utils benchmark
```

## 🔐 Безопасность

### Рекомендации

1. **Регулярные бэкапы**: Создавайте бэкапы перед важными изменениями
2. **Мониторинг**: Следите за активностью системы
3. **Логирование**: Анализируйте логи для выявления проблем
4. **Обновления**: Регулярно обновляйте систему и модули
5. **Права доступа**: Ограничивайте доступ к критическим командам

### Аудит безопасности

```bash
# Проверка безопасности
python sdb security audit

# Проверка прав доступа
python sdb user permissions --list

# Мониторинг активности
python sdb user activity --detailed
```

## 📈 Рекомендации по использованию

### Для разработчиков

1. Используйте `python sdb run dev` для разработки
2. Включите отладку: `python sdb run debug`
3. Мониторьте производительность: `python sdb process monitor`
4. Тестируйте модули: `python sdb module test`

### Для администраторов

1. Регулярно проверяйте статус: `python sdb system status`
2. Создавайте бэкапы: `python sdb backup create`
3. Мониторьте пользователей: `python sdb user activity`
4. Анализируйте логи: `python sdb system logs`

### Для операторов

1. Используйте мониторинг: `python sdb utils monitor`
2. Проверяйте процессы: `python sdb process list`
3. Управляйте бэкапами: `python sdb backup list`
4. Диагностируйте проблемы: `python sdb utils diagnose`

## 🤝 Поддержка

Если у вас возникли проблемы с CLI командами:

1. Проверьте документацию конкретной команды
2. Выполните диагностику: `python sdb utils diagnose`
3. Проверьте логи: `python sdb system logs`
4. Обратитесь к разделу "Устранение проблем" в соответствующей документации

## 📝 Примечания

- Все команды поддерживают флаг `--help` для получения справки
- Используйте `--json` для машинно-читаемого вывода
- Добавьте `--verbose` для подробной информации
- Флаг `--dry-run` покажет что будет сделано без выполнения

---

**Версия документации**: 1.0.0  
**Последнее обновление**: 2024-01-15  
**Статус**: ✅ Полная документация готова 