# cli_commands/cli_utils.py

from typing import Optional, Any, Tuple
from pathlib import Path
import asyncio
import typer # Для typer.confirm
from rich.console import Console # Можно использовать для вывода, если понадобится

# console_cli_utils = Console() # Если нужен свой экземпляр консоли для утилит

async def get_sdb_services_for_cli(
    init_db: bool = False,
    init_rbac: bool = False,
) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]: # (settings, db_manager, rbac_service)
    """
    Вспомогательная асинхронная функция для получения основных сервисов SDB,
    необходимых для выполнения многих CLI команд.
    Инициализирует DBManager "на лету" и, опционально, RBACService.
    Возвращает кортеж (settings, db_manager, rbac_service).
    DBManager нужно будет закрыть вручную через await db_manager.dispose().
    """
    settings_instance: Optional[Any] = None
    db_manager_instance: Optional[Any] = None
    rbac_service_instance: Optional[Any] = None

    try:
        from core.app_settings import settings # Загружаем глобальные настройки
        settings_instance = settings

        if init_db or init_rbac: # DBManager нужен для RBAC
            from core.database.manager import DBManager
            # Используем app_settings=settings, чтобы DBManager правильно строил пути и т.д.
            db_m = DBManager(db_settings=settings.db, app_settings=settings)
            await db_m.initialize()
            db_manager_instance = db_m

            if init_rbac and db_manager_instance:
                from core.rbac.service import RBACService
                rbac_service_instance = RBACService(db_manager=db_manager_instance) # Передаем DBManager

        return settings_instance, db_manager_instance, rbac_service_instance

    except ImportError as e_imp:
        # Ошибки импорта должны быть обработаны в вызывающем коде, здесь просто перевыбрасываем
        # Console().print(f"[bold red]Ошибка импорта в get_sdb_services_for_cli: {e_imp}[/]")
        raise
    except Exception as e_init:
        # Console().print(f"[bold red]Ошибка инициализации сервисов в get_sdb_services_for_cli: {e_init}[/]")
        if db_manager_instance: # Попытаться закрыть, если что-то создалось до ошибки
            await db_manager_instance.dispose()
        raise


def confirm_action(prompt_message: str, default_choice: bool = False, abort_on_false: bool = True) -> bool:
    """
    Общая функция для запроса подтверждения действия у пользователя через Typer.
    Если abort_on_false=True и пользователь отвечает "нет", вызывает typer.Abort().
    Возвращает True, если пользователь ответил "да".
    """
    confirmed = typer.confirm(prompt_message, default=default_choice, abort=abort_on_false)
    # Если abort_on_false=True и пользователь выбрал "нет", typer.confirm уже вызовет typer.Abort().
    # Если abort_on_false=False и пользователь выбрал "нет", вернется False.
    # Если пользователь выбрал "да", вернется True.
    return confirmed


def format_size(size_bytes: int) -> str:
    """Форматирует размер в байтах в человекочитаемый вид (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.2f} MB"
    else:
        return f"{size_bytes/(1024**3):.2f} GB"