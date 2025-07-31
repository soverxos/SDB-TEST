# 🚀 SwiftDevBot

> Современная модульная платформа для создания Telegram ботов на Python

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://aiogram.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ⚡ Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>
cd SwiftDevBot

# Установка зависимостей
pip install -r requirements.txt

# Инициализация конфигурации
./sdb.py config init

# Настройка чувствительных данных (опционально)
./sdb.py setup-env

# Запуск бота
./sdb.py start
```

## 📚 Документация

Полная документация находится в папке [`Docs/`](Docs/):

- **[Docs/INDEX.md](Docs/INDEX.md)** - 📋 Главная страница документации с навигацией
- **[Docs/Modules/QUICK_START.md](Docs/Modules/QUICK_START.md)** - 🚀 Создание модуля за 5 минут
- **[Docs/Development/DEVELOPMENT_GUIDE.md](Docs/Development/DEVELOPMENT_GUIDE.md)** - 🛠️ Руководство разработчика
- **[Docs/Reports/FINAL_STATUS.md](Docs/Reports/FINAL_STATUS.md)** - 📊 Текущий статус проекта

### 📂 Разделы документации
- **[Modules/](Docs/Modules/)** - 🧩 Разработка модулей
- **[Development/](Docs/Development/)** - 🛠️ Руководства разработчика  
- **[Reports/](Docs/Reports/)** - 📊 Отчеты и статусы
- **[Guides/](Docs/Guides/)** - 📖 Руководства пользователя
- **[Architecture/](Docs/Architecture/)** - 🏗️ Архитектура системы

## 🎯 Основные возможности

- 🏗️ **Модульная архитектура** - легкое расширение функциональности
- 🔧 **CLI управление** - полный контроль через командную строку  
- 🗄️ **Гибкая БД** - поддержка SQLite, PostgreSQL, MySQL
- 👥 **RBAC система** - управление правами и ролями
- 🌍 **Интернационализация** - поддержка множества языков
- 📊 **Мониторинг** - встроенные системы отслеживания производительности

## 🧩 Активные модули

- **� Notes Manager** - система управления заметками с CRUD операциями
- **🌟 Example Module** - демонстрационный модуль с FSM и UI

Подробнее о модулях: [`Docs/Modules/MODULES_OVERVIEW.md`](Docs/Modules/MODULES_OVERVIEW.md)

**Хотите создать свой модуль?** → [`Docs/Modules/QUICK_START.md`](Docs/Modules/QUICK_START.md)

## 🛠️ CLI команды

```bash
./sdb.py --help          # Справка по всем командам
./sdb.py config init     # Инициализация конфигурации
./sdb.py setup-env       # Настройка чувствительных данных
./sdb.py status          # Статус бота
./sdb.py start           # Запуск бота
./sdb.py stop            # Остановка бота
./sdb.py restart         # Перезапуск бота

# Управление модулями
./sdb.py module list     # Список модулей
./sdb.py module create   # Создание нового модуля
./sdb.py module enable   # Активация модуля
./sdb.py module disable  # Деактивация модуля
```

## 📂 Структура проекта

```
SwiftDevBot/
├── 📚 Docs/                    # Документация
├── 🔧 cli_commands/            # CLI команды
├── 🏗️ core/                    # Ядро системы
├── 🧩 modules/                 # Модули бота
├── 🗄️ alembic_migrations/      # Миграции БД
├── 🌍 locales/                 # Файлы локализации
├── 📊 project_data/            # Данные проекта
├── 🧪 tests/                   # Тесты
└── 📝 scripts/                 # Утилиты
```

## 🚦 Статус проекта

**✅ Production Ready** - Проект готов к полноценному использованию!

- ✅ Все основные функции реализованы
- ✅ Комплексное тестирование пройдено
- ✅ Документация завершена
- ✅ Системы мониторинга настроены

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Смотрите [DEVELOPMENT_GUIDE.md](Docs/DEVELOPMENT_GUIDE.md) для получения инструкций.

## 🔒 Безопасность

### Чувствительные данные
Проект использует безопасную двухуровневую систему конфигурации:

- **`.env`** - чувствительные данные (токены, ID администраторов, пароли БД)
- **`config.yaml`** - настраиваемые параметры (логирование, модули, интерфейс)

### Настройка безопасности
```bash
# Инициализация конфигурации (создает config.yaml)
./sdb.py config init

# Создание .env файла с чувствительными данными
./sdb.py setup-env

# Файл .env автоматически добавляется в .gitignore
# НЕ КОММИТЬТЕ .env файл в репозиторий!
```

### Переменные окружения
Основные переменные в `.env`:
- `BOT_TOKEN` - токен Telegram бота
- `SUPER_ADMIN_IDS` - ID супер-администраторов (через запятую)
- `DB_PG_DSN` / `DB_MYSQL_DSN` - строки подключения к БД
- `REDIS_URL` - URL для Redis кэша

### Управление конфигурацией
```bash
# Обновить конфигурацию с новыми параметрами
./sdb.py config init

# Синхронизировать с .env и config.yaml
./sdb.py config init --update-env

# Просмотреть текущую конфигурацию
./sdb.py config info

# Красивый вывод конфигурации (по умолчанию)
./sdb.py config info

# Компактный вывод
./sdb.py config info --compact

# Сырой вывод в YAML/JSON
./sdb.py config info --format yaml
./sdb.py config info --format json
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

---

*Для получения полной информации посетите [документацию](Docs/INDEX.md)*
