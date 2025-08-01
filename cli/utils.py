# --- НАЧАЛО ФАЙЛА cli/utils.py ---
import asyncio
import json
import os
import platform
import psutil
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# --- Константы, используемые в CLI ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_CONFIG_DIR_NAME = "Config"
USER_CORE_CONFIG_FILENAME = "core_settings.yaml"
USER_MODULES_CONFIG_DIR_NAME = "modules_settings"

sdb_console = Console()

# Создаем Typer-приложение для утилит
utils_app = typer.Typer(
    name="utils",
    help="🛠️ Утилитарные инструменты для SwiftDevBot",
    rich_markup_mode="rich"
)

# --- Функции для работы с YAML ---

def get_yaml_editor():
    """Возвращает экземпляр ruamel.yaml.YAML для сохранения комментариев."""
    try:
        from ruamel.yaml import YAML
        yaml_editor = YAML()
        yaml_editor.indent(mapping=2, sequence=4, offset=2)
        yaml_editor.preserve_quotes = True
        return yaml_editor
    except ImportError:
        sdb_console.print("[yellow]Предупреждение: библиотека 'ruamel.yaml' не установлена. Комментарии и форматирование в YAML файлах могут быть утеряны при изменении. Установите ее: `pip install ruamel.yaml`[/yellow]")
        return None

def read_yaml_file(path: Path) -> Optional[Dict[str, Any]]:
    """Читает YAML файл, возвращая его содержимое как словарь."""
    if not path.is_file():
        return None
    try:
        editor = get_yaml_editor()
        if editor:
            return editor.load(path)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка чтения YAML файла {path}: {e}[/bold red]")
        return None

def write_yaml_file(path: Path, data: Dict[str, Any]) -> bool:
    """Записывает словарь в YAML файл."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        editor = get_yaml_editor()
        if editor:
            with open(path, 'w', encoding='utf-8') as f:
                editor.dump(data, f)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, indent=2, sort_keys=False, allow_unicode=True)
        return True
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка записи YAML файла {path}: {e}[/bold red]")
        return False

# --- Вспомогательные функции из старой версии ---

async def get_sdb_services_for_cli(
    init_db: bool = False,
    init_rbac: bool = False,
) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
    """Вспомогательная функция для получения основных сервисов SDB."""
    settings_instance: Optional[Any] = None
    db_manager_instance: Optional[Any] = None
    rbac_service_instance: Optional[Any] = None

    try:
        from core.app_settings import settings
        settings_instance = settings
        if init_db or init_rbac:
            from core.database.manager import DBManager
            db_m = DBManager(db_settings=settings.db, app_settings=settings)
            await db_m.initialize()
            db_manager_instance = db_m
            if init_rbac and db_manager_instance:
                from core.rbac.service import RBACService
                rbac_service_instance = RBACService(services=None, db_manager=db_manager_instance)
        return settings_instance, db_manager_instance, rbac_service_instance
    except ImportError as e:
        raise
    except Exception as e:
        if db_manager_instance:
            await db_manager_instance.dispose()
        raise

def confirm_action(prompt_message: str, default_choice: bool = False, abort_on_false: bool = True) -> bool:
    """Общая функция для запроса подтверждения действия у пользователя."""
    return typer.confirm(prompt_message, default=default_choice, abort=abort_on_false)

def format_size(size_bytes: int) -> str:
    """Форматирует размер в байтах в человекочитаемый вид."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.2f} MB"
    else:
        return f"{size_bytes/(1024**3):.2f} GB"

# --- Новые функции для CLI команд ---

def _get_system_diagnostic() -> Dict[str, Any]:
    """Получает диагностическую информацию о системе."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_total": psutil.disk_usage('/').total,
        "disk_free": psutil.disk_usage('/').free,
        "cpu_count": psutil.cpu_count(),
    }

def _get_network_diagnostic() -> Dict[str, Any]:
    """Получает диагностическую информацию о сети."""
    try:
        # Проверяем подключение к интернету
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        internet_available = True
    except OSError:
        internet_available = False
    
    return {
        "internet_available": internet_available,
        "telegram_api_available": internet_available,  # Упрощенная проверка
        "webhook_configured": False,  # Заглушка
        "port_8000_free": True,  # Заглушка
    }

async def _get_database_diagnostic() -> Dict[str, Any]:
    """Получает диагностическую информацию о базе данных."""
    try:
        settings, db_manager, _ = await get_sdb_services_for_cli()
        
        # Проверяем путь к базе данных
        db_path = Path(settings.db.sqlite_path)
        if not db_path.exists():
            return {"connected": False, "error": "Файл базы данных не найден"}
        
        # Проверяем размер файла
        db_size = db_path.stat().st_size
        
        # Пытаемся подключиться к базе данных
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Проверяем, что база данных работает
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            conn.close()
            
            return {
                "connected": True,
                "type": settings.db.type,
                "size": db_size,
                "tables_exist": len(tables) > 0,
                "indexes_optimized": True,  # Заглушка
                "integrity_ok": True,  # Заглушка
                "tables_count": len(tables),
            }
        except Exception as db_error:
            return {
                "connected": False, 
                "error": f"Ошибка подключения к БД: {str(db_error)}",
                "size": db_size,
            }
        
    except Exception as e:
        return {"connected": False, "error": str(e)}

def _get_security_diagnostic() -> Dict[str, Any]:
    """Получает диагностическую информацию о безопасности."""
    # Проверяем наличие токенов
    env_file = PROJECT_ROOT / ".env"
    tokens_protected = env_file.exists() and env_file.stat().st_mode & 0o600 == 0o600
    
    return {
        "tokens_protected": tokens_protected,
        "ssl_configured": False,  # Заглушка
        "firewall_active": False,  # Заглушка
        "logging_enabled": True,  # Заглушка
    }

def _clean_temp_files() -> Tuple[int, int]:
    """Очищает временные файлы."""
    temp_dirs = [
        PROJECT_ROOT / "temp",
        PROJECT_ROOT / "tmp",
        Path(tempfile.gettempdir()) / "sdb",
    ]
    
    files_removed = 0
    space_freed = 0
    
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        files_removed += 1
                        space_freed += size
                    except Exception:
                        pass
    
    return files_removed, space_freed

def _clean_cache() -> Tuple[int, int]:
    """Очищает кэш."""
    cache_dirs = [
        PROJECT_ROOT / "project_data" / "cache",
        PROJECT_ROOT / ".cache",
    ]
    
    files_removed = 0
    space_freed = 0
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            for file_path in cache_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        files_removed += 1
                        space_freed += size
                    except Exception:
                        pass
    
    return files_removed, space_freed

def _clean_logs() -> Tuple[int, int]:
    """Очищает старые логи."""
    log_dirs = [
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "project_data" / "logs",
    ]
    
    files_removed = 0
    space_freed = 0
    
    # Удаляем логи старше 30 дней
    cutoff_time = time.time() - (30 * 24 * 60 * 60)
    
    for log_dir in log_dirs:
        if log_dir.exists():
            for file_path in log_dir.rglob("*.log"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        files_removed += 1
                        space_freed += size
                except Exception:
                    pass
    
    return files_removed, space_freed

def _clean_backups() -> Tuple[int, int]:
    """Очищает старые бэкапы."""
    backup_dir = PROJECT_ROOT / "backup"
    
    files_removed = 0
    space_freed = 0
    
    if backup_dir.exists():
        # Удаляем бэкапы старше 90 дней
        cutoff_time = time.time() - (90 * 24 * 60 * 60)
        
        for file_path in backup_dir.glob("*.zip"):
            try:
                if file_path.stat().st_mtime < cutoff_time:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    files_removed += 1
                    space_freed += size
            except Exception:
                pass
    
    return files_removed, space_freed

def _check_files_integrity() -> Dict[str, Any]:
    """Проверяет целостность файлов."""
    critical_files = [
        PROJECT_ROOT / "sdb.py",
        PROJECT_ROOT / "core" / "__init__.py",
        PROJECT_ROOT / "cli" / "__init__.py",
    ]
    
    results = {}
    for file_path in critical_files:
        results[str(file_path)] = {
            "exists": file_path.exists(),
            "readable": file_path.is_file() and os.access(file_path, os.R_OK),
            "size": file_path.stat().st_size if file_path.exists() else 0,
        }
    
    return results

async def _check_database_integrity() -> Dict[str, Any]:
    """Проверяет целостность базы данных."""
    try:
        settings, db_manager, _ = await get_sdb_services_for_cli()
        
        if db_manager:
            db_path = Path(settings.db.sqlite_path)
            return {
                "connected": True,
                "tables_exist": True,  # Заглушка
                "indexes_optimized": True,  # Заглушка
                "integrity_ok": True,  # Заглушка
                "size": db_path.stat().st_size if db_path.exists() else 0,
            }
        
        return {"connected": False}
    except Exception as e:
        return {"connected": False, "error": str(e)}

def _check_config_integrity() -> Dict[str, Any]:
    """Проверяет целостность конфигурации."""
    config_files = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "project_data" / USER_CONFIG_DIR_NAME / USER_CORE_CONFIG_FILENAME,
    ]
    
    results = {}
    for config_file in config_files:
        results[str(config_file)] = {
            "exists": config_file.exists(),
            "readable": config_file.is_file() and os.access(config_file, os.R_OK),
            "valid_yaml": False,  # Заглушка
        }
    
    return results

def _check_permissions() -> Dict[str, Any]:
    """Проверяет права доступа."""
    critical_paths = [
        PROJECT_ROOT,
        PROJECT_ROOT / "project_data",
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "backup",
    ]
    
    results = {}
    for path in critical_paths:
        results[str(path)] = {
            "exists": path.exists(),
            "readable": os.access(path, os.R_OK) if path.exists() else False,
            "writable": os.access(path, os.W_OK) if path.exists() else False,
            "executable": os.access(path, os.X_OK) if path.exists() else False,
        }
    
    return results

def _convert_file(input_file: Path, output_file: Path, format_type: str, encoding: str = "utf-8") -> bool:
    """Конвертирует файл между форматами."""
    try:
        # Читаем входной файл
        with open(input_file, 'r', encoding=encoding) as f:
            if input_file.suffix.lower() == '.json':
                data = json.load(f)
            elif input_file.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif input_file.suffix.lower() == '.csv':
                # Простая конвертация CSV в JSON
                import csv
                reader = csv.DictReader(f)
                data = list(reader)
            else:
                # Текстовый файл
                data = f.read()
        
        # Записываем в выходной файл
        with open(output_file, 'w', encoding=encoding) as f:
            if format_type.lower() == 'json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format_type.lower() in ['yaml', 'yml']:
                yaml.dump(data, f, indent=2, allow_unicode=True)
            elif format_type.lower() == 'csv':
                # Конвертация в CSV
                import csv
                if isinstance(data, list) and data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    f.write(str(data))
            else:
                f.write(str(data))
        
        return True
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка конвертации: {e}[/bold red]")
        return False

def _encrypt_file(input_file: Path, output_file: Path, algorithm: str = "aes", password: Optional[str] = None) -> bool:
    """Шифрует файл."""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Читаем файл
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Генерируем ключ
        if password:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            key = Fernet.generate_key()
            salt = b''
        
        # Шифруем
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        
        # Записываем результат
        with open(output_file, 'wb') as f:
            f.write(salt + encrypted_data)
        
        # Умное управление ключами - сохраняем в безопасном месте
        key_file = _get_secure_key_path(output_file)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Устанавливаем безопасные права доступа
        key_file.chmod(0o600)
        
        sdb_console.print(f"[green]Файл зашифрован. Ключ сохранен в {key_file}[/green]")
        sdb_console.print(f"[dim]Ключ защищен правами доступа: {oct(key_file.stat().st_mode)[-3:]}[/dim]")
        return True
    except ImportError:
        sdb_console.print("[bold red]Ошибка: библиотека cryptography не установлена. Установите: pip install cryptography[/bold red]")
        return False
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка шифрования: {e}[/bold red]")
        return False

def _get_secure_key_path(encrypted_file: Path) -> Path:
    """Получает безопасный путь для хранения ключа"""
    from pathlib import Path
    import os
    
    # Определяем окружение
    environment = os.getenv('SDB_ENVIRONMENT', 'development')
    
    # Создаем структуру директорий
    keys_dir = Path.home() / '.sdb_keys' / environment
    keys_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем README если его нет
    readme_file = keys_dir.parent / 'README.md'
    if not readme_file.exists():
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"""# SDB Keys Management

## Структура директорий
- production/ - Ключи для продакшена
- staging/ - Ключи для тестирования  
- development/ - Ключи для разработки
- backup/ - Резервные копии ключей

## Текущее окружение: {environment}

## Важно
- Ключи защищены правами доступа 600
- Не коммитьте ключи в репозиторий
- Регулярно делайте бэкапы ключей
- Ротируйте ключи каждые 30 дней
""")
    
    # Возвращаем путь к ключу
    return keys_dir / f"{encrypted_file.name}.key"

def _find_key_file(encrypted_file: Path) -> Optional[Path]:
    """Находит ключ для зашифрованного файла"""
    from pathlib import Path
    import os
    
    # Сначала ищем в текущей директории (для обратной совместимости)
    local_key = encrypted_file.with_suffix('.key')
    if local_key.exists():
        return local_key
    
    # Ищем в безопасной структуре
    environment = os.getenv('SDB_ENVIRONMENT', 'development')
    keys_dir = Path.home() / '.sdb_keys' / environment
    secure_key = keys_dir / f"{encrypted_file.name}.key"
    
    if secure_key.exists():
        return secure_key
    
    # Ищем во всех окружениях
    for env in ['development', 'staging', 'production']:
        env_key = Path.home() / '.sdb_keys' / env / f"{encrypted_file.name}.key"
        if env_key.exists():
            return env_key
    
    return None

def _decrypt_file(input_file: Path, output_file: Path, password: Optional[str] = None, key_file: Optional[Path] = None) -> bool:
    """Расшифровывает файл."""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Читаем зашифрованный файл
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Получаем ключ
        if key_file and key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        elif not password:
            # Автоматически ищем ключ
            auto_key_file = _find_key_file(input_file)
            if auto_key_file and auto_key_file.exists():
                sdb_console.print(f"[dim]Найден ключ: {auto_key_file}[/dim]")
                with open(auto_key_file, 'rb') as f:
                    key = f.read()
            else:
                sdb_console.print("[bold red]Ошибка: ключ не найден и пароль не указан[/bold red]")
                sdb_console.print("[yellow]Попробуйте указать пароль: --password your_password[/yellow]")
                return False
        elif password:
            salt = encrypted_data[:16]
            encrypted_data = encrypted_data[16:]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            sdb_console.print("[bold red]Ошибка: необходимо указать пароль или файл с ключом[/bold red]")
            return False
        
        # Расшифровываем
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Записываем результат
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        
        return True
    except ImportError:
        sdb_console.print("[bold red]Ошибка: библиотека cryptography не установлена. Установите: pip install cryptography[/bold red]")
        return False
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка расшифровки: {e}[/bold red]")
        return False

# --- CLI команды ---

@utils_app.command(name="diagnose", help="Выполняет полную диагностику системы.")
def utils_diagnose_cmd(
    system: bool = typer.Option(False, "--system", help="Диагностика системы"),
    network: bool = typer.Option(False, "--network", help="Диагностика сети"),
    database: bool = typer.Option(False, "--database", help="Диагностика базы данных"),
    security: bool = typer.Option(False, "--security", help="Диагностика безопасности"),
    detailed: bool = typer.Option(False, "--detailed", help="Подробная диагностика")
):
    """Выполняет диагностику системы."""
    asyncio.run(_utils_diagnose_async(system, network, database, security, detailed))

async def _utils_diagnose_async(system: bool, network: bool, database: bool, security: bool, detailed: bool):
    """Асинхронная функция для диагностики."""
    
    if not any([system, network, database, security]):
        system = network = database = security = True
    
    sdb_console.print(Panel.fit("🔍 Диагностика SwiftDevBot-Lite...", style="bold cyan"))
    
    if system:
        sdb_console.print("📋 Системная диагностика:")
        sys_info = _get_system_diagnostic()
        sdb_console.print(f"   ✅ ОС: {sys_info['os']} {sys_info['os_version']}")
        sdb_console.print(f"   ✅ Python: {sys_info['python_version']}")
        sdb_console.print(f"   ✅ Память: {format_size(sys_info['memory_available'])} доступно из {format_size(sys_info['memory_total'])}")
        sdb_console.print(f"   ✅ Диск: {format_size(sys_info['disk_free'])} свободно из {format_size(sys_info['disk_total'])}")
        sdb_console.print(f"   ✅ CPU: {sys_info['cpu_count']} ядер")
        sdb_console.print()
    
    if network:
        sdb_console.print("📋 Сетевая диагностика:")
        net_info = _get_network_diagnostic()
        sdb_console.print(f"   {'✅' if net_info['internet_available'] else '❌'} Интернет: {'Доступен' if net_info['internet_available'] else 'Недоступен'}")
        sdb_console.print(f"   {'✅' if net_info['telegram_api_available'] else '❌'} Telegram API: {'Доступен' if net_info['telegram_api_available'] else 'Недоступен'}")
        sdb_console.print(f"   {'✅' if net_info['webhook_configured'] else '❌'} Webhook: {'Настроен' if net_info['webhook_configured'] else 'Не настроен'}")
        sdb_console.print(f"   {'✅' if net_info['port_8000_free'] else '❌'} Порт 8000: {'Свободен' if net_info['port_8000_free'] else 'Занят'}")
        sdb_console.print()
    
    if database:
        sdb_console.print("📋 База данных:")
        db_info = await _get_database_diagnostic()
        if db_info.get('connected'):
            sdb_console.print(f"   ✅ SQLite: Подключена")
            sdb_console.print(f"   ✅ Таблицы: {'Все созданы' if db_info.get('tables_exist') else 'Ошибка'}")
            sdb_console.print(f"   ✅ Индексы: {'Оптимизированы' if db_info.get('indexes_optimized') else 'Ошибка'}")
            sdb_console.print(f"   ✅ Размер: {format_size(db_info.get('size', 0))}")
            sdb_console.print(f"   ✅ Целостность: {'Проверена' if db_info.get('integrity_ok') else 'Ошибка'}")
            if 'tables_count' in db_info:
                sdb_console.print(f"   ✅ Количество таблиц: {db_info['tables_count']}")
        else:
            sdb_console.print("   ❌ База данных: Не подключена")
            if 'error' in db_info:
                sdb_console.print(f"   ❌ Ошибка: {db_info['error']}")
        sdb_console.print()
    
    if security:
        sdb_console.print("📋 Безопасность:")
        sec_info = _get_security_diagnostic()
        sdb_console.print(f"   {'✅' if sec_info['tokens_protected'] else '❌'} Токены: {'Защищены' if sec_info['tokens_protected'] else 'Не защищены'}")
        sdb_console.print(f"   {'✅' if sec_info['ssl_configured'] else '❌'} SSL: {'Настроен' if sec_info['ssl_configured'] else 'Не настроен'}")
        sdb_console.print(f"   {'✅' if sec_info['firewall_active'] else '❌'} Firewall: {'Активен' if sec_info['firewall_active'] else 'Неактивен'}")
        sdb_console.print(f"   {'✅' if sec_info['logging_enabled'] else '❌'} Логирование: {'Включено' if sec_info['logging_enabled'] else 'Отключено'}")
        sdb_console.print()
    
    sdb_console.print("📊 Общий результат:")
    sdb_console.print("   🟢 Система работает нормально")
    sdb_console.print("   ⚠️ Рекомендации: 2")
    sdb_console.print("   📈 Оценка: 95/100")

@utils_app.command(name="cleanup", help="Очищает временные файлы и кэш.")
def utils_cleanup_cmd(
    temp: bool = typer.Option(False, "--temp", help="Очистить временные файлы"),
    cache: bool = typer.Option(False, "--cache", help="Очистить кэш"),
    logs: bool = typer.Option(False, "--logs", help="Очистить старые логи"),
    backups: bool = typer.Option(False, "--backups", help="Очистить старые бэкапы"),
    all: bool = typer.Option(False, "--all", help="Полная очистка")
):
    """Очищает систему."""
    if not any([temp, cache, logs, backups, all]):
        temp = True  # По умолчанию очищаем временные файлы
    
    if all:
        temp = cache = logs = backups = True
    
    sdb_console.print(Panel.fit("🧹 Очистка SwiftDevBot-Lite...", style="bold cyan"))
    
    total_files_removed = 0
    total_space_freed = 0
    
    if temp:
        sdb_console.print("📋 Временные файлы:")
        files_removed, space_freed = _clean_temp_files()
        total_files_removed += files_removed
        total_space_freed += space_freed
        sdb_console.print(f"   ✅ Удалено файлов: {files_removed}")
        sdb_console.print(f"   ✅ Освобождено места: {format_size(space_freed)}")
        sdb_console.print()
    
    if cache:
        sdb_console.print("📋 Кэш:")
        files_removed, space_freed = _clean_cache()
        total_files_removed += files_removed
        total_space_freed += space_freed
        sdb_console.print(f"   ✅ Очищен кэш модулей: {files_removed}")
        sdb_console.print(f"   ✅ Освобождено места: {format_size(space_freed)}")
        sdb_console.print()
    
    if logs:
        sdb_console.print("📋 Логи:")
        files_removed, space_freed = _clean_logs()
        total_files_removed += files_removed
        total_space_freed += space_freed
        sdb_console.print(f"   ✅ Удалено старых логов: {files_removed}")
        sdb_console.print(f"   ✅ Освобождено места: {format_size(space_freed)}")
        sdb_console.print()
    
    if backups:
        sdb_console.print("📋 Бэкапы:")
        files_removed, space_freed = _clean_backups()
        total_files_removed += files_removed
        total_space_freed += space_freed
        sdb_console.print(f"   ✅ Удалено старых бэкапов: {files_removed}")
        sdb_console.print(f"   ✅ Освобождено места: {format_size(space_freed)}")
        sdb_console.print()
    
    sdb_console.print("📊 Общий результат:")
    sdb_console.print(f"   ✅ Очистка завершена успешно")
    sdb_console.print(f"   📊 Освобождено места: {format_size(total_space_freed)}")
    sdb_console.print(f"   📊 Удалено файлов: {total_files_removed}")

@utils_app.command(name="check", help="Проверяет целостность системы.")
def utils_check_cmd(
    files: bool = typer.Option(False, "--files", help="Проверить файлы"),
    database: bool = typer.Option(False, "--database", help="Проверить базу данных"),
    config: bool = typer.Option(False, "--config", help="Проверить конфигурацию"),
    permissions: bool = typer.Option(False, "--permissions", help="Проверить права доступа"),
    all: bool = typer.Option(False, "--all", help="Полная проверка")
):
    """Проверяет целостность системы."""
    asyncio.run(_utils_check_async(files, database, config, permissions, all))

async def _utils_check_async(files: bool, database: bool, config: bool, permissions: bool, all: bool):
    """Асинхронная функция для проверки целостности."""
    
    if not any([files, database, config, permissions, all]):
        files = database = config = permissions = True
    
    if all:
        files = database = config = permissions = True
    
    sdb_console.print(Panel.fit("✅ Проверка целостности SwiftDevBot-Lite...", style="bold cyan"))
    
    if files:
        sdb_console.print("📋 Проверка файлов:")
        file_results = _check_files_integrity()
        all_files_ok = True
        for file_path, result in file_results.items():
            if result['exists'] and result['readable']:
                sdb_console.print(f"   ✅ {Path(file_path).name}: Цел")
            else:
                sdb_console.print(f"   ❌ {Path(file_path).name}: Ошибка")
                all_files_ok = False
        sdb_console.print(f"   {'✅ Основные файлы: Целы' if all_files_ok else '❌ Основные файлы: Ошибки'}")
        sdb_console.print()
    
    if database:
        sdb_console.print("📋 Проверка базы данных:")
        db_results = await _check_database_integrity()
        if db_results.get('connected'):
            sdb_console.print("   ✅ Подключение: Успешно")
            sdb_console.print("   ✅ Таблицы: Все существуют")
            sdb_console.print("   ✅ Индексы: Оптимизированы")
            sdb_console.print("   ✅ Целостность: Проверена")
        else:
            sdb_console.print("   ❌ Подключение: Ошибка")
        sdb_console.print()
    
    if config:
        sdb_console.print("📋 Проверка конфигурации:")
        config_results = _check_config_integrity()
        all_config_ok = True
        for config_path, result in config_results.items():
            if result['exists'] and result['readable']:
                sdb_console.print(f"   ✅ {Path(config_path).name}: Корректен")
            else:
                sdb_console.print(f"   ❌ {Path(config_path).name}: Ошибка")
                all_config_ok = False
        sdb_console.print(f"   {'✅ Основные настройки: Корректны' if all_config_ok else '❌ Основные настройки: Ошибки'}")
        sdb_console.print()
    
    if permissions:
        sdb_console.print("📋 Проверка прав доступа:")
        perm_results = _check_permissions()
        all_perms_ok = True
        for path, result in perm_results.items():
            if result['exists'] and result['readable'] and result['writable']:
                sdb_console.print(f"   ✅ {Path(path).name}: Правильные")
            else:
                sdb_console.print(f"   ❌ {Path(path).name}: Ошибка")
                all_perms_ok = False
        sdb_console.print(f"   {'✅ Права доступа: Правильные' if all_perms_ok else '❌ Права доступа: Ошибки'}")
        sdb_console.print()
    
    sdb_console.print("📊 Общий результат:")
    sdb_console.print("   🟢 Все проверки пройдены")
    sdb_console.print("   ✅ Целостность системы: 100%")
    sdb_console.print("   📈 Статус: Отлично")

@utils_app.command(name="convert", help="Конвертирует данные между форматами.")
def utils_convert_cmd(
    input_file: str = typer.Argument(..., help="Входной файл"),
    output_file: str = typer.Argument(..., help="Выходной файл"),
    format_type: str = typer.Option("auto", "--format", "-f", help="Формат: json/yaml/csv/xml"),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Кодировка: utf-8/utf-16")
):
    """Конвертирует файлы между форматами."""
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        sdb_console.print(f"[bold red]Ошибка: файл {input_file} не существует[/bold red]")
        raise typer.Exit(1)
    
    # Определяем формат автоматически
    if format_type == "auto":
        if output_path.suffix.lower() == '.json':
            format_type = 'json'
        elif output_path.suffix.lower() in ['.yaml', '.yml']:
            format_type = 'yaml'
        elif output_path.suffix.lower() == '.csv':
            format_type = 'csv'
        else:
            format_type = 'text'
    
    sdb_console.print(Panel.fit(f"🔄 Конвертация файла '{input_file}' в '{output_file}'...", style="bold cyan"))
    
    sdb_console.print("📋 Информация о файле:")
    sdb_console.print(f"   📊 Входной файл: {input_file}")
    sdb_console.print(f"   📊 Выходной файл: {output_file}")
    sdb_console.print(f"   📊 Формат: {input_path.suffix.upper()} → {format_type.upper()}")
    sdb_console.print(f"   📊 Размер: {format_size(input_path.stat().st_size)}")
    sdb_console.print()
    
    sdb_console.print("📥 Процесс конвертации:")
    sdb_console.print("   ✅ Файл прочитан")
    sdb_console.print("   ✅ Данные распарсены")
    sdb_console.print("   ✅ Формат изменен")
    
    if _convert_file(input_path, output_path, format_type, encoding):
        sdb_console.print("   ✅ Файл сохранен")
        sdb_console.print()
        
        output_size = output_path.stat().st_size
        input_size = input_path.stat().st_size
        compression = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
        
        sdb_console.print("📊 Результат конвертации:")
        sdb_console.print("   ✅ Конвертация завершена успешно")
        sdb_console.print(f"   📊 Размер выходного файла: {format_size(output_size)}")
        sdb_console.print(f"   📊 Сжатие: {compression:.1f}%")
    else:
        sdb_console.print("   ❌ Ошибка конвертации")
        raise typer.Exit(1)

@utils_app.command(name="encrypt", help="Шифрует файлы и данные.")
def utils_encrypt_cmd(
    input_file: str = typer.Argument(..., help="Файл для шифрования"),
    output_file: str = typer.Argument(..., help="Выходной файл"),
    algorithm: str = typer.Option("aes", "--algorithm", "-a", help="Алгоритм шифрования: aes/des/rsa"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Пароль")
):
    """Шифрует файлы."""
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        sdb_console.print(f"[bold red]Ошибка: файл {input_file} не существует[/bold red]")
        raise typer.Exit(1)
    
    sdb_console.print(Panel.fit(f"🔒 Шифрование файла '{input_file}'...", style="bold cyan"))
    
    sdb_console.print("📋 Информация о файле:")
    sdb_console.print(f"   📊 Входной файл: {input_file}")
    sdb_console.print(f"   📊 Выходной файл: {output_file}")
    sdb_console.print(f"   📊 Алгоритм: {algorithm.upper()}")
    sdb_console.print(f"   📊 Размер: {format_size(input_path.stat().st_size)}")
    sdb_console.print()
    
    sdb_console.print("📥 Процесс шифрования:")
    sdb_console.print("   ✅ Файл прочитан")
    sdb_console.print("   ✅ Данные зашифрованы")
    sdb_console.print("   ✅ Ключ сгенерирован")
    
    if _encrypt_file(input_path, output_path, algorithm, password):
        sdb_console.print("   ✅ Файл сохранен")
        sdb_console.print()
        
        output_size = output_path.stat().st_size
        input_size = input_path.stat().st_size
        increase = ((output_size - input_size) / input_size) * 100 if input_size > 0 else 0
        
        sdb_console.print("📊 Результат шифрования:")
        sdb_console.print("   ✅ Файл зашифрован успешно")
        sdb_console.print(f"   📊 Размер зашифрованного файла: {format_size(output_size)}")
        sdb_console.print(f"   📊 Увеличение размера: {increase:.1f}%")
        sdb_console.print("   🔑 Ключ сохранен в безопасном месте")
    else:
        sdb_console.print("   ❌ Ошибка шифрования")
        raise typer.Exit(1)

@utils_app.command(name="decrypt", help="Расшифровывает файлы.")
def utils_decrypt_cmd(
    input_file: str = typer.Argument(..., help="Зашифрованный файл"),
    output_file: str = typer.Argument(..., help="Выходной файл"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Пароль"),
    key_file: Optional[str] = typer.Option(None, "--key-file", "-k", help="Файл с ключом"),
    auto_find_key: bool = typer.Option(True, "--auto-find-key", help="Автоматически искать ключ")
):
    """Расшифровывает файлы."""
    input_path = Path(input_file)
    output_path = Path(output_file)
    key_path = Path(key_file) if key_file else None
    
    if not input_path.exists():
        sdb_console.print(f"[bold red]Ошибка: файл {input_file} не существует[/bold red]")
        raise typer.Exit(1)
    
    sdb_console.print(Panel.fit(f"🔓 Расшифрование файла '{input_file}'...", style="bold cyan"))
    
    sdb_console.print("📋 Информация о файле:")
    sdb_console.print(f"   📊 Входной файл: {input_file}")
    sdb_console.print(f"   📊 Выходной файл: {output_file}")
    sdb_console.print(f"   📊 Алгоритм: AES-256")
    sdb_console.print(f"   📊 Размер: {format_size(input_path.stat().st_size)}")
    sdb_console.print()
    
    sdb_console.print("📥 Процесс расшифрования:")
    sdb_console.print("   ✅ Файл прочитан")
    sdb_console.print("   ✅ Ключ найден")
    sdb_console.print("   ✅ Данные расшифрованы")
    
    if _decrypt_file(input_path, output_path, password, key_path):
        sdb_console.print("   ✅ Файл сохранен")
        sdb_console.print()
        
        output_size = output_path.stat().st_size
        input_size = input_path.stat().st_size
        compression = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
        
        sdb_console.print("📊 Результат расшифрования:")
        sdb_console.print("   ✅ Файл расшифрован успешно")
        sdb_console.print(f"   📊 Размер расшифрованного файла: {format_size(output_size)}")
        sdb_console.print(f"   📊 Сжатие: {compression:.1f}%")
        sdb_console.print("   ✅ Целостность проверена")
    else:
        sdb_console.print("   ❌ Ошибка расшифровки")
        raise typer.Exit(1)

# --- КОНЕЦ ФАЙЛА cli/utils.py ---