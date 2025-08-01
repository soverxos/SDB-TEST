# --- НАЧАЛО ФАЙЛА cli/run.py ---
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

import typer
from loguru import logger as global_logger
from rich.panel import Panel

from .process import PID_FILENAME, _is_process_running # Импортируем из соседнего файла

sdb_console = None  # Будет инициализирована в sdb.py

def run_command(
    debug: bool = typer.Option(
        False, "--debug", "-d",
        help="Запустить бота в режиме отладки (увеличит уровень логирования до DEBUG)."
    ),
    background: bool = typer.Option(
        False, "--background", "-b",
        help="Запустить бота в фоновом режиме (демонизировать)."
    )
):
    """
    🚀 Запускает основной процесс Telegram бота SDB.
    """
    # Импортируем здесь, чтобы избежать циклических зависимостей и ускорить запуск CLI
    from core.app_settings import settings
    from core.bot_entrypoint import run_sdb_bot
    
    global sdb_console
    if sdb_console is None:
        from rich.console import Console
        sdb_console = Console()

    project_root = Path(__file__).resolve().parent.parent
    pid_file_path = settings.core.project_data_path / PID_FILENAME

    if pid_file_path.exists():
        try:
            with open(pid_file_path, "r") as f:
                pid = int(f.read().strip())
            if _is_process_running(pid):
                sdb_console.print(f"[yellow]SDB бот уже запущен (PID: {pid}). Используйте 'sdb stop' для остановки.[/yellow]")
                raise typer.Exit(code=1)
        except (OSError, ValueError):
            sdb_console.print(f"[yellow]Обнаружен устаревший PID-файл ({pid_file_path}). Удаление...[/yellow]")
            pid_file_path.unlink(missing_ok=True)
        except Exception as e_pid_check:
             sdb_console.print(f"[red]Ошибка при проверке PID-файла: {e_pid_check}[/red]")

    if debug:
        sdb_console.print(Panel(f"[bold yellow]Запрос на запуск бота в режиме DEBUG.[/]",
                                title="SDB Run (Debug Mode Requested)", expand=False, border_style="yellow"))
        os.environ["SDB_LAUNCH_DEBUG_MODE"] = "true"
    else:
        os.environ["SDB_LAUNCH_DEBUG_MODE"] = "false"

    if background:
        if sys.platform == "win32":
            sdb_console.print("[bold red]Фоновый режим (-b/--background) пока не поддерживается на Windows через эту команду.[/bold red]")
            sdb_console.print("Пожалуйста, запустите бота без флага -b или используйте другие средства для демонизации.")
            raise typer.Exit(code=1)

        sdb_console.print(Panel("[bold blue]Запуск SDB бота в фоновом режиме...[/]",
                                title="SDB Run (Background)", expand=False, border_style="blue"))
        
        run_bot_script_path = project_root / "run_bot.py"
        
        env_for_subprocess = os.environ.copy()
        env_for_subprocess["SDB_SHOULD_WRITE_PID"] = "true"
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(run_bot_script_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=env_for_subprocess
            )
            sdb_console.print(f"Процесс бота запущен в фоне (системный PID: {process.pid}).")
            sdb_console.print(f"Ожидание создания PID-файла '{PID_FILENAME}' (до 10 секунд)...")
            
            pid_file_created_successfully = False
            for i in range(10):
                time.sleep(1)
                if pid_file_path.exists():
                    try:
                        actual_pid_from_file_str = pid_file_path.read_text().strip()
                        if actual_pid_from_file_str.isdigit():
                            actual_pid_from_file = int(actual_pid_from_file_str)
                            sdb_console.print(f"[green]PID-файл {pid_file_path} создан. PID бота: {actual_pid_from_file}.[/green]")
                            sdb_console.print("Для просмотра статуса используйте: [cyan]sdb status[/cyan]")
                            sdb_console.print("Для остановки используйте: [cyan]sdb stop[/cyan]")
                            pid_file_created_successfully = True
                            break
                    except (ValueError, IOError) as e_read_pid:
                         sdb_console.print(f"[yellow]Ошибка чтения PID из файла ({e_read_pid}). Попытка {i+1}/10.[/yellow]")

            if not pid_file_created_successfully:
                sdb_console.print(f"[yellow]Предупреждение: PID-файл не был корректно создан/прочитан в течение 10 секунд.[/yellow]")
                sdb_console.print(f"  Возможно, бот не запустился корректно. Проверьте логи.")
                sdb_console.print(f"  Системный PID: {process.pid}. Проверьте его статус вручную.")

        except Exception as e_popen:
            sdb_console.print(f"[bold red]Ошибка при запуске бота в фоновом режиме: {e_popen}[/bold red]")
            raise typer.Exit(code=1)
    else:
        if not debug:
             sdb_console.print(Panel("[bold green]Запуск Telegram бота SDB...[/]",
                                title="SDB Run", expand=False, border_style="green"))
        try:
            os.environ["SDB_SHOULD_WRITE_PID"] = "false"
            
            bot_coroutine = run_sdb_bot()
            exit_code = asyncio.run(bot_coroutine)
            
            if exit_code != 0:
                sdb_console.print(f"[bold red]Бот завершил работу с кодом ошибки: {exit_code}[/]")
                sys.exit(exit_code)
            else:
                 sdb_console.print("[bold green]Бот успешно завершил свою работу.[/]")
                
        except KeyboardInterrupt:
            sdb_console.print("\n[bold orange_red1]🤖 Бот остановлен пользователем (Ctrl+C).[/]")
            sys.exit(0)
        except Exception as e:
            sdb_console.print(Panel(f"[bold red]КРИТИЧЕСКАЯ ОШИБКА:[/]\n{e}",
                                    title="SDB Runtime Error", border_style="red", expand=True))
            global_logger.opt(exception=e).critical("Необработанное исключение в cli/run.py")
            sys.exit(1)
# --- КОНЕЦ ФАЙЛА cli/run.py ---