# --- НАЧАЛО ФАЙЛА sdb.py (и sdb) ---
#!/usr/bin/env python3

import sys
from pathlib import Path

# Гарантируем, что корень проекта в sys.path
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import typer
    from rich.console import Console
except ImportError as e:
    print(f"Критическая ошибка: Typer или Rich не установлены. {e}", file=sys.stderr)
    print(f"Пожалуйста, установите зависимости: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Создаем главный CLI-объект
cli_main_app = typer.Typer(
    name="sdb",
    help="🚀 [bold cyan]SwiftDevBot CLI[/] - Утилита для управления вашим SDB!",
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Импортируем и регистрируем все команды и группы
try:
    # Группы команд (Typer-приложения)
    from cli.config import config_app
    from cli.db import db_app
    from cli.module import module_app
    from cli.user import user_app
    from cli.backup import backup_app
    from cli.system import system_app
    from cli.bot import bot_app
    from cli.monitor import monitor_app
    from cli.utils import utils_app
    from cli.security import security_app
    from cli.notifications import notifications_app
    
    cli_main_app.add_typer(config_app, name="config", help="🔧 Управление конфигурацией.")
    cli_main_app.add_typer(db_app, name="db", help="🗄️ Управление базой данных.")
    cli_main_app.add_typer(module_app, name="module", help="🧩 Управление модулями.")
    cli_main_app.add_typer(user_app, name="user", help="👤 Управление пользователями.")
    cli_main_app.add_typer(backup_app, name="backup", help="💾 Управление бэкапами.")
    cli_main_app.add_typer(system_app, name="system", help="🛠️ Системные команды.")
    cli_main_app.add_typer(bot_app, name="bot", help="🤖 Взаимодействие с Bot API.")
    cli_main_app.add_typer(monitor_app, name="monitor", help="📊 Мониторинг и аналитика.")
    cli_main_app.add_typer(utils_app, name="utils", help="🛠️ Утилитарные инструменты.")
    cli_main_app.add_typer(security_app, name="security", help="🔒 Управление безопасностью.")
    cli_main_app.add_typer(notifications_app, name="notifications", help="🔔 Управление уведомлениями.")

    # Отдельные команды
    from cli.run import run_command
    from cli.process import stop_command, status_command, restart_command

    # Регистрируем команды верхнего уровня
    cli_main_app.command("run")(run_command)
    cli_main_app.command("start", help="🚀 Псевдоним для 'run'.")(run_command)
    cli_main_app.command("stop", help="🚦 Остановить процесс бота.")(stop_command)
    cli_main_app.command("status", help="🚦 Показать статус процесса.")(status_command)
    cli_main_app.command("restart", help="🚦 Перезапустить процесс бота.")(restart_command)

except ImportError as e:
    console = Console()
    console.print(f"[bold red]Ошибка импорта CLI компонентов:[/]\n {e}")
    console.print("Убедитесь, что структура папки 'cli/' корректна и все файлы на месте.")
    sys.exit(1)


if __name__ == "__main__":
    cli_main_app()
# --- КОНЕЦ ФАЙЛА sdb.py (и sdb) ---