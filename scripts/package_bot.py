#!/usr/bin/env python3
"""
Скрипт для упаковки SwiftDevBot в архив для развертывания на новом сервере
Создает готовый к запуску пакет без персональных данных и кеша
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
import json
import yaml

class BotPackager:
    """Упаковщик бота для развертывания"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.package_name = f"SwiftDevBot_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.temp_dir = self.project_root / "temp_package"
        self.output_dir = self.project_root / "deploy_packages"
        
        # Файлы и папки для исключения
        self.exclude_patterns = {
            # Персональные данные и конфиги
            'config.yaml',
            'config.yml', 
            '.env',
            '*.env',
            
            # Данные проекта
            'project_data/',
            'project_data/*',
            
            # Кеш и временные файлы
            '__pycache__/',
            '*.pyc',
            '*.pyo',
            '.pytest_cache/',
            'temp_package/',
            'deploy_packages/',
            'nohup.out',
            
            # Git и IDE
            '.git/',
            '.gitignore',
            '.vscode/',
            '.idea/',
            '*.swp',
            '*.swo',
            
            # Логи
            '*.log',
            'logs/',
            
            # Виртуальное окружение
            '.venv/',
            'venv/',
            'env/',
            
            # Резервные копии
            '*.bak',
            '*.backup',
            '*~',
            
            # Тестовые и отладочные файлы
            'test_*.py',
            '*_test.py',
            'debug_*.py',
            'demo_*.py',
            'quick_test.py',
            'check_*.py',
            'fix_*.py',
            'sync_*.py',
            'create_table.py',
            'simple_rbac_test.py',
            'test_integration.py',
            'test_web_server.py',
            'tests/',
            
            # Документация разработки (оставляем только основную)
            '*_REPORT.md',
            '*_GUIDE.md',
            '*_ADDED.md',
            '*_CHANGES.md',
            '*_FIXES.md',
            '*_IMPROVEMENTS.md',
            '*_COMPLETE.md',
            '*_UPDATE.md',
            '*_STATUS*.md',
            '*_RESULTS.md',
            'FINAL_*.md',
            'FIXES_*.md',
            'IMPROVEMENTS_*.md',
            'DEVELOPMENT_*.md',
            'МОДУЛИ_*.md',
            'YOUTUBE_*.md',
            'CALLBACK_*.md',
            'CLI_*.md',
            'PROJECT_*.md',
            'TEST_*.md',
            'Docs/',
            'docs/',
            
            # Другие временные файлы
            '.DS_Store',
            'Thumbs.db',
            '*.tmp',
            '*.temp',
            '.python-version'
        }
        
        # Обязательные файлы для проверки
        self.required_files = [
            'run_bot.py',
            'sdb.py', 
            'requirements.txt',
            'README.md',
            'alembic.ini',
            'babel.cfg'
        ]
        
        # Файлы для создания шаблонов
        self.template_files = {
            'config.yaml': 'config.template.yaml',
            '.env': '.env.template'
        }
    
    def create_package(self, format_type: str = 'zip') -> str:
        """Создает пакет для развертывания"""
        print(f"🚀 Начинаю упаковку SwiftDevBot...")
        print(f"📁 Проект: {self.project_root}")
        print(f"📦 Пакет: {self.package_name}")
        
        try:
            # Подготовка
            self._prepare_directories()
            self._check_required_files()
            
            # Копирование файлов
            self._copy_project_files()
            self._create_template_configs()
            self._create_deployment_scripts()
            self._create_readme()
            
            # Создание архива
            archive_path = self._create_archive(format_type)
            
            # Очистка
            self._cleanup()
            
            print(f"✅ Пакет готов: {archive_path}")
            print(f"📊 Размер: {self._get_file_size(archive_path)}")
            
            return str(archive_path)
            
        except Exception as e:
            print(f"❌ Ошибка упаковки: {e}")
            self._cleanup()
            return None
    
    def _prepare_directories(self):
        """Подготавливает директории"""
        # Удаляем старую временную папку
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        # Создаем директории
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"📁 Временная папка: {self.temp_dir}")
    
    def _check_required_files(self):
        """Проверяет наличие обязательных файлов"""
        missing = []
        for file in self.required_files:
            if not (self.project_root / file).exists():
                missing.append(file)
        
        if missing:
            raise FileNotFoundError(f"Отсутствуют обязательные файлы: {missing}")
        
        print("✅ Все обязательные файлы найдены")
    
    def _should_exclude(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить файл/папку"""
        rel_path = path.relative_to(self.project_root)
        
        for pattern in self.exclude_patterns:
            if self._match_pattern(str(rel_path), pattern):
                return True
        
        return False
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Проверяет соответствие пути паттерну"""
        import fnmatch
        
        # Прямое совпадение
        if path == pattern or path == pattern.rstrip('/'):
            return True
        
        # Wildcard паттерны
        if '*' in pattern:
            if fnmatch.fnmatch(path, pattern):
                return True
        
        # Паттерны директорий
        if pattern.endswith('/'):
            if path.startswith(pattern) or path.startswith(pattern.rstrip('/')):
                return True
        
        return False
    
    def _copy_project_files(self):
        """Копирует файлы проекта"""
        print("📋 Копирую файлы проекта...")
        
        copied_count = 0
        excluded_count = 0
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Проверяем директорию
            if self._should_exclude(root_path):
                dirs.clear()  # Не обходим поддиректории
                excluded_count += 1
                continue
            
            # Создаем соответствующую директорию
            rel_dir = root_path.relative_to(self.project_root)
            target_dir = self.temp_dir / rel_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем файлы
            for file in files:
                file_path = root_path / file
                
                if self._should_exclude(file_path):
                    excluded_count += 1
                    continue
                
                # Дополнительная проверка для файлов миграций
                if file_path.name.endswith('.py') and 'alembic_migrations/versions' in str(file_path):
                    if file_path.stat().st_size == 0:  # Пустой файл
                        excluded_count += 1
                        continue
                    
                    # Проверяем наличие revision в файле миграции
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content and 'revision:' not in content and 'revision =' not in content:
                                excluded_count += 1
                                continue
                    except:
                        excluded_count += 1
                        continue
                
                target_path = target_dir / file
                shutil.copy2(file_path, target_path)
                copied_count += 1
        
        print(f"✅ Скопировано файлов: {copied_count}")
        print(f"🚫 Исключено файлов: {excluded_count}")
    
    def _create_template_configs(self):
        """Создает шаблоны конфигурационных файлов"""
        print("⚙️ Создаю шаблоны конфигураций...")
        
        # Шаблон config.yaml
        config_template = {
            'bot': {
                'token': 'YOUR_BOT_TOKEN_HERE',
                'username': 'your_bot_username'
            },
            'admin': {
                'super_admin_telegram_id': 123456789,  # ОБЯЗАТЕЛЬНО! Ваш Telegram ID
                'auto_create_super_admin': True
            },
            'database': {
                'url': 'sqlite:///project_data/Database_files/sdb.db',
                'echo': False
            },
            'cache': {
                'backend': 'memory',
                'ttl': 3600
            },
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'console_logging': True
            },
            'features': {
                'web_download_server': {
                    'enabled': True,
                    'host': '0.0.0.0',
                    'port': 8080,
                    'external_host': 'YOUR_EXTERNAL_IP_HERE',
                    'external_port': 8080
                }
            }
        }
        
        config_path = self.temp_dir / 'config.template.yaml'
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_template, f, default_flow_style=False, allow_unicode=True)
        
        # Шаблон .env
        env_template = """# SwiftDevBot Environment Variables
# Скопируйте этот файл в .env и заполните значения

# Токен Telegram бота (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# СУПЕР АДМИНИСТРАТОР (ОБЯЗАТЕЛЬНО!)
SUPER_ADMIN_TELEGRAM_ID=123456789

# База данных (оставьте как есть для SQLite)
DATABASE_URL=sqlite:///project_data/Database_files/sdb.db

# Внешний IP для веб-сервера скачивания (ваш публичный IP или домен)
EXTERNAL_HOST=your_external_ip_here

# Опциональные настройки
DEBUG=False
LOG_LEVEL=INFO
"""
        
        env_path = self.temp_dir / '.env.template'
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        print("✅ Шаблоны конфигураций созданы")
    
    def _create_deployment_scripts(self):
        """Создает скрипты для развертывания"""
        print("📜 Создаю скрипты развертывания...")
        
        # Скрипт установки для Linux
        install_script = """#!/bin/bash
# SwiftDevBot Installation Script

set -e

echo "🚀 Установка SwiftDevBot..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+"
    exit 1
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv .venv
source .venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
echo "⬇️ Установка зависимостей..."
pip install -r requirements.txt

# Создание структуры папок
echo "📁 Создание структуры проекта..."
mkdir -p project_data/{Database_files,Logs,Cache_data,core_backups,module_backups}

# Копирование конфигурации
if [ ! -f config.yaml ]; then
    if [ -f config.template.yaml ]; then
        cp config.template.yaml config.yaml
        echo "⚙️ Скопирован config.template.yaml -> config.yaml"
        echo "❗ ОБЯЗАТЕЛЬНО отредактируйте config.yaml с вашими настройками!"
    fi
fi

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."
python -m alembic upgrade head

echo "✅ Установка завершена!"
echo ""
echo "📋 Что дальше:"
echo "1. Отредактируйте config.yaml - укажите токен бота и другие настройки"
echo "2. Запустите бота: python run_bot.py"
echo ""
echo "📖 Подробности в README.md"
"""
        
        install_path = self.temp_dir / 'install.sh'
        with open(install_path, 'w', encoding='utf-8') as f:
            f.write(install_script)
        os.chmod(install_path, 0o755)
        
        # Скрипт для Windows
        install_bat = """@echo off
REM SwiftDevBot Installation Script for Windows

echo 🚀 Установка SwiftDevBot...

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)

REM Создание виртуального окружения
echo 📦 Создание виртуального окружения...
python -m venv .venv
call .venv\\Scripts\\activate.bat

REM Обновление pip
python -m pip install --upgrade pip

REM Установка зависимостей
echo ⬇️ Установка зависимостей...
pip install -r requirements.txt

REM Создание структуры папок
echo 📁 Создание структуры проекта...
if not exist "project_data" mkdir project_data
if not exist "project_data\\Database_files" mkdir project_data\\Database_files
if not exist "project_data\\Logs" mkdir project_data\\Logs
if not exist "project_data\\Cache_data" mkdir project_data\\Cache_data
if not exist "project_data\\core_backups" mkdir project_data\\core_backups
if not exist "project_data\\module_backups" mkdir project_data\\module_backups

REM Копирование конфигурации
if not exist "config.yaml" (
    if exist "config.template.yaml" (
        copy config.template.yaml config.yaml
        echo ⚙️ Скопирован config.template.yaml -^> config.yaml
        echo ❗ ОБЯЗАТЕЛЬНО отредактируйте config.yaml с вашими настройками!
    )
)

REM Инициализация базы данных
echo 🗄️ Инициализация базы данных...
python -m alembic upgrade head

echo ✅ Установка завершена!
echo.
echo 📋 Что дальше:
echo 1. Отредактируйте config.yaml - укажите токен бота и другие настройки
echo 2. Запустите бота: python run_bot.py
echo.
echo 📖 Подробности в README.md
pause
"""
        
        install_bat_path = self.temp_dir / 'install.bat'
        with open(install_bat_path, 'w', encoding='utf-8') as f:
            f.write(install_bat)
        
        # Скрипт запуска
        start_script = """#!/bin/bash
# SwiftDevBot Start Script

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "❌ Виртуальное окружение не найдено. Запустите сначала install.sh"
    exit 1
fi

echo "🚀 Запуск SwiftDevBot..."
source .venv/bin/activate
python run_bot.py
"""
        
        start_path = self.temp_dir / 'start.sh'
        with open(start_path, 'w', encoding='utf-8') as f:
            f.write(start_script)
        os.chmod(start_path, 0o755)
        
        # Скрипт запуска для Windows
        start_bat = """@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo ❌ Виртуальное окружение не найдено. Запустите сначала install.bat
    pause
    exit /b 1
)

echo 🚀 Запуск SwiftDevBot...
call .venv\\Scripts\\activate.bat
python run_bot.py
pause
"""
        
        start_bat_path = self.temp_dir / 'start.bat'
        with open(start_bat_path, 'w', encoding='utf-8') as f:
            f.write(start_bat)
        
        print("✅ Скрипты развертывания созданы")
    
    def _create_readme(self):
        """Создает README для развертывания"""
        readme_content = f"""# SwiftDevBot - Готовый к развертыванию пакет

Этот пакет содержит полностью готовый к развертыванию SwiftDevBot.

## 🚀 Быстрый старт

### Linux/macOS:
```bash
# Распаковать архив
unzip {self.package_name}.zip
cd {self.package_name}

# Установить и настроить
chmod +x install.sh
./install.sh

# Отредактировать конфигурацию
nano config.yaml

# Запустить бота
./start.sh
```

### Windows:
```cmd
REM Распаковать архив и перейти в папку
cd {self.package_name}

REM Установить и настроить
install.bat

REM Отредактировать config.yaml в любом текстовом редакторе

REM Запустить бота
start.bat
```

## ⚙️ Настройка

### 1. Получение токена бота
1. Напишите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте полученный токен

### 2. Настройка config.yaml
Откройте файл `config.yaml` и заполните:
- `bot.token` - токен вашего бота
- `features.web_download_server.external_host` - ваш внешний IP адрес

### 3. Настройка портов (опционально)
Если нужен другой порт для веб-сервера скачивания:
- Измените `features.web_download_server.port` в config.yaml
- Откройте порт в файрволе

## 🔧 Системные требования

- Python 3.8 или выше
- 500+ МБ свободного места
- Доступ в интернет
- Открытый порт 8080 (или другой настроенный) для веб-сервера

## 📁 Структура проекта

- `core/` - Основные компоненты бота
- `modules/` - Модули функциональности (YouTube downloader и др.)
- `project_data/` - Данные проекта (БД, логи, кеш)
- `config.yaml` - Главный файл конфигурации
- `requirements.txt` - Python зависимости

## 🎯 Возможности

- ✅ Скачивание видео с YouTube
- ✅ Веб-сервер для больших файлов
- ✅ Система ролей и разрешений  
- ✅ Модульная архитектура
- ✅ Система кеширования
- ✅ Логирование и мониторинг

## 🛠️ Команды управления

Администраторские команды доступны в боте:
- `/admin` - Панель администратора
- `/modules` - Управление модулями
- `/users` - Управление пользователями

## 🆘 Поддержка

При проблемах:
1. Проверьте логи в `project_data/Logs/`
2. Убедитесь что токен бота корректный
3. Проверьте доступность портов

## 📋 Changelog

Версия пакета: {datetime.now().strftime('%Y.%m.%d')}
Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}

---
🤖 SwiftDevBot - Telegram бот для YouTube с веб-интерфейсом
"""
        
        readme_path = self.temp_dir / 'DEPLOY_README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ README для развертывания создан")
    
    def _create_archive(self, format_type: str) -> Path:
        """Создает архив"""
        print(f"📦 Создание архива в формате {format_type}...")
        
        if format_type == 'zip':
            archive_path = self.output_dir / f"{self.package_name}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arc_name = file_path.relative_to(self.temp_dir)
                        zipf.write(file_path, arc_name)
        
        elif format_type == 'tar.gz':
            archive_path = self.output_dir / f"{self.package_name}.tar.gz"
            with tarfile.open(archive_path, 'w:gz') as tarf:
                tarf.add(self.temp_dir, arcname=self.package_name)
        
        else:
            raise ValueError(f"Неподдерживаемый формат: {format_type}")
        
        return archive_path
    
    def _cleanup(self):
        """Очищает временные файлы"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _get_file_size(self, file_path: Path) -> str:
        """Возвращает размер файла в читаемом формате"""
        size = file_path.stat().st_size
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ТБ"


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Упаковка SwiftDevBot для развертывания')
    parser.add_argument('--format', choices=['zip', 'tar.gz'], default='zip',
                       help='Формат архива (по умолчанию: zip)')
    parser.add_argument('--project-root', type=str,
                       help='Путь к корню проекта (по умолчанию: текущая папка)')
    
    args = parser.parse_args()
    
    try:
        packager = BotPackager(args.project_root)
        result = packager.create_package(args.format)
        
        if result:
            print("\n🎉 Упаковка завершена успешно!")
            print(f"📦 Файл: {result}")
            print("\n📋 Инструкции по развертыванию:")
            print("1. Скопируйте архив на целевой сервер")
            print("2. Распакуйте архив")
            print("3. Запустите install.sh (Linux/macOS) или install.bat (Windows)")
            print("4. Отредактируйте config.yaml")
            print("5. Запустите start.sh или start.bat")
        else:
            print("\n❌ Упаковка не удалась")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Упаковка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
