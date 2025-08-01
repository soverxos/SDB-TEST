# --- НАЧАЛО ФАЙЛА cli/config.py ---
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from dotenv import set_key, find_dotenv

from .utils import confirm_action

# Глобальная консоль, будет инициализирована в sdb.py
sdb_console = Console()

# --- Typer App для группы команд 'config' ---
config_app = typer.Typer(
    name="config",
    help="🔧 Управление конфигурацией SwiftDevBot (инициализация, просмотр, изменение).",
    rich_markup_mode="rich",
    no_args_is_help=True
)

# --- Константы ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_CONFIG_DIR_NAME = "Config"
USER_CORE_CONFIG_FILENAME = "core_settings.yaml"
USER_MODULES_CONFIG_DIR_NAME = "modules_settings"
ENV_FILENAME = ".env"

# --- Вспомогательные функции ---

def _update_env_file(key: str, value: str) -> bool:
    """Безопасно находит и обновляет .env файл."""
    env_path = find_dotenv(filename=ENV_FILENAME, usecwd=True, raise_error_if_not_found=False)
    if not env_path:
        env_path = PROJECT_ROOT / ENV_FILENAME
        sdb_console.print(f"[dim]Файл .env не найден, будет создан новый: {env_path}[/dim]")
        env_path.touch()

    try:
        set_key(dotenv_path=env_path, key_to_set=key, value_to_set=value)
        sdb_console.print(f"[green]✓[/] Переменная [cyan]{key}[/] сохранена в [yellow]{env_path}[/yellow]")
        return True
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка при записи в .env файл ({env_path}): {e}[/bold red]")
        return False

def _get_project_data_path() -> Path:
    """Получает путь к project_data, даже если настройки еще не загружены."""
    from core.app_settings import CoreAppSettings
    # Используем путь по умолчанию из модели Pydantic, чтобы не зависеть от загруженных настроек
    default_path = CoreAppSettings.model_fields['project_data_path'].default
    return (PROJECT_ROOT / default_path).resolve()


# --- Команды CLI ---

@config_app.command(name="init", help="Интерактивная настройка бота и создание файлов конфигурации.")
def init_command(
    force: bool = typer.Option(False, "--force", "-f", help="Принудительно перезаписать существующие конфиги (с бэкапом).")
):
    """Запускает интерактивный визард для первоначальной настройки бота."""
    sdb_console.print(Panel("🤖 [bold cyan]Интерактивный настройщик SwiftDevBot[/]",
                        subtitle="Давайте настроим вашего бота шаг за шагом!", expand=False))
    
    # 1. Токен Бота
    sdb_console.print("\n--- [bold]Шаг 1: Токен Telegram Бота[/bold] ---")
    sdb_console.print("Получите токен у @BotFather в Telegram.")
    bot_token = typer.prompt("🔑 Пожалуйста, введите ваш BOT_TOKEN", hide_input=False) # hide_input=True не работает в некоторых терминалах
    if not bot_token or len(bot_token.split(':')) != 2:
        sdb_console.print("[bold red]Ошибка: Токен выглядит некорректно. Настройка прервана.[/bold red]")
        raise typer.Exit(1)
    _update_env_file("BOT_TOKEN", bot_token)

    # 2. Настройка Базы Данных
    sdb_console.print("\n--- [bold]Шаг 2: База Данных[/bold] ---")
    db_type_choice = typer.prompt(
        "🗄️ Выберите тип базы данных:\n[1] sqlite (рекомендуется для простого старта)\n[2] postgresql\n[3] mysql\n> Введите номер",
        default="1", show_choices=False
    )
    
    db_config: Dict[str, Any] = {}
    env_vars_to_set: Dict[str, str] = {}

    if db_type_choice == "1":
        db_config['type'] = "sqlite"
        default_path = "project_data/Database_files/swiftdevbot.db"
        sqlite_path = typer.prompt(f"📁 Путь к файлу SQLite (относительно корня проекта)", default=default_path)
        env_vars_to_set['SDB_DB_TYPE'] = 'sqlite'
        env_vars_to_set['SDB_DB_SQLITE_PATH'] = sqlite_path
    
    elif db_type_choice in ["2", "3"]:
        db_type = "postgresql" if db_type_choice == "2" else "mysql"
        default_port = "5432" if db_type == "postgresql" else "3306"
        sdb_console.print(f"--- [bold]Настройка {db_type.capitalize()}[/bold] ---")
        
        host = typer.prompt("🌐 Хост (IP-адрес или домен)", default="localhost")
        port = typer.prompt("🚪 Порт", default=default_port)
        user = typer.prompt("👤 Имя пользователя (логин)")
        password = typer.prompt("🔒 Пароль", hide_input=True)
        dbname = typer.prompt("💾 Имя базы данных")
        
        driver = "psycopg" if db_type == "postgresql" else "aiomysql"
        dsn = f"{db_type}+{driver}://{user}:{password}@{host}:{port}/{dbname}"
        if db_type == "mysql":
            dsn += "?charset=utf8mb4"

        env_vars_to_set['SDB_DB_TYPE'] = db_type
        if db_type == "postgresql":
            env_vars_to_set['SDB_DB_PG_DSN'] = dsn
        else:
            env_vars_to_set['SDB_DB_MYSQL_DSN'] = dsn
    else:
        sdb_console.print("[bold red]Неверный выбор. Настройка прервана.[/bold red]")
        raise typer.Exit(1)
        
    for key, value in env_vars_to_set.items():
        _update_env_file(key, value)

    # 3. Супер-Администратор
    sdb_console.print("\n--- [bold]Шаг 3: Супер-Администратор[/bold] ---")
    sdb_console.print("Это пользователь с полными правами, который может настраивать все остальное.")
    super_admin_id = typer.prompt("👑 Введите ваш Telegram ID (числовой)")
    if not super_admin_id.isdigit():
        sdb_console.print("[bold red]Ошибка: Telegram ID должен быть числом. Настройка прервана.[/bold red]")
        raise typer.Exit(1)
    _update_env_file("SDB_CORE_SUPER_ADMINS", super_admin_id)

    # 4. Создание core_settings.yaml
    project_data_path = _get_project_data_path()
    user_config_dir = project_data_path / USER_CONFIG_DIR_NAME
    user_config_file_path = user_config_dir / USER_CORE_CONFIG_FILENAME
    
    user_config_dir.mkdir(parents=True, exist_ok=True)

    if user_config_file_path.exists() and not force:
        sdb_console.print(f"[yellow]Файл {user_config_file_path} уже существует. Используйте --force для перезаписи.[/yellow]")
    else:
        # В этой версии init мы сохраняем почти всё в .env, 
        # поэтому core_settings.yaml может быть почти пустым,
        # он будет использовать значения по умолчанию.
        # Можно добавить сюда не-секретные настройки.
        core_settings_data = {
            'core': {
                'log_level': 'INFO',
                'log_to_file': True
            }
        }
        try:
            with open(user_config_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(core_settings_data, f, indent=2, sort_keys=False)
            sdb_console.print(f"[green]✓[/] Файл конфигурации [yellow]{user_config_file_path}[/yellow] создан/обновлен.")
        except Exception as e:
            sdb_console.print(f"[bold red]Ошибка при записи файла {user_config_file_path}: {e}[/bold red]")
    
    sdb_console.print(Panel("✅ [bold green]Настройка успешно завершена![/]", expand=False, border_style="green"))
    sdb_console.print("💡 [bold]Следующие шаги:[/bold]")
    sdb_console.print("   1. Примените миграции базы данных: [cyan]sdb db upgrade head[/cyan]")
    sdb_console.print("   2. Запустите бота: [cyan]sdb run[/cyan]")


@config_app.command(name="get", help="Показать всю конфигурацию или значение конкретного ключа.")
def get_command(
    key: Optional[str] = typer.Argument(None, help="Ключ для получения (например, 'db.type' или 'core.super_admins')."),
    show_defaults: bool = typer.Option(False, "--show-defaults", help="Показать значения по умолчанию.")
):
    """Отображает текущую активную конфигурацию SDB."""
    try:
        from core.app_settings import settings
    except Exception as e:
        sdb_console.print(f"[bold red]Ошибка при загрузке настроек: {e}[/bold red]")
        raise typer.Exit(1)
        
    if key is None:
        # Показываем всю конфигурацию
        sdb_console.print(Panel("[bold cyan]Текущая активная конфигурация SwiftDevBot[/]", expand=False))
        config_dict = settings.model_dump(mode='json', exclude_defaults=not show_defaults)
        yaml_output = yaml.dump(config_dict, indent=2, allow_unicode=True, sort_keys=False)
        sdb_console.print(Syntax(yaml_output, "yaml", theme="native", line_numbers=True))
    else:
        # Показываем значение конкретного ключа
        try:
            value = settings
            for part in key.split('.'):
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = getattr(value, part)
            
            if isinstance(value, (dict, list, tuple)) or hasattr(value, 'model_dump'):
                if hasattr(value, 'model_dump'):
                    value = value.model_dump(mode='json')
                yaml_output = yaml.dump(value, indent=2, allow_unicode=True)
                sdb_console.print(f"Значение для ключа [cyan]{key}[/]:")
                sdb_console.print(Syntax(yaml_output, "yaml", theme="native"))
            else:
                sdb_console.print(f"Значение для ключа [cyan]{key}[/]: [bold green]{value}[/bold green]")

        except (AttributeError, KeyError):
            sdb_console.print(f"[bold red]Ошибка: Ключ '{key}' не найден в конфигурации.[/bold red]")
            raise typer.Exit(1)

# Команды 'set' и 'set-module' требуют более сложной логики для безопасного изменения YAML.
# Пока что их можно опустить, чтобы не усложнять, или добавить в следующей итерации.
# Если вы хотите их сейчас, я могу написать упрощенную версию.

if __name__ == "__main__":
    config_app()
# --- КОНЕЦ ФАЙЛА cli/config.py ---