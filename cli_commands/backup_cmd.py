# cli_commands/backup_cmd.py

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import shutil
import subprocess
from pathlib import Path
import sys
from datetime import datetime
import tarfile
import os
from typing import Optional, List, Tuple as TypingTuple 
from urllib.parse import urlparse 

console = Console()
backup_app = typer.Typer( name="backup", help="💾 Создание, управление и восстановление бэкапов SwiftDevBot.", rich_markup_mode="rich")

DB_BACKUP_DIR_NAME = "database"
DATA_FILES_BACKUP_DIR_NAME = "project_data_files"
DATA_ARCHIVE_EXTENSION = ".tar.gz"
POSTGRES_BACKUP_FILENAME = "sdb_postgres_backup.dump" 
MYSQL_BACKUP_FILENAME = "sdb_mysql_backup.sql"       
USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT = "Config"

def _get_backup_base_dir() -> Optional[Path]:
    try:
        from core.app_settings import settings
        backup_dir = settings.core.project_data_path / "sdb_backups" 
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    except ImportError:
        console.print("[bold red]Ошибка: Не удалось импортировать настройки для определения пути к бэкапам.[/]")
        return None
    except Exception as e:
        console.print(f"[bold red]Ошибка при создании/доступе к директории бэкапов: {e}[/]")
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
                 console.print(f"[dim cyan]  --- STDOUT ---[/]\n{process.stdout.strip()}")
            return True
        else:
            console.print(f"[bold red]  ❌ Ошибка выполнения команды (код: {process.returncode}): {' '.join(command)}[/]")
            if process.stdout:
                console.print(f"[yellow]  --- STDOUT ---[/]\n{process.stdout.strip()}")
            if process.stderr:
                console.print(f"[red]  --- STDERR ---[/]\n{process.stderr.strip()}")
            return False
    except FileNotFoundError:
        console.print(f"[bold red]  ❌ Ошибка: Команда '{command[0]}' не найдена. Убедитесь, что утилита установлена и доступна в PATH.[/]")
        return False
    except Exception as e:
        console.print(f"[bold red]  ❌ Неожиданная ошибка при выполнении команды '{command[0]}': {e}[/]")
        return False

@backup_app.command(name="create", help="Создать новый бэкап данных и/или базы данных SDB.")
def create_backup_cmd(
    name: Optional[str] = typer.Option( None, "--name", "-n", help="Пользовательское имя для этого бэкапа (иначе генерируется по дате и времени)."),
    include_db: bool = typer.Option(True, "--db/--no-db", help="Включить ли базу данных в бэкап."),
    include_data_dirs: Optional[List[str]] = typer.Option( None, "--data-dir", "-dd", help=(f"Какие директории из 'project_data/' включить в бэкап (относительно 'project_data/'). По умолчанию: ['{USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT}'] (папка Config). Можно указать несколько через пробел или несколько раз опцию. Пример: -dd Config -dd ModulesData")),
    compress_data: bool = typer.Option(True, "--compress/--no-compress", help="Сжимать ли бэкап данных в архив (.tar.gz).")
):
    from core.app_settings import settings 

    if include_data_dirs is None: 
        include_data_dirs = [USER_CONFIG_DIR_NAME_FOR_BACKUP_DEFAULT]

    backup_base_dir = _get_backup_base_dir()
    if not backup_base_dir: 
        raise typer.Exit(code=1)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = name if name else f"sdb_backup_{timestamp}"
    
    current_backup_path = backup_base_dir / backup_name
    if current_backup_path.exists():
        console.print(f"[bold red]Ошибка: Директория/файл бэкапа с именем '{backup_name}' уже существует.[/]")
        raise typer.Exit(code=1)
    
    try:
        current_backup_path.mkdir(parents=True)
    except Exception as e_mkdir:
        console.print(f"[bold red]Ошибка создания директории для бэкапа '{current_backup_path}': {e_mkdir}[/]")
        raise typer.Exit(code=1)
        
    console.print(Panel(f"[bold cyan]Создание бэкапа: {backup_name}[/]", expand=False, border_style="cyan", subtitle=f"Расположение: {current_backup_path}"))

    db_backup_successful = False
    data_backup_successful = False

    if include_db:
        console.print("\n[bold blue]1. Бэкап Базы Данных[/]")
        db_settings = settings.db
        db_backup_target_dir = current_backup_path / DB_BACKUP_DIR_NAME
        db_backup_target_dir.mkdir()

        if db_settings.type == "sqlite":
            sqlite_file_path = Path(db_settings.sqlite_path) 
            if sqlite_file_path.exists() and sqlite_file_path.is_file():
                try:
                    backup_db_file = db_backup_target_dir / sqlite_file_path.name
                    shutil.copy2(sqlite_file_path, backup_db_file)
                    console.print(f"[green]  ✅ Бэкап SQLite БД успешно создан: '{backup_db_file}'[/]")
                    db_backup_successful = True
                except Exception as e_sqlite:
                    console.print(f"[bold red]  ❌ Ошибка при копировании файла SQLite БД: {e_sqlite}[/]")
            else:
                console.print(f"[bold red]  ❌ Ошибка: Файл SQLite БД не найден по пути '{sqlite_file_path}'[/]")
        
        elif db_settings.type == "postgresql":
            pg_dump_path = _find_system_utility("pg_dump")
            if not pg_dump_path: console.print("[bold red]  ❌ Утилита 'pg_dump' не найдена. Бэкап PostgreSQL невозможен.[/]")
            elif not db_settings.pg_dsn: console.print("[bold red]  ❌ DSN для PostgreSQL (pg_dsn) не настроен. Бэкап невозможен.[/]")
            else:
                parsed_url = urlparse(str(db_settings.pg_dsn))
                pg_host = parsed_url.hostname if parsed_url.hostname else "localhost"
                pg_port = str(parsed_url.port) if parsed_url.port is not None else "5432"
                pg_user = parsed_url.username if parsed_url.username else ""
                pg_password = parsed_url.password if parsed_url.password else ""
                pg_database = parsed_url.path.lstrip('/') if parsed_url.path else ""
                backup_file = db_backup_target_dir / POSTGRES_BACKUP_FILENAME
                cmd = [ pg_dump_path ]
                if pg_host: cmd.extend(["-h", pg_host])
                if pg_port: cmd.extend(["-p", pg_port])
                if pg_user: cmd.extend(["-U", pg_user])
                if not pg_database: console.print("[bold red]  ❌ Имя базы данных не найдено в DSN PostgreSQL. Бэкап невозможен.[/]")
                else:
                    cmd.extend(["-d", pg_database, "-F", "c", "-f", str(backup_file)])
                    env = {}
                    if pg_password: env["PGPASSWORD"] = pg_password
                    console.print(f"  Выполнение pg_dump для PostgreSQL в '{backup_file}'...")
                    if _execute_system_command(cmd, env_vars=env):
                        console.print(f"[green]  ✅ Бэкап PostgreSQL успешно создан: '{backup_file}'[/]")
                        db_backup_successful = True
                    else: console.print(f"[bold red]  ❌ Ошибка при создании бэкапа PostgreSQL.[/]")
        
        elif db_settings.type == "mysql":
            mysqldump_path = _find_system_utility("mysqldump")
            if not mysqldump_path: console.print("[bold red]  ❌ Утилита 'mysqldump' не найдена. Бэкап MySQL невозможен.[/]")
            elif not db_settings.mysql_dsn: console.print("[bold red]  ❌ DSN для MySQL (mysql_dsn) не настроен. Бэкап невозможен.[/]")
            else:
                parsed_url = urlparse(str(db_settings.mysql_dsn))
                mysql_host = parsed_url.hostname if parsed_url.hostname else "localhost"
                mysql_port = str(parsed_url.port) if parsed_url.port is not None else "3306"
                mysql_user = parsed_url.username if parsed_url.username else ""
                mysql_password = parsed_url.password if parsed_url.password else ""
                mysql_database = parsed_url.path.lstrip('/') if parsed_url.path else ""
                backup_file = db_backup_target_dir / MYSQL_BACKUP_FILENAME
                cmd = [ mysqldump_path ]
                if mysql_host: cmd.extend(["-h", mysql_host])
                if mysql_port: cmd.extend(["-P", mysql_port])
                if mysql_user: cmd.extend(["-u", mysql_user])
                cmd.append("--column-statistics=0") 
                if not mysql_database: console.print("[bold red]  ❌ Имя базы данных не найдено в DSN MySQL. Бэкап невозможен.[/]")
                else:
                    cmd.extend(["--databases", mysql_database]) # Эта опция включает CREATE DATABASE IF NOT EXISTS
                    cmd.append(f"--result-file={backup_file}")
                    env = {}
                    if mysql_password: env["MYSQL_PWD"] = mysql_password
                    console.print(f"  Выполнение mysqldump для MySQL в '{backup_file}'...")
                    if _execute_system_command(cmd, env_vars=env):
                        console.print(f"[green]  ✅ Бэкап MySQL успешно создан: '{backup_file}'[/]")
                        db_backup_successful = True
                    else: console.print(f"[bold red]  ❌ Ошибка при создании бэкапа MySQL.[/]")
        else: console.print(f"[bold red]  ❌ Неподдерживаемый тип БД для бэкапа: {db_settings.type}[/]")
    else: console.print("\n[dim blue]1. Бэкап Базы Данных пропущен (согласно опции).[/dim]")

    if include_data_dirs: 
        console.print(f"\n[bold blue]2. Бэкап Данных Проекта (директории: {', '.join(include_data_dirs)})[/]")
        project_data_root_path = settings.core.project_data_path
        data_to_archive_paths: List[TypingTuple[Path, str]] = []
        for dir_name_rel in include_data_dirs:
            source_dir_abs = (project_data_root_path / dir_name_rel).resolve()
            if source_dir_abs.exists() and source_dir_abs.is_dir(): data_to_archive_paths.append((source_dir_abs, dir_name_rel))
            else: console.print(f"[yellow]  ⚠️ Предупреждение: Директория данных '{source_dir_abs}' не найдена или не является директорией. Пропущена.[/]")
        if data_to_archive_paths:
            data_backup_target_dir = current_backup_path / DATA_FILES_BACKUP_DIR_NAME
            data_backup_target_dir.mkdir(exist_ok=True)
            archive_filename_stem = f"project_data_backup_{timestamp}"
            archive_file_path = data_backup_target_dir / (archive_filename_stem + (DATA_ARCHIVE_EXTENSION if compress_data else ".tar"))
            try:
                mode = "w:gz" if compress_data else "w"
                with tarfile.open(archive_file_path, mode) as tar:
                    for source_path, arcname_prefix in data_to_archive_paths:
                        tar.add(str(source_path), arcname=arcname_prefix) 
                        console.print(f"[green]    Директория '{source_path.relative_to(project_data_root_path.parent)}' добавлена в архив.[/]")
                console.print(f"[green]  ✅ Бэкап данных проекта успешно создан: '{archive_file_path}'[/]")
                data_backup_successful = True
            except Exception as e_tar: console.print(f"[bold red]  ❌ Ошибка при создании архива данных проекта: {e_tar}[/]")
        elif not include_data_dirs: console.print("[yellow]  Не указаны директории для бэкапа данных.[/]")
        else: console.print("[yellow]  Нет валидных директорий данных для бэкапа (все указанные не найдены).[/]")
    else: console.print("\n[dim blue]2. Бэкап Данных Проекта пропущен (директории не указаны).[/dim]")
    
    console.print("\n[bold underline]Итоги создания бэкапа:[/]")
    if include_db:
        if db_backup_successful: console.print("[bold green]  БД: УСПЕШНО[/]")
        else: console.print("[bold red]  БД: ОШИБКА[/]")
    if include_data_dirs: 
        if data_backup_successful: console.print("[bold green]  Данные проекта: УСПЕШНО[/]")
        elif data_to_archive_paths: console.print("[bold red]  Данные проекта: ОШИБКА[/]") 
    if not (include_db or (include_data_dirs and data_to_archive_paths)):
        console.print("[yellow]  Не было выбрано или найдено компонентов для бэкапа.[/]")
        try:
            if current_backup_path.is_dir(): shutil.rmtree(current_backup_path)
            console.print(f"[dim]Пустая/неполная директория бэкапа '{current_backup_path}' удалена.[/dim]")
        except Exception as e_rm: console.print(f"[yellow]Не удалось удалить пустую директорию бэкапа: {e_rm}[/yellow]")
    elif not db_backup_successful and include_db or (include_data_dirs and data_to_archive_paths and not data_backup_successful):
        console.print("[bold red]Создание бэкапа завершилось с ошибками для некоторых компонентов.[/]")
    else: console.print(f"\n[bold green]🎉 Бэкап '{backup_name}' успешно завершен.[/]")

@backup_app.command(name="list", help="Показать список доступных бэкапов SDB.")
def list_backups_cmd():
    backup_base_dir = _get_backup_base_dir()
    if not backup_base_dir: return typer.Exit(code=1)
    backups = [d for d in backup_base_dir.iterdir() if d.is_dir()] 
    if not backups:
        console.print(f"[yellow]Не найдено ни одного бэкапа в директории '{backup_base_dir}'.[/]")
        return
    table = Table(title="[bold cyan]Доступные бэкапы SwiftDevBot[/]", show_header=True, header_style="bold magenta")
    table.add_column("Имя Бэкапа", style="cyan", min_width=25)
    table.add_column("Дата Создания (из имени)", min_width=20)
    table.add_column("Содержит БД?", justify="center")
    table.add_column("Содержит Данные?", justify="center")
    table.add_column("Размер (приблизительно)", justify="right")
    for backup_dir_path in sorted(backups, key=lambda p: p.name, reverse=True):
        backup_name = backup_dir_path.name
        date_from_name = "N/A"
        if backup_name.startswith("sdb_backup_") and len(backup_name.split("_")[-1]) == 15: 
            try:
                ts_str = backup_name.split("_")[-1]
                dt_obj = datetime.strptime(ts_str, '%Y%m%d_%H%M%S')
                date_from_name = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError: pass
        has_db_backup_dir = (backup_dir_path / DB_BACKUP_DIR_NAME).is_dir()
        db_files_exist = any((backup_dir_path / DB_BACKUP_DIR_NAME).iterdir()) if has_db_backup_dir else False
        has_data_backup_dir = (backup_dir_path / DATA_FILES_BACKUP_DIR_NAME).is_dir()
        data_files_exist = any((backup_dir_path / DATA_FILES_BACKUP_DIR_NAME).iterdir()) if has_data_backup_dir else False
        total_size = 0
        try:
            for f_item in backup_dir_path.rglob('*'):
                if f_item.is_file(): total_size += f_item.stat().st_size
            size_str = f"{total_size / (1024*1024):.2f} MB" if total_size > (1024*512) else f"{total_size / 1024:.1f} KB"
        except Exception: size_str = "N/A"
        table.add_row(backup_name, date_from_name, "✅" if db_files_exist else "❌" if has_db_backup_dir else "-", "✅" if data_files_exist else "❌" if has_data_backup_dir else "-", size_str)
    console.print(table)

@backup_app.command(name="restore", help="[ОПАСНО!] Восстановить систему SDB из указанного бэкапа.")
def restore_backup_cmd(
    backup_name: str = typer.Argument(..., help="Имя бэкапа для восстановления (из команды 'sdb backup list')."),
    restore_db: bool = typer.Option(True, "--db/--no-db", help="Восстановить ли базу данных из бэкапа."),
    restore_data_dirs: bool = typer.Option(True, "--data/--no-data", help="Восстановить ли директории данных проекта из бэкапа.")
):
    from core.app_settings import settings 

    console.print(Panel(f"[bold red]ВОССТАНОВЛЕНИЕ ИЗ БЭКАПА: {backup_name}[/]", expand=False, border_style="red"))
    console.print("[bold red]ВНИМАНИЕ: ЭТА ОПЕРАЦИЯ ПЕРЕЗАПИШЕТ ТЕКУЩУЮ БАЗУ ДАННЫХ И/ИЛИ ДАННЫЕ ПРОЕКТА![/]")
    console.print("[bold yellow]Убедитесь, что Telegram-бот SDB ОСТАНОВЛЕН перед началом восстановления.[/]")
    
    if not (restore_db or restore_data_dirs):
        console.print("[yellow]Не выбрано ни одного компонента для восстановления (ни БД, ни данные). Операция отменена.[/yellow]")
        raise typer.Exit()

    base_backup_dir = _get_backup_base_dir()
    if not base_backup_dir: raise typer.Exit(code=1)
    
    target_backup_path = base_backup_dir / backup_name
    if not target_backup_path.is_dir():
        console.print(f"[bold red]Ошибка: Директория бэкапа '{target_backup_path}' не найдена.[/]")
        raise typer.Exit(code=1)

    if not typer.confirm(f"Вы АБСОЛЮТНО уверены, что хотите восстановить систему из бэкапа '{backup_name}'?", abort=True):
        return 
    if not typer.confirm(f"ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ: Это необратимо. Продолжить восстановление?", default=False, abort=True):
        return

    db_restore_successful = False
    data_restore_successful = False
    timestamp_for_files = datetime.now().strftime('%Y%m%d%H%M%S')

    if restore_db:
        console.print("\n[bold blue]1. Восстановление Базы Данных[/]")
        db_settings = settings.db
        backup_db_content_path = target_backup_path / DB_BACKUP_DIR_NAME
        
        if not backup_db_content_path.is_dir() or not any(backup_db_content_path.iterdir()):
            console.print(f"[yellow]  Не найдены файлы бэкапа БД в '{backup_db_content_path}'. Пропуск восстановления БД.[/yellow]")
        else:
            if db_settings.type == "sqlite":
                sqlite_backup_files = list(backup_db_content_path.glob("*.db")) or \
                                      list(backup_db_content_path.glob("*.sqlite")) or \
                                      list(backup_db_content_path.glob("*.sqlite3"))
                if sqlite_backup_files:
                    source_db_file_in_backup = sqlite_backup_files[0]
                    target_current_db_file = Path(db_settings.sqlite_path)
                    console.print(f"  Подготовка к восстановлению SQLite из '{source_db_file_in_backup}' в '{target_current_db_file}'...")
                    if target_current_db_file.exists():
                        current_db_backup_path = target_current_db_file.with_suffix(f"{target_current_db_file.suffix}.before_restore_{timestamp_for_files}")
                        try:
                            shutil.copy2(target_current_db_file, current_db_backup_path)
                            console.print(f"[dim]    Текущий файл БД сохранен в: '{current_db_backup_path}'[/dim]")
                        except Exception as e_backup_current: console.print(f"[yellow]    Не удалось создать бэкап текущего файла БД: {e_backup_current}[/yellow]")
                    try:
                        shutil.copy2(source_db_file_in_backup, target_current_db_file)
                        console.print(f"[green]  ✅ База данных SQLite успешно восстановлена из бэкапа.[/]")
                        db_restore_successful = True
                    except Exception as e_restore_sqlite: console.print(f"[bold red]  ❌ Ошибка при восстановлении SQLite: {e_restore_sqlite}[/]")
                else: console.print(f"[yellow]  Не найден файл бэкапа SQLite (.db, .sqlite, .sqlite3) в '{backup_db_content_path}'.[/yellow]")

            elif db_settings.type == "postgresql":
                pg_restore_path = _find_system_utility("pg_restore")
                backup_file_in_archive = backup_db_content_path / POSTGRES_BACKUP_FILENAME
                if not pg_restore_path: console.print("[bold red]  ❌ Утилита 'pg_restore' не найдена. Восстановление PostgreSQL невозможно.[/]")
                elif not db_settings.pg_dsn: console.print("[bold red]  ❌ DSN для PostgreSQL (pg_dsn) не настроен. Восстановление невозможно.[/]")
                elif not backup_file_in_archive.is_file(): console.print(f"[bold red]  ❌ Файл бэкапа '{POSTGRES_BACKUP_FILENAME}' не найден в '{backup_db_content_path}'.[/]")
                else:
                    parsed_url = urlparse(str(db_settings.pg_dsn))
                    pg_host = parsed_url.hostname if parsed_url.hostname else "localhost"
                    pg_port = str(parsed_url.port) if parsed_url.port is not None else "5432"
                    pg_user = parsed_url.username if parsed_url.username else ""
                    pg_password = parsed_url.password if parsed_url.password else ""
                    pg_database = parsed_url.path.lstrip('/') if parsed_url.path else ""
                    cmd = [ pg_restore_path ]
                    if pg_host: cmd.extend(["-h", pg_host])
                    if pg_port: cmd.extend(["-p", pg_port])
                    if pg_user: cmd.extend(["-U", pg_user])
                    if not pg_database: console.print("[bold red]  ❌ Имя базы данных не найдено в DSN PostgreSQL. Восстановление невозможно.[/]")
                    else:
                        cmd.extend(["-d", pg_database, "--clean", "--if-exists", str(backup_file_in_archive)])
                        env = {}
                        if pg_password: env["PGPASSWORD"] = pg_password
                        console.print(f"  Выполнение pg_restore для PostgreSQL из '{backup_file_in_archive}' в БД '{pg_database}'...")
                        if _execute_system_command(cmd, env_vars=env, show_stdout_on_success=True):
                            console.print(f"[green]  ✅ База данных PostgreSQL успешно восстановлена.[/]")
                            db_restore_successful = True
                        else: console.print(f"[bold red]  ❌ Ошибка при восстановлении PostgreSQL.[/]")
            
            elif db_settings.type == "mysql":
                mysql_path = _find_system_utility("mysql")
                backup_file_in_archive = backup_db_content_path / MYSQL_BACKUP_FILENAME
                if not mysql_path: console.print("[bold red]  ❌ Утилита 'mysql' не найдена. Восстановление MySQL невозможно.[/]")
                elif not db_settings.mysql_dsn: console.print("[bold red]  ❌ DSN для MySQL (mysql_dsn) не настроен. Восстановление невозможно.[/]")
                elif not backup_file_in_archive.is_file(): console.print(f"[bold red]  ❌ Файл бэкапа '{MYSQL_BACKUP_FILENAME}' не найден в '{backup_db_content_path}'.[/]")
                else:
                    parsed_url = urlparse(str(db_settings.mysql_dsn))
                    mysql_host = parsed_url.hostname if parsed_url.hostname else "localhost"
                    mysql_port = str(parsed_url.port) if parsed_url.port is not None else "3306"
                    mysql_user = parsed_url.username if parsed_url.username else ""
                    mysql_password = parsed_url.password if parsed_url.password else ""
                    mysql_database = parsed_url.path.lstrip('/') if parsed_url.path else ""
                    cmd = [ mysql_path ]
                    if mysql_host: cmd.extend(["-h", mysql_host])
                    if mysql_port: cmd.extend(["-P", mysql_port])
                    if mysql_user: cmd.extend(["-u", mysql_user])
                    if not mysql_database: console.print("[bold red]  ❌ Имя базы данных не найдено в DSN MySQL. Восстановление невозможно.[/]")
                    else:
                        cmd.append(mysql_database) 
                        env = {}
                        if mysql_password: env["MYSQL_PWD"] = mysql_password
                        try:
                            sql_dump_content = backup_file_in_archive.read_text(encoding='utf-8')
                            console.print(f"  Выполнение восстановления MySQL из '{backup_file_in_archive}' в БД '{mysql_database}'...")
                            if _execute_system_command(cmd, env_vars=env, input_data=sql_dump_content, show_stdout_on_success=True):
                                console.print(f"[green]  ✅ База данных MySQL успешно восстановлена.[/]")
                                db_restore_successful = True
                            else: console.print(f"[bold red]  ❌ Ошибка при восстановлении MySQL.[/]")
                        except Exception as e_read_sql: console.print(f"[bold red]  ❌ Ошибка чтения SQL-дампа '{backup_file_in_archive}': {e_read_sql}[/]")
            else:
                console.print(f"[bold red]  ❌ Неподдерживаемый тип БД для восстановления: {db_settings.type}[/]")
    else:
        console.print("\n[dim blue]1. Восстановление Базы Данных пропущено.[/dim]")

    if restore_data_dirs:
        console.print(f"\n[bold blue]2. Восстановление Данных Проекта[/]")
        backup_data_archive_dir = target_backup_path / DATA_FILES_BACKUP_DIR_NAME
        target_project_data_dir = settings.core.project_data_path
        if not backup_data_archive_dir.is_dir() or not any(backup_data_archive_dir.iterdir()):
            console.print(f"[yellow]  Не найдены архивы с данными проекта в '{backup_data_archive_dir}'. Пропуск.[/yellow]")
        else:
            data_archives = list(backup_data_archive_dir.glob(f"*{DATA_ARCHIVE_EXTENSION}")) or list(backup_data_archive_dir.glob("*.tar"))
            if data_archives:
                source_data_archive = data_archives[0] 
                console.print(f"  Распаковка архива данных '{source_data_archive}' в '{target_project_data_dir}'...")
                try:
                    temp_extract_path = target_project_data_dir.parent / f"__{target_project_data_dir.name}_restore_temp_{timestamp_for_files}"
                    temp_extract_path.mkdir(parents=True, exist_ok=True)
                    with tarfile.open(source_data_archive, "r:*") as tar: tar.extractall(path=str(temp_extract_path))
                    console.print(f"[dim]    Содержимое архива распаковано во временную папку: {temp_extract_path}[/dim]")
                    console.print(f"[dim]    Перемещение/копирование в целевую директорию: {target_project_data_dir} ...[/dim]")
                    for item_in_temp in temp_extract_path.iterdir():
                        target_item_path = target_project_data_dir / item_in_temp.name
                        if item_in_temp.is_dir():
                            if target_item_path.exists(): shutil.rmtree(target_item_path)
                            shutil.move(str(item_in_temp), str(target_item_path))
                        elif item_in_temp.is_file(): shutil.move(str(item_in_temp), str(target_item_path)) 
                    shutil.rmtree(temp_extract_path) 
                    console.print(f"[green]  ✅ Данные проекта успешно восстановлены из архива.[/]")
                    data_restore_successful = True
                except tarfile.ReadError as e_tar_read: console.print(f"[bold red]  ❌ Ошибка чтения архива данных '{source_data_archive}': {e_tar_read}[/]")
                except Exception as e_restore_data:
                    console.print(f"[bold red]  ❌ Ошибка при восстановлении данных проекта: {e_restore_data}[/]")
                    if 'temp_extract_path' in locals() and temp_extract_path.exists():
                         try: shutil.rmtree(temp_extract_path)
                         except Exception: pass
            else: console.print(f"[yellow]  Не найден архив данных (.tar.gz или .tar) в '{backup_data_archive_dir}'.[/yellow]")
    else: console.print("\n[dim blue]2. Восстановление Данных Проекта пропущено.[/dim]")

    console.print("\n[bold underline]Итоги восстановления:[/]")
    if restore_db:
        if db_restore_successful: console.print("[bold green]  БД: УСПЕШНО[/]")
        else: console.print("[bold red]  БД: ОШИБКА или НЕ ВЫПОЛНЕНО[/]")
    if restore_data_dirs:
        if data_restore_successful: console.print("[bold green]  Данные проекта: УСПЕШНО[/]")
        else: console.print("[bold red]  Данные проекта: ОШИБКА или НЕ ВЫПОЛНЕНО[/]")
    if not db_restore_successful and restore_db or (not data_restore_successful and restore_data_dirs):
        console.print("[bold red]Восстановление завершилось с ошибками для некоторых компонентов.[/]")
    elif not restore_db and not restore_data_dirs: pass 
    else:
        console.print(f"\n[bold green]🎉 Восстановление из бэкапа '{backup_name}' успешно завершено для выбранных компонентов.[/]")
        console.print("[yellow]Не забудьте проверить конфигурацию и, возможно, перезапустить бота, если он был запущен во время восстановления.[/yellow]")
        console.print("[yellow]Если восстанавливалась БД, может потребоваться `alembic stamp head` или проверка миграций.[/yellow]")