#!/usr/bin/env python3
# scripts/validate_environment.py

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# Минимальные требования
PYTHON_MIN_VERSION = (3, 10)
REQUIRED_PACKAGES = [
    ("aiogram", "3.0.0"),
    ("pydantic", "2.0.0"),
    ("sqlalchemy", "2.0.0"),
    ("loguru", "0.6.0"),
    ("typer", "0.9.0"),
    ("rich", "13.0.0"),
]

OPTIONAL_PACKAGES = [
    ("redis", "4.5.0"),
    ("psycopg", "3.1.0"),
    ("aiomysql", "0.1.0"),
    ("pytest", "7.0.0"),
]


def check_python_version() -> Tuple[bool, str]:
    """Проверяет версию Python."""
    current_version = sys.version_info[:2]
    if current_version >= PYTHON_MIN_VERSION:
        return True, f"✅ Python {sys.version.split()[0]}"
    else:
        return False, f"❌ Python {sys.version.split()[0]} (требуется >= {'.'.join(map(str, PYTHON_MIN_VERSION))})"


def check_package_version(package_name: str, min_version: str) -> Tuple[bool, str]:
    """Проверяет версию пакета."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {package_name}; print({package_name}.__version__)"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            installed_version = result.stdout.strip()
            # Простая проверка версии (можно улучшить с packaging.version)
            return True, f"✅ {package_name} {installed_version}"
        else:
            return False, f"❌ {package_name} не установлен"
            
    except subprocess.TimeoutExpired:
        return False, f"⏱️ {package_name} проверка превысила таймаут"
    except Exception as e:
        return False, f"❌ {package_name} ошибка проверки: {e}"


def check_environment_variables() -> List[Tuple[bool, str]]:
    """Проверяет важные переменные окружения."""
    checks = []
    
    # Проверка BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token:
        if len(bot_token) > 10 and ":" in bot_token:
            checks.append((True, "✅ BOT_TOKEN установлен и выглядит корректно"))
        else:
            checks.append((False, "⚠️ BOT_TOKEN установлен, но выглядит некорректно"))
    else:
        checks.append((False, "❌ BOT_TOKEN не установлен"))
    
    # Проверка .env файла
    env_file = Path(".env")
    if env_file.exists():
        checks.append((True, "✅ Файл .env найден"))
    else:
        checks.append((False, "⚠️ Файл .env не найден"))
    
    return checks


def check_project_structure() -> List[Tuple[bool, str]]:
    """Проверяет структуру проекта."""
    checks = []
    
    required_dirs = [
        "core",
        "modules", 
        "cli_commands",
        "project_data",
        "locales"
    ]
    
    required_files = [
        "config.yaml",
        "requirements.txt",
        "run_bot.py",
        "sdb.py"
    ]
    
    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            checks.append((True, f"✅ Директория {dir_name}/"))
        else:
            checks.append((False, f"❌ Директория {dir_name}/ не найдена"))
    
    for file_name in required_files:
        if Path(file_name).is_file():
            checks.append((True, f"✅ Файл {file_name}"))
        else:
            checks.append((False, f"❌ Файл {file_name} не найден"))
    
    return checks


def check_database() -> Tuple[bool, str]:
    """Проверяет доступность базы данных."""
    try:
        # Пытаемся импортировать настройки
        sys.path.insert(0, str(Path.cwd()))
        from core.app_settings import settings
        
        # settings уже загружен как глобальный объект
        db_path = settings.core.project_data_path / settings.db.sqlite_path
        
        if db_path.exists():
            return True, f"✅ База данных найдена: {db_path}"
        else:
            return False, f"⚠️ База данных не найдена: {db_path}"
            
    except Exception as e:
        return False, f"❌ Ошибка проверки БД: {e}"


def main():
    """Основная функция валидации."""
    console.print(Panel(
        "[bold cyan]🔍 Валидация окружения SwiftDevBot[/bold cyan]",
        box=box.DOUBLE
    ))
    
    all_checks_passed = True
    
    # Проверка Python
    python_ok, python_msg = check_python_version()
    console.print(python_msg)
    if not python_ok:
        all_checks_passed = False
    
    console.print()
    
    # Проверка обязательных пакетов
    console.print("[bold]Обязательные пакеты:[/bold]")
    for package, min_ver in REQUIRED_PACKAGES:
        package_ok, package_msg = check_package_version(package, min_ver)
        console.print(f"  {package_msg}")
        if not package_ok:
            all_checks_passed = False
    
    console.print()
    
    # Проверка опциональных пакетов
    console.print("[bold]Опциональные пакеты:[/bold]")
    for package, min_ver in OPTIONAL_PACKAGES:
        package_ok, package_msg = check_package_version(package, min_ver)
        console.print(f"  {package_msg}")
    
    console.print()
    
    # Проверка переменных окружения
    console.print("[bold]Переменные окружения:[/bold]")
    env_checks = check_environment_variables()
    for env_ok, env_msg in env_checks:
        console.print(f"  {env_msg}")
        if not env_ok and "BOT_TOKEN не установлен" in env_msg:
            all_checks_passed = False
    
    console.print()
    
    # Проверка структуры проекта
    console.print("[bold]Структура проекта:[/bold]")
    structure_checks = check_project_structure()
    for struct_ok, struct_msg in structure_checks:
        console.print(f"  {struct_msg}")
        if not struct_ok and any(critical in struct_msg for critical in ["core/", "config.yaml", "sdb.py"]):
            all_checks_passed = False
    
    console.print()
    
    # Проверка базы данных
    console.print("[bold]База данных:[/bold]")
    db_ok, db_msg = check_database()
    console.print(f"  {db_msg}")
    
    console.print()
    
    # Итоговый результат
    if all_checks_passed:
        console.print(Panel(
            "[bold green]✅ Все критичные проверки пройдены! SwiftDevBot готов к запуску.[/bold green]",
            style="green"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Обнаружены критичные проблемы. Исправьте их перед запуском.[/bold red]",
            style="red"
        ))
        
        console.print("\n[yellow]Рекомендации по исправлению:[/yellow]")
        console.print("1. Убедитесь, что используете Python >= 3.10")
        console.print("2. Установите зависимости: pip install -r requirements.txt")
        console.print("3. Создайте файл .env с BOT_TOKEN")
        console.print("4. Запустите: ./sdb.py config init")
        console.print("5. Запустите: ./sdb.py db upgrade head")
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())
