# --- НАЧАЛО ФАЙЛА cli/utils.py ---
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import typer
import yaml
from rich.console import Console

# --- Константы, используемые в CLI ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_CONFIG_DIR_NAME = "Config"
USER_CORE_CONFIG_FILENAME = "core_settings.yaml"
USER_MODULES_CONFIG_DIR_NAME = "modules_settings"

sdb_console = Console()

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
# --- КОНЕЦ ФАЙЛА cli/utils.py ---