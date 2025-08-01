# --- НАЧАЛО ФАЙЛА cli/backup.py ---
import os
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple as TypingTuple
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Утилиты и Typer-приложение
from .utils import sdb_console, confirm_action

backup_app = typer.Typer(
    name="backup",
    help="💾 Создание, управление и восстановление бэкапов SwiftDevBot.",
    rich_markup_mode="rich",
    no_args_is_help=True
)

# Константы
DB_BACKUP_DIR_NAME = "database"
DATA_FILES_BACKUP_DIR_NAME = "project_data_files"
DATA_ARCHIVE_EXTENSION = ".tar.gz"
POSTGRES_BACKUP_FILENAME = "sdb_postgres_backup.dump"
MYSQL_BACKUP_FILENAME = "sdb_mysql_backup.sql"
USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT = "Config"

def _get_backup_base_dir() -> Optional[Path]:
    try:
        # Используем папку backup в корне проекта
        project_root = Path(__file__).resolve().parent.parent
        backup_dir = project_root / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка при создании/доступе к директории бэкапов: {e}[/]")
        return None

def _find_system_utility(name: str) -> Optional[str]:
    return shutil.which(name)

def _execute_system_command(command: List[str], env_vars: Optional[dict] = None, input_data: Optional[str] = None, show_stdout_on_success: bool = False) -> bool:
    full_env = os.environ.copy()
    if env_vars:
        full_env.update(env_vars)
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=full_env,
            input=input_data,
            check=False
        )
        if process.returncode == 0:
            if show_stdout_on_success and process.stdout:
                 sdb_console.print(f"[dim cyan]  --- STDOUT ---[/]\n{process.stdout.strip()}")
            return True
        else:
            sdb_console.print(f"[bold red]  ❌ Ошибка выполнения команды (код: {process.returncode}): {' '.join(command)}[/]")
            if process.stdout:
                sdb_console.print(f"[yellow]  --- STDOUT ---[/]\n{process.stdout.strip()}")
            if process.stderr:
                sdb_console.print(f"[red]  --- STDERR ---[/]\n{process.stderr.strip()}")
            return False
    except FileNotFoundError:
        sdb_console.print(f"[bold red]  ❌ Ошибка: Команда '{command[0]}' не найдена. Убедитесь, что утилита установлена и доступна в PATH.[/]")
        return False
    except Exception as e:
        sdb_console.print(f"[bold red]  ❌ Неожиданная ошибка при выполнении команды '{command[0]}': {e}[/]")
        return False

@backup_app.command(name="create", help="Создать новый бэкап данных и/или базы данных SDB.")
def create_backup_cmd(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Пользовательское имя для бэкапа."),
    include_db: bool = typer.Option(True, "--db/--no-db", help="Включить ли базу данных в бэкап."),
    include_data_dirs: Optional[List[str]] = typer.Option(None, "--data-dir", "-dd", help=f"Директории из 'project_data/' для бэкапа. По умолчанию: ['{USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT}']."),
    compress_data: bool = typer.Option(True, "--compress/--no-compress", help="Сжимать ли бэкап данных в архив."),
    path: Optional[Path] = typer.Option(None, "--path", help="Путь к папке, куда будет создан бэкап (по умолчанию ./backup/<имя_бэкапа>)"),
    exclude: Optional[List[str]] = typer.Option(None, "--exclude", help="Список путей для исключения при бэкапе данных (например: logs, temp)")
):
    from core.app_settings import settings

    if include_data_dirs is None:
        include_data_dirs = [USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT]
    elif include_data_dirs == [""]:
        include_data_dirs = []

    backup_base_dir = _get_backup_base_dir()
    if not backup_base_dir and not path:
        raise typer.Exit(code=1)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Определяем тип бэкапа для названия папки
    backup_types = []
    if include_db:
        from core.app_settings import settings
        backup_types.append(f"db_{settings.db.type}")
    if include_data_dirs:
        backup_types.append("data")
    
    backup_type_name = "_".join(backup_types) if backup_types else "full"
    backup_name = name if name else f"{backup_type_name}_{timestamp}"
    
    if path:
        current_backup_path = Path(path).expanduser().resolve()
    else:
        current_backup_path = backup_base_dir / backup_name
    if current_backup_path.exists():
        sdb_console.print(f"[bold red]Ошибка: Директория бэкапа с именем '{current_backup_path}' уже существует.[/]")
        raise typer.Exit(code=1)
    
    current_backup_path.mkdir(parents=True)
    sdb_console.print(Panel(f"[bold cyan]Создание бэкапа: {backup_name}[/]", expand=False, subtitle=f"Расположение: {current_backup_path}"))

    db_backup_successful = False
    data_backup_successful = False

    if include_db:
        sdb_console.print("\n[bold blue]1. Бэкап Базы Данных[/]")
        db_settings = settings.db
        db_backup_target_dir = current_backup_path / DB_BACKUP_DIR_NAME
        db_backup_target_dir.mkdir()

        if db_settings.type == "sqlite":
            sqlite_file_path = Path(db_settings.sqlite_path)
            if sqlite_file_path.is_file():
                backup_db_file = db_backup_target_dir / sqlite_file_path.name
                shutil.copy2(sqlite_file_path, backup_db_file)
                sdb_console.print(f"[green]  ✅ Бэкап SQLite БД успешно создан: '{backup_db_file}'[/]")
                db_backup_successful = True
            else:
                sdb_console.print(f"[bold red]  ❌ Ошибка: Файл SQLite БД не найден по пути '{sqlite_file_path}'[/]")
        
        elif db_settings.type == "postgresql":
            pg_dump_path = _find_system_utility("pg_dump")
            if not pg_dump_path: sdb_console.print("[bold red]  ❌ Утилита 'pg_dump' не найдена.[/]")
            elif not db_settings.pg_dsn: sdb_console.print("[bold red]  ❌ DSN для PostgreSQL не настроен.[/]")
            else:
                parsed_url = urlparse(str(db_settings.pg_dsn))
                backup_file = db_backup_target_dir / POSTGRES_BACKUP_FILENAME
                cmd = [pg_dump_path, "-F", "c", "-f", str(backup_file), str(db_settings.pg_dsn)]
                env = {"PGPASSWORD": parsed_url.password} if parsed_url.password else {}
                sdb_console.print(f"  Выполнение pg_dump для PostgreSQL в '{backup_file}'...")
                if _execute_system_command(cmd, env_vars=env):
                    sdb_console.print(f"[green]  ✅ Бэкап PostgreSQL успешно создан.[/]")
                    db_backup_successful = True
        
        elif db_settings.type == "mysql":
            mysqldump_path = _find_system_utility("mysqldump")
            if not mysqldump_path: sdb_console.print("[bold red]  ❌ Утилита 'mysqldump' не найдена.[/]")
            elif not db_settings.mysql_dsn: sdb_console.print("[bold red]  ❌ DSN для MySQL не настроен.[/]")
            else:
                parsed_url = urlparse(str(db_settings.mysql_dsn))
                backup_file = db_backup_target_dir / MYSQL_BACKUP_FILENAME
                cmd = [
                    mysqldump_path,
                    f"--host={parsed_url.hostname or 'localhost'}",
                    f"--port={parsed_url.port or 3306}",
                    f"--user={parsed_url.username}",
                    "--column-statistics=0",
                    "--databases",
                    parsed_url.path.lstrip('/'),
                    f"--result-file={backup_file}"
                ]
                env = {"MYSQL_PWD": parsed_url.password} if parsed_url.password else {}
                sdb_console.print(f"  Выполнение mysqldump для MySQL в '{backup_file}'...")
                if _execute_system_command(cmd, env_vars=env):
                    sdb_console.print(f"[green]  ✅ Бэкап MySQL успешно создан.[/]")
                    db_backup_successful = True
        else:
            sdb_console.print(f"[bold red]  ❌ Неподдерживаемый тип БД: {db_settings.type}[/]")
    
    if include_data_dirs:
        sdb_console.print(f"\n[bold blue]2. Бэкап Данных Проекта[/]")
        if exclude:
            sdb_console.print(f"[yellow]  Исключаемые пути: {', '.join(exclude)}[/]")
        project_data_root_path = settings.core.project_data_path
        data_to_archive_paths: List[TypingTuple[Path, str]] = []
        for dir_name_rel in include_data_dirs:
            source_dir_abs = (project_data_root_path / dir_name_rel).resolve()
            if source_dir_abs.is_dir():
                data_to_archive_paths.append((source_dir_abs, dir_name_rel))
            else:
                sdb_console.print(f"[yellow]  ⚠️ Директория '{source_dir_abs}' не найдена. Пропущена.[/]")
        
        if data_to_archive_paths:
            data_backup_target_dir = current_backup_path / DATA_FILES_BACKUP_DIR_NAME
            data_backup_target_dir.mkdir(exist_ok=True)
            archive_filename_stem = f"project_data_backup_{timestamp}"
            archive_file_path = data_backup_target_dir / (archive_filename_stem + (DATA_ARCHIVE_EXTENSION if compress_data else ".tar"))
            mode = "w:gz" if compress_data else "w"
            
            def filter_function(tarinfo):
                """Функция для фильтрации файлов при добавлении в архив."""
                if exclude:
                    # Получаем относительный путь от корня архива
                    arcname = tarinfo.name
                    # Проверяем, не исключён ли путь
                    for exclude_path in exclude:
                        if arcname.startswith(exclude_path + "/") or arcname == exclude_path:
                            return None
                return tarinfo
            
            with tarfile.open(archive_file_path, mode) as tar:
                for source_path, arcname_prefix in data_to_archive_paths:
                    tar.add(str(source_path), arcname=arcname_prefix, filter=filter_function)
            sdb_console.print(f"[green]  ✅ Бэкап данных проекта успешно создан: '{archive_file_path}'[/]")
            data_backup_successful = True

    sdb_console.print("\n[bold underline]Итоги создания бэкапа:[/]")
    if include_db:
        sdb_console.print(f"[bold green]  БД: УСПЕШНО[/]" if db_backup_successful else "[bold red]  БД: ОШИБКА[/]")
    if include_data_dirs:
        sdb_console.print(f"[bold green]  Данные проекта: УСПЕШНО[/]" if data_backup_successful else "[bold red]  Данные проекта: ОШИБКА[/]")

@backup_app.command(name="list", help="Показать список доступных бэкапов SDB.")
def list_backups_cmd():
    backup_base_dir = _get_backup_base_dir()
    if not backup_base_dir: raise typer.Exit(code=1)
    
    backups = [d for d in backup_base_dir.iterdir() if d.is_dir()]
    if not backups:
        sdb_console.print(f"[yellow]Не найдено бэкапов в '{backup_base_dir}'.[/]"); return

    table = Table(title="[bold cyan]Доступные бэкапы[/]")
    table.add_column("Имя Бэкапа", style="cyan")
    table.add_column("Дата Создания")
    table.add_column("Содержит БД?")
    table.add_column("Содержит Данные?")
    
    for backup_dir in sorted(backups, key=lambda p: p.name, reverse=True):
        date_str = "N/A"
        try:
            ts_str = backup_dir.name.split('_')[-1]
            dt_obj = datetime.strptime(ts_str, '%Y%m%d_%H%M%S')
            date_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, IndexError): pass
        
        has_db = (backup_dir / DB_BACKUP_DIR_NAME).is_dir() and any((backup_dir / DB_BACKUP_DIR_NAME).iterdir())
        has_data = (backup_dir / DATA_FILES_BACKUP_DIR_NAME).is_dir() and any((backup_dir / DATA_FILES_BACKUP_DIR_NAME).iterdir())
        table.add_row(backup_dir.name, date_str, "✅" if has_db else "❌", "✅" if has_data else "❌")
    sdb_console.print(table)

@backup_app.command(name="restore", help="[ОПАСНО!] Восстановить систему SDB из указанного бэкапа.")
def restore_backup_cmd(
    backup_name: str = typer.Argument(..., help="Имя бэкапа для восстановления."),
    restore_db: bool = typer.Option(True, "--db/--no-db", help="Восстановить ли базу данных."),
    restore_data_dirs: bool = typer.Option(True, "--data/--no-data", help="Восстановить ли данные проекта.")
):
    from core.app_settings import settings
    sdb_console.print(Panel(f"[bold red]ВОССТАНОВЛЕНИЕ ИЗ БЭКАПА: {backup_name}[/]", expand=False))
    sdb_console.print("[bold red]ВНИМАНИЕ: ЭТА ОПЕРАЦИЯ ПЕРЕЗАПИШЕТ ТЕКУЩИЕ ДАННЫЕ![/]")
    if not confirm_action("Вы абсолютно уверены, что хотите продолжить?", default_choice=False):
        raise typer.Abort()

    base_backup_dir = _get_backup_base_dir()
    if not base_backup_dir: raise typer.Exit(code=1)
    
    target_backup_path = base_backup_dir / backup_name
    if not target_backup_path.is_dir():
        sdb_console.print(f"[bold red]Ошибка: Директория бэкапа '{target_backup_path}' не найдена.[/]")
        raise typer.Exit(code=1)

    db_restore_successful = False
    data_restore_successful = False
    
    if restore_db:
        sdb_console.print("\n[bold blue]1. Восстановление Базы Данных[/]")
        db_settings = settings.db
        backup_db_content_path = target_backup_path / DB_BACKUP_DIR_NAME
        if not backup_db_content_path.is_dir() or not any(backup_db_content_path.iterdir()):
            sdb_console.print(f"[yellow]  Не найдены файлы бэкапа БД в '{backup_db_content_path}'. Пропуск.[/yellow]")
        else:
            if db_settings.type == "sqlite":
                backup_file = next(backup_db_content_path.glob("*.db"), None)
                if backup_file:
                    shutil.copy2(backup_file, db_settings.sqlite_path)
                    sdb_console.print(f"[green]  ✅ База данных SQLite успешно восстановлена.[/]")
                    db_restore_successful = True
                else:
                    sdb_console.print(f"[yellow]  Не найден файл бэкапа SQLite (.db) в '{backup_db_content_path}'.[/yellow]")
            elif db_settings.type == "postgresql":
                pg_restore = _find_system_utility("pg_restore")
                backup_file = backup_db_content_path / POSTGRES_BACKUP_FILENAME
                if pg_restore and backup_file.is_file() and db_settings.pg_dsn:
                    parsed_url = urlparse(str(db_settings.pg_dsn))
                    cmd = [pg_restore, "--clean", "--if-exists", "-d", str(db_settings.pg_dsn), str(backup_file)]
                    env = {"PGPASSWORD": parsed_url.password} if parsed_url.password else {}
                    if _execute_system_command(cmd, env_vars=env):
                        sdb_console.print("[green]  ✅ База данных PostgreSQL успешно восстановлена.[/]")
                        db_restore_successful = True
                else:
                    sdb_console.print("[red]  ❌ Утилита pg_restore, файл бэкапа или DSN не найдены/не настроены.[/red]")
            elif db_settings.type == "mysql":
                mysql_client = _find_system_utility("mysql")
                backup_file = backup_db_content_path / MYSQL_BACKUP_FILENAME
                if mysql_client and backup_file.is_file() and db_settings.mysql_dsn:
                    parsed_url = urlparse(str(db_settings.mysql_dsn))
                    cmd = [
                        mysql_client,
                        f"--host={parsed_url.hostname or 'localhost'}",
                        f"--port={parsed_url.port or 3306}",
                        f"--user={parsed_url.username}",
                        parsed_url.path.lstrip('/')
                    ]
                    env = {"MYSQL_PWD": parsed_url.password} if parsed_url.password else {}
                    sql_dump_content = backup_file.read_text(encoding='utf-8')
                    if _execute_system_command(cmd, env_vars=env, input_data=sql_dump_content):
                        sdb_console.print("[green]  ✅ База данных MySQL успешно восстановлена.[/]")
                        db_restore_successful = True
                else:
                    sdb_console.print("[red]  ❌ Утилита mysql, файл бэкапа или DSN не найдены/не настроены.[/red]")

    if restore_data_dirs:
        sdb_console.print(f"\n[bold blue]2. Восстановление Данных Проекта[/]")
        backup_data_archive_dir = target_backup_path / DATA_FILES_BACKUP_DIR_NAME
        archive_file = next(backup_data_archive_dir.glob(f"*{DATA_ARCHIVE_EXTENSION}"), None)
        if archive_file and archive_file.is_file():
            target_project_data_dir = settings.core.project_data_path
            with tarfile.open(archive_file, "r:*") as tar:
                tar.extractall(path=str(target_project_data_dir))
            sdb_console.print(f"[green]  ✅ Данные проекта успешно восстановлены из архива.[/]")
            data_restore_successful = True
        else:
            sdb_console.print(f"[yellow]  Не найден архив с данными проекта в '{backup_data_archive_dir}'. Пропуск.[/yellow]")

    sdb_console.print("\n[bold underline]Итоги восстановления:[/]")
    sdb_console.print(f"  БД: {'[green]УСПЕШНО[/]' if db_restore_successful else '[yellow]ПРОПУЩЕНО/ОШИБКА[/]'}")
    sdb_console.print(f"  Данные: {'[green]УСПЕШНО[/]' if data_restore_successful else '[yellow]ПРОПУЩЕНО/ОШИБКА[/]'}")
# --- КОНЕЦ ФАЙЛА cli/backup.py ---