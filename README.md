# 🚀 SwiftDevBot-Lite

**Мощная система управления ботом с расширенными возможностями безопасности и мониторинга**

## 📋 Обзор

SwiftDevBot-Lite - это комплексная система для управления Telegram ботом с богатым набором CLI команд, системой безопасности, мониторингом и модульной архитектурой.

## ✨ Основные возможности

### 🤖 **Telegram Bot**
- Полноценный бот с aiogram 3.x
- Система навигации и меню
- Админ-панель с управлением пользователями
- Система ролей и разрешений

### 🛠️ **CLI Команды**
- **Управление конфигурацией** (`config`)
- **База данных** (`db`) - миграции, бэкапы
- **Модули** (`module`) - установка, управление
- **Пользователи** (`user`) - роли, разрешения
- **Бэкапы** (`backup`) - умные бэкапы
- **Система** (`system`) - статус, обновления
- **Бот** (`bot`) - управление ботом
- **Мониторинг** (`monitor`) - метрики, алерты
- **Утилиты** (`utils`) - диагностика, очистка
- **Безопасность** (`security`) - аудит, интеграции

### 🔒 **Система безопасности**
- **Интеграции с внешними сервисами**:
  - VirusTotal - сканирование файлов и URL
  - Shodan - информация о хостах
  - AbuseIPDB - проверка вредоносных IP
  - SecurityTrails - информация о доменах
- **Локальные сканеры**:
  - Nmap - сетевой сканер
  - SSLyze/OpenSSL - SSL анализ
- **Адаптивность к окружению** (контейнеры/ОС)

### 📊 **Мониторинг**
- Системные метрики
- Мониторинг производительности
- Логирование и алерты
- Дашборды и отчеты

## 🚀 Быстрый старт

### 1. Установка
```bash
# Клонирование
git clone <repository>
cd SwiftDevBot-Lite

# Виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows

# Зависимости
pip install -r requirements.txt
```

### 2. Настройка
```bash
# Инициализация конфигурации
python sdb.py config init

# Настройка базы данных
python sdb.py db upgrade

# Запуск бота
python sdb.py run
```

### 3. Основные команды
```bash
# Управление модулями
python sdb.py module list
python sdb.py module enable module_name

# Пользователи
python sdb.py user list
python sdb.py user assign-role user_id admin

# Безопасность
python sdb.py security integrations system-info
python sdb.py security integrations nmap --target example.com

# Мониторинг
python sdb.py monitor status
python sdb.py monitor dashboard
```

## 📁 Структура проекта

```
SwiftDevBot-Lite/
├── 📁 core/                 # Ядро системы
├── 📁 cli/                  # CLI команды
├── 📁 modules/              # Модули системы
├── 📁 tests/                # Тесты
├── 📁 Docs/                 # Документация
│   ├── 📁 Reports/          # Отчеты
│   ├── 📁 Guides/           # Руководства
│   └── 📁 API/              # API документация
├── 📁 config/               # Конфигурация
├── 📁 scripts/              # Скрипты
├── 📁 backup/               # Бэкапы
├── 📁 alembic_migrations/   # Миграции БД
├── 📁 locales/              # Локализация
├── 📁 project_data/         # Данные проекта
├── 📄 sdb.py                # Главный CLI
├── 📄 run_bot.py            # Запуск бота
├── 📄 requirements.txt       # Зависимости
└── 📄 README.md             # Этот файл
```

## 🔧 Конфигурация

### Основные файлы
- `.env` - переменные окружения
- `config.yaml` - основная конфигурация
- `config/security_integrations.json` - интеграции безопасности

### Переменные окружения
```bash
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=sqlite:///sdb.db
LOG_LEVEL=INFO
```

## 📚 Документация

### 📖 Руководства
- [Быстрый старт безопасности](Docs/Guides/SECURITY_INTEGRATIONS_QUICK_START.md)
- [Полное руководство по безопасности](Docs/Guides/SECURITY_INTEGRATIONS.md)

### 📊 Отчеты
- [Проектный чек-лист](Docs/Reports/PROJECT_CHECKLIST.md)
- [Отчеты CLI команд](Docs/Reports/)

### 🧪 Тестирование
```bash
# Запуск тестов
python -m pytest tests/

# Тестирование CLI
python tests/quick_test_commands.py
```

## 🛡️ Безопасность

### Интеграции
```bash
# Настройка API ключей
python sdb.py security integrations config --service virustotal --api-key YOUR_KEY

# Сканирование
python sdb.py security integrations nmap --target example.com
python sdb.py security integrations comprehensive --target example.com
```

### Рекомендации
1. Храните API ключи в переменных окружения
2. Регулярно обновляйте зависимости
3. Мониторьте логи и алерты
4. Используйте HTTPS для внешних соединений

## 🔄 Разработка

### Добавление модулей
```bash
# Создание модуля
python sdb.py module create my_module

# Установка из репозитория
python sdb.py module install module_name
```

### CLI команды
```bash
# Создание новой команды
# См. примеры в cli/ directory
```

## 📈 Мониторинг

### Системные метрики
```bash
python sdb.py monitor status
python sdb.py monitor metrics
python sdb.py monitor dashboard
```

### Логирование
- Автоматическая ротация логов
- Различные уровни логирования
- Структурированные логи

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для фичи
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

[Укажите лицензию]

## 🆘 Поддержка

- **Issues**: [GitHub Issues](link)
- **Документация**: [Docs/](Docs/)
- **Телеграм**: [@your_bot](https://t.me/your_bot)

---

**🎉 SwiftDevBot-Lite - мощная система управления ботом с расширенными возможностями!**

*Версия: 1.0.0 | Последнее обновление: 2025-08-01* 