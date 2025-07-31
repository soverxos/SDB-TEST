# cli_commands/setup_cmd.py

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax # Для красивого вывода конфига
import yaml # Для работы с YAML файлами
import json # Для возможного вывода в JSON
import shutil # Для копирования файлов
import re # Для работы с регулярными выражениями
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Создаем свою консоль для этого модуля
console = Console()


def merge_yaml_configs(template_path: Path, user_config_path: Path) -> bool:
    """
    Объединяет шаблон конфигурации с пользовательским файлом.
    Новые ключи из шаблона добавляются, существующие значения пользователя сохраняются.
    """
    try:
        # Загружаем шаблон
        with open(template_path, 'r', encoding='utf-8') as f:
            template_config = yaml.safe_load(f) or {}
        
        # Загружаем пользовательскую конфигурацию
        with open(user_config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        
        # Функция рекурсивного слияния
        def deep_merge(template: dict, user: dict) -> dict:
            result = user.copy()
            for key, value in template.items():
                if key not in result:
                    # Новый ключ из шаблона - добавляем
                    result[key] = value
                    console.print(f"[green]+ Добавлен новый параметр: {key}[/green]")
                elif isinstance(value, dict) and isinstance(result[key], dict):
                    # Рекурсивно обрабатываем вложенные объекты
                    result[key] = deep_merge(value, result[key])
                elif key in result:
                    # Если ключ уже существует, но значения разные, показываем предупреждение
                    if result[key] != value:
                        console.print(f"[yellow]⚠️ Параметр {key} уже существует с другим значением[/yellow]")
            return result
        
        # Очищаем дублирующиеся секции
        cleaned_user_config = clean_duplicate_sections(user_config)
        
        # Объединяем конфигурации
        merged_config = deep_merge(template_config, cleaned_user_config)
        
        # Финальная очистка дубликатов в объединенной конфигурации
        final_config = clean_duplicate_sections(merged_config)
        
        # Создаем backup
        backup_path = user_config_path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        shutil.copy2(user_config_path, backup_path)
        console.print(f"[blue]Создан backup: {backup_path}[/blue]")
        
        # Сохраняем объединенную конфигурацию
        with open(user_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(final_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        return True
        
    except Exception as e:
        console.print(f"[red]Ошибка при слиянии конфигураций: {e}[/red]")
        return False


def clean_duplicate_sections(config: dict) -> dict:
    """Очищает дублирующиеся секции в конфигурации."""
    cleaned = {}
    
    # Правила для обработки дубликатов
    duplicate_rules = {
        'db': 'database',        # Заменяем 'db' на 'database'
        'bot': 'telegram',       # Заменяем 'bot' на 'telegram'
    }
    
    # Сначала обрабатываем секции, которые нужно переименовать
    for key, value in list(config.items()):
        if key in duplicate_rules:
            target_key = duplicate_rules[key]
            if target_key in config:
                # Если целевая секция уже существует, объединяем их
                if isinstance(value, dict) and isinstance(config[target_key], dict):
                    merged_value = {**config[target_key], **value}
                    cleaned[target_key] = merged_value
                    console.print(f"[yellow]⚠️ Объединены секции: {key} → {target_key}[/yellow]")
                else:
                    # Если не словари, используем значение из приоритетной секции
                    cleaned[target_key] = config[target_key]
                    console.print(f"[yellow]⚠️ Пропущена секция {key} в пользу {target_key}[/yellow]")
            else:
                # Переименовываем секцию
                cleaned[target_key] = value
                console.print(f"[green]✓ Переименована секция: {key} → {target_key}[/green]")
        elif key not in cleaned:
            # Очищаем дублирующиеся поля внутри секций
            if isinstance(value, dict):
                cleaned_value = {}
                seen_fields = set()
                for field_key, field_value in value.items():
                    if field_key not in seen_fields:
                        cleaned_value[field_key] = field_value
                        seen_fields.add(field_key)
                    else:
                        console.print(f"[yellow]⚠️ Пропущено дублирующееся поле: {key}.{field_key}[/yellow]")
                cleaned[key] = cleaned_value
            else:
                cleaned[key] = value
    
    return cleaned


def parse_env_file(env_path: Path) -> Dict[str, str]:
    """Парсит .env файл и возвращает словарь переменных."""
    env_vars = {}
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            console.print(f"[yellow]Ошибка чтения .env файла: {e}[/yellow]")
    return env_vars


def write_env_file(env_path: Path, env_vars: Dict[str, str]) -> bool:
    """Записывает переменные в .env файл."""
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# .env - Чувствительные данные SwiftDevBot\n")
            f.write("# ⚠️ НЕ КОММИТЬТЕ ЭТОТ ФАЙЛ В GIT!\n\n")
            
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        console.print(f"[red]Ошибка записи .env файла: {e}[/red]")
        return False


def extract_env_variables_from_template(template_path: Path) -> Dict[str, str]:
    """Извлекает переменные окружения из шаблона config.yaml."""
    env_vars = {}
    if not template_path.exists():
        return env_vars
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем комментарии с переменными окружения
        env_pattern = r'#\s*([A-Z_]+)\s+в\s+\.env'
        matches = re.findall(env_pattern, content)
        
        # Добавляем стандартные переменные
        standard_vars = [
            "BOT_TOKEN",
            "SUPER_ADMIN_IDS", 
            "DB_PG_DSN",
            "DB_MYSQL_DSN",
            "REDIS_URL",
            "WEB_SERVER_EXTERNAL_HOST",
            "WEB_SERVER_EXTERNAL_PORT"
        ]
        
        for var in standard_vars:
            if var not in env_vars:
                env_vars[var] = ""
                
    except Exception as e:
        console.print(f"[yellow]Ошибка извлечения переменных из шаблона: {e}[/yellow]")
    
    return env_vars


def handle_env_file(env_path: Path, template_path: Path, create_env: bool, update_env: bool) -> None:
    """Обрабатывает .env файл - создает или обновляет его."""
    existing_env_vars = parse_env_file(env_path)
    template_env_vars = extract_env_variables_from_template(template_path)
    
    if create_env and not env_path.exists():
        # Создаем новый .env файл
        console.print(f"[cyan]Создание нового .env файла: {env_path}[/cyan]")
        
        # Запрашиваем обязательные переменные
        bot_token = typer.prompt("Введите токен Telegram бота (BOT_TOKEN)")
        super_admin_ids = typer.prompt("Введите ID супер-администраторов через запятую (SUPER_ADMIN_IDS)")
        
        env_vars = {
            "BOT_TOKEN": bot_token,
            "SUPER_ADMIN_IDS": super_admin_ids
        }
        
        # Добавляем опциональные переменные
        for var in template_env_vars:
            if var not in env_vars:
                value = typer.prompt(f"Введите {var} (или оставьте пустым)", default="")
                if value:
                    env_vars[var] = value
        
        if write_env_file(env_path, env_vars):
            console.print(f"[green]✅ .env файл успешно создан![/green]")
        else:
            console.print(f"[red]❌ Ошибка создания .env файла[/red]")
    
    elif update_env and env_path.exists():
        # Обновляем существующий .env файл
        console.print(f"[cyan]Обновление .env файла: {env_path}[/cyan]")
        
        # Добавляем новые переменные из шаблона
        updated_vars = existing_env_vars.copy()
        for var in template_env_vars:
            if var not in updated_vars:
                value = typer.prompt(f"Добавить {var}?", default="")
                if value:
                    updated_vars[var] = value
        
        if write_env_file(env_path, updated_vars):
            console.print(f"[green]✅ .env файл успешно обновлен![/green]")
        else:
            console.print(f"[red]❌ Ошибка обновления .env файла[/red]")


def sync_config_with_env_and_template(user_config_path: Path, env_path: Path, template_path: Path) -> None:
    """Синхронизирует пользовательскую конфигурацию с .env и шаблоном."""
    console.print("[cyan]Синхронизация конфигурации...[/cyan]")
    
    # Загружаем текущие конфигурации
    env_vars = parse_env_file(env_path)
    template_config = {}
    user_config = {}
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template_config = yaml.safe_load(f) or {}
    
    if user_config_path.exists():
        with open(user_config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
    
    # Создаем backup
    if user_config_path.exists():
        backup_path = user_config_path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        shutil.copy2(user_config_path, backup_path)
        console.print(f"[blue]Создан backup: {backup_path}[/blue]")
    
    # Объединяем конфигурации
    merged_config = deep_merge_configs(template_config, user_config)
    
    # Сохраняем обновленную конфигурацию
    with open(user_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(merged_config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    console.print(f"[green]✅ Конфигурация синхронизирована![/green]")


def deep_merge_configs(template: dict, user: dict) -> dict:
    """Рекурсивно объединяет конфигурации."""
    result = user.copy()
    for key, value in template.items():
        if key not in result:
            result[key] = value
            console.print(f"[green]+ Добавлен новый параметр: {key}[/green]")
        elif isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = deep_merge_configs(value, result[key])
    return result


# Typer-приложение для команд группы 'config' (ранее setup_app)
# Переименовал setup_app в config_app для ясности, что это группа команд "config"
config_app = typer.Typer(
    name="config", 
    help="🔧 Управление конфигурацией SwiftDevBot (инициализация, просмотр).",
    rich_markup_mode="rich"
)

# Определяем корень проекта относительно текущего файла
# cli_commands/setup_cmd.py -> cli_commands -> SDB_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_TEMPLATE_NAME = "config.yaml" # Шаблон в корне проекта
USER_CONFIG_DIR_NAME_IN_PROJECT_DATA = "Config" # Имя папки Config внутри project_data
USER_CONFIG_FILENAME = "core_settings.yaml" # Имя пользовательского конфига

@config_app.command(name="init", help="Инициализировать или обновить файл конфигурации пользователя.")
def setup_config_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Принудительно перезаписать существующий конфиг (с созданием бэкапа)."),
    update_env: bool = typer.Option(False, "--update-env", "-e", help="Обновить .env файл с новыми переменными из шаблона."),
    create_env: bool = typer.Option(False, "--create-env", help="Создать .env файл, если он не существует.")
):
    """
    Создает или обновляет пользовательский файл конфигурации 'core_settings.yaml'
    в директории 'project_data/Config/' на основе шаблона 'config.yaml' из корня проекта.
    Также может обновить .env файл с новыми переменными.
    """
    console.print(Panel("[bold cyan]Инициализация конфигурации SwiftDevBot[/]", expand=False, border_style="cyan"))

    try:
        # Импортируем настройки SDB, чтобы получить путь к project_data
        from core.app_settings import settings, PROJECT_ROOT_DIR # settings уже загружены, если sdb.py их импортировал
        
        project_data_path = settings.core.project_data_path
        user_config_dir = project_data_path / USER_CONFIG_DIR_NAME_IN_PROJECT_DATA
        user_config_file_path = user_config_dir / USER_CONFIG_FILENAME
        template_config_path = PROJECT_ROOT_DIR / DEFAULT_CONFIG_TEMPLATE_NAME
        env_file_path = PROJECT_ROOT_DIR / ".env"

        user_config_dir.mkdir(parents=True, exist_ok=True) # Создаем директорию, если ее нет

        if not template_config_path.exists():
            console.print(f"[bold red]Ошибка: Шаблон конфигурации '{template_config_path}' не найден.[/]")
            console.print("Убедитесь, что файл 'config.yaml' существует в корне проекта.")
            raise typer.Exit(code=1)

        # Обработка .env файла
        if create_env or update_env:
            handle_env_file(env_file_path, template_config_path, create_env, update_env)

        if user_config_file_path.exists():
            console.print(f"[yellow]Обнаружен существующий файл конфигурации: '{user_config_file_path}'[/]")
            if force:
                should_overwrite = True
                console.print("[yellow]Опция --force: существующий конфиг будет перезаписан (с бэкапом).[/]")
            else:
                # Спрашиваем пользователя, что делать
                console.print("\n[cyan]Выберите действие:[/cyan]")
                console.print("1. Перезаписать (создать backup)")
                console.print("2. Обновить/дополнить (слияние конфигураций)")
                console.print("3. Синхронизировать с .env и config.yaml")
                console.print("4. Отмена")
                
                choice = typer.prompt("Ваш выбор", type=int, default=4)
                
                if choice == 1:
                    should_overwrite = True
                elif choice == 2:
                    # Реализуем слияние YAML конфигураций
                    should_overwrite = merge_yaml_configs(template_config_path, user_config_file_path)
                    if should_overwrite:
                        console.print("[green]Конфигурации успешно объединены![/green]")
                        return
                    else:
                        console.print("[red]Ошибка при объединении конфигураций.[/red]")
                        raise typer.Exit(code=1)
                elif choice == 3:
                    # Синхронизация с .env и config.yaml
                    sync_config_with_env_and_template(user_config_file_path, env_file_path, template_config_path)
                    console.print("[green]Конфигурация синхронизирована с .env и config.yaml![/green]")
                    return
                elif choice == 4:
                    console.print("[bold green]Операция отменена пользователем.[/]")
                    return
                else:
                    console.print("[red]Неверный выбор, операция отменена.[/red]")
                    raise typer.Exit(code=1)
                
                if choice == 1 and not typer.confirm(f"Подтвердите перезапись файла '{user_config_file_path}'?", default=False):
                    console.print("[bold green]Операция отменена пользователем.[/]")
                    return
                should_overwrite = True
            
            if should_overwrite:
                backup_path = user_config_file_path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
                try:
                    shutil.copy2(user_config_file_path, backup_path) # copy2 сохраняет метаданные
                    console.print(f"[green]Создан бэкап старого конфига: '{backup_path}'[/]")
                except Exception as e_backup:
                    console.print(f"[bold red]Ошибка создания бэкапа для '{user_config_file_path}': {e_backup}[/]")
                    if not typer.confirm("Продолжить перезапись без бэкапа?", default=False):
                        raise typer.Exit()
                
                # Удаляем старый файл перед копированием нового, чтобы избежать проблем с правами/слиянием
                user_config_file_path.unlink(missing_ok=True) 
        
        # Копируем шаблон в пользовательский конфиг
        try:
            shutil.copy2(template_config_path, user_config_file_path)
            console.print(f"[bold green]Файл конфигурации успешно создан/обновлен: '{user_config_file_path}'[/]")
            console.print(f"Пожалуйста, отредактируйте этот файл, указав ваши настройки.")
            console.print(f"Не забудьте также создать файл '.env' в корне проекта и указать в нем чувствительные данные.")
        except Exception as e_copy:
            console.print(f"[bold red]Ошибка копирования шаблона '{template_config_path}' в '{user_config_file_path}': {e_copy}[/]")
            raise typer.Exit(code=1)

    except ImportError:
        console.print(f"[bold red]Ошибка: Не удалось импортировать 'core.app_settings'.[/]")
        console.print("Убедитесь, что SDB установлен корректно и вы запускаете команду из корня проекта.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Произошла непредвиденная ошибка: {e}[/]")
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)

@config_app.command(name="info", help="Показать текущую активную конфигурацию SDB.")
def show_info_cmd(
    show_defaults: bool = typer.Option(False, "--show-defaults", help="Включить в вывод значения по умолчанию (для Pydantic моделей)."),
    output_format: str = typer.Option("rich", "--format", "-fmt", help="Формат вывода: 'rich', 'yaml' или 'json'.", 
                                       case_sensitive=False, show_choices=True),
    compact: bool = typer.Option(False, "--compact", "-c", help="Компактный вывод без детальной информации.")
):
    """
    Отображает текущую загруженную конфигурацию SwiftDevBot в красивом формате,
    объединяя значения из файла настроек, переменных окружения и дефолтов.
    """
    output_format = output_format.lower()
    if output_format not in ["rich", "yaml", "json"]:
        console.print(f"[bold red]Ошибка: Неподдерживаемый формат вывода '{output_format}'. Доступны: 'rich', 'yaml', 'json'.[/]")
        raise typer.Exit(code=1)

    try:
        from core.app_settings import settings # Загружаем уже инициализированные настройки

        if output_format == "rich":
            show_rich_config_info(settings, show_defaults, compact)
        else:
            show_raw_config_info(settings, show_defaults, output_format)

    except ImportError:
        console.print(f"[bold red]Ошибка: Не удалось импортировать 'core.app_settings'.[/]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Произошла непредвиденная ошибка при отображении конфигурации: {e}[/]")
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)


def show_rich_config_info(settings, show_defaults: bool, compact: bool):
    """Показывает конфигурацию в красивом rich формате."""
    
    # Заголовок
    console.print(Panel.fit(
        "[bold cyan]🔧 Конфигурация SwiftDevBot[/bold cyan]",
        border_style="cyan",
        padding=(0, 1)
    ))
    
    if not compact:
        # Общая информация
        console.print("\n[bold]📊 Общая информация:[/bold]")
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Параметр", style="cyan")
        info_table.add_column("Значение", style="green")
        
        info_table.add_row("Версия SDB", settings.core.sdb_version)
        info_table.add_row("Путь к данным", str(settings.core.project_data_path))
        info_table.add_row("Уровень логирования", settings.core.log_level)
        info_table.add_row("Логирование в файл", "✅" if settings.core.log_to_file else "❌")
        
        console.print(info_table)
    
    # Telegram Bot
    console.print("\n[bold]🤖 Telegram Bot:[/bold]")
    bot_table = Table(show_header=False, box=None, padding=(0, 1))
    bot_table.add_column("Параметр", style="cyan")
    bot_table.add_column("Значение", style="green")
    
    token_display = f"****{settings.telegram.token[-4:]}" if settings.telegram.token else "❌ Не настроен"
    bot_table.add_row("Токен", token_display)
    bot_table.add_row("Polling Timeout", f"{settings.telegram.polling_timeout} сек")
    
    console.print(bot_table)
    
    # База данных
    console.print("\n[bold]🗄️ База данных:[/bold]")
    db_table = Table(show_header=False, box=None, padding=(0, 1))
    db_table.add_column("Параметр", style="cyan")
    db_table.add_column("Значение", style="green")
    
    db_table.add_row("Тип", settings.db.type.upper())
    if settings.db.type == "sqlite":
        db_table.add_row("Путь к файлу", str(settings.db.sqlite_path))
    elif settings.db.type == "postgresql" and settings.db.pg_dsn:
        db_table.add_row("PostgreSQL DSN", "****" + str(settings.db.pg_dsn)[-20:])
    elif settings.db.type == "mysql" and settings.db.mysql_dsn:
        db_table.add_row("MySQL DSN", "****" + str(settings.db.mysql_dsn)[-20:])
    
    db_table.add_row("SQL Echo", "✅" if settings.db.echo_sql else "❌")
    
    console.print(db_table)
    
    # Кэш
    console.print("\n[bold]💾 Кэш:[/bold]")
    cache_table = Table(show_header=False, box=None, padding=(0, 1))
    cache_table.add_column("Параметр", style="cyan")
    cache_table.add_column("Значение", style="green")
    
    cache_table.add_row("Тип", settings.cache.type.upper())
    if settings.cache.type == "redis" and settings.cache.redis_url:
        cache_table.add_row("Redis URL", "****" + str(settings.cache.redis_url)[-20:])
    else:
        cache_table.add_row("Redis URL", "❌ Не настроен")
    
    console.print(cache_table)
    
    # Администраторы
    console.print("\n[bold]👑 Администраторы:[/bold]")
    admin_table = Table(show_header=False, box=None, padding=(0, 1))
    admin_table.add_column("Параметр", style="cyan")
    admin_table.add_column("Значение", style="green")
    
    if settings.core.super_admins:
        admin_table.add_row("Супер-администраторы", ", ".join(map(str, settings.core.super_admins)))
    else:
        admin_table.add_row("Супер-администраторы", "❌ Не настроены")
    
    admin_table.add_row("Автосоздание админа", "✅" if getattr(settings, 'admin', {}).get('auto_create_super_admin', False) else "❌")
    
    console.print(admin_table)
    
    # Интернационализация
    console.print("\n[bold]🌍 Интернационализация:[/bold]")
    i18n_table = Table(show_header=False, box=None, padding=(0, 1))
    i18n_table.add_column("Параметр", style="cyan")
    i18n_table.add_column("Значение", style="green")
    
    i18n_table.add_row("Язык по умолчанию", settings.core.i18n.default_locale.upper())
    i18n_table.add_row("Доступные языки", ", ".join(settings.core.i18n.available_locales))
    i18n_table.add_row("Путь к переводам", str(settings.core.i18n.locales_dir))
    
    console.print(i18n_table)
    
    # Модули
    console.print("\n[bold]🧩 Модули:[/bold]")
    modules_table = Table(show_header=False, box=None, padding=(0, 1))
    modules_table.add_column("Параметр", style="cyan")
    modules_table.add_column("Значение", style="green")
    
    modules_table.add_row("Автозагрузка", "✅" if getattr(settings, 'modules', {}).get('auto_load', True) else "❌")
    modules_table.add_row("Репозиторий модулей", str(settings.module_repo.index_url))
    
    console.print(modules_table)
    
    # Веб-сервер
    console.print("\n[bold]🌐 Веб-сервер:[/bold]")
    web_table = Table(show_header=False, box=None, padding=(0, 1))
    web_table.add_column("Параметр", style="cyan")
    web_table.add_column("Значение", style="green")
    
    web_server_enabled = getattr(settings, 'features', {}).get('web_download_server', {}).get('enabled', False)
    web_table.add_row("Включен", "✅" if web_server_enabled else "❌")
    
    if web_server_enabled:
        web_config = getattr(settings, 'features', {}).get('web_download_server', {})
        web_table.add_row("Хост", web_config.get('host', '0.0.0.0'))
        web_table.add_row("Порт", str(web_config.get('port', 8080)))
    
    console.print(web_table)
    
    # Мониторинг
    console.print("\n[bold]📊 Мониторинг:[/bold]")
    monitoring_table = Table(show_header=False, box=None, padding=(0, 1))
    monitoring_table.add_column("Параметр", style="cyan")
    monitoring_table.add_column("Значение", style="green")
    
    monitoring_enabled = getattr(settings, 'monitoring', {}).get('enabled', False)
    monitoring_table.add_row("Включен", "✅" if monitoring_enabled else "❌")
    
    if monitoring_enabled:
        monitoring_config = getattr(settings, 'monitoring', {})
        monitoring_table.add_row("Порт метрик", str(monitoring_config.get('metrics_port', 9090)))
        monitoring_table.add_row("Health Check", "✅" if monitoring_config.get('health_check_enabled', True) else "❌")
    
    console.print(monitoring_table)
    
    # Статус конфигурации
    console.print("\n[bold]✅ Статус конфигурации:[/bold]")
    status_table = Table(show_header=False, box=None, padding=(0, 1))
    status_table.add_column("Проверка", style="cyan")
    status_table.add_column("Статус", style="green")
    
    # Проверяем основные компоненты
    status_table.add_row("Telegram Token", "✅ Настроен" if settings.telegram.token else "❌ Не настроен")
    status_table.add_row("База данных", "✅ Настроена" if settings.db.type else "❌ Не настроена")
    status_table.add_row("Администраторы", "✅ Настроены" if settings.core.super_admins else "❌ Не настроены")
    status_table.add_row("Путь к данным", "✅ Существует" if settings.core.project_data_path.exists() else "❌ Не существует")
    
    console.print(status_table)
    
    # Футер
    console.print(f"\n[dim]💡 Используйте --show-defaults для отображения значений по умолчанию[/dim]")
    console.print(f"[dim]💡 Используйте --compact для компактного вывода[/dim]")
    console.print(f"[dim]💡 Используйте --format yaml/json для сырого вывода[/dim]")


def show_raw_config_info(settings, show_defaults: bool, output_format: str):
    """Показывает конфигурацию в сыром формате (YAML/JSON)."""
    console.print(Panel("[bold cyan]Текущая активная конфигурация SwiftDevBot[/]", expand=False, border_style="cyan"))
    
    # Используем model_dump() из Pydantic V2 для получения словаря
    config_dict = settings.model_dump(mode='json', exclude_defaults=not show_defaults)

    if output_format == "yaml":
        try:
            yaml_output_str = yaml.dump(config_dict, indent=2, allow_unicode=True, sort_keys=False)
            syntax = Syntax(yaml_output_str, "yaml", theme="native", line_numbers=True, word_wrap=True)
            console.print(syntax)
        except ImportError:
            console.print("[yellow]PyYAML не установлен. Вывод будет в формате JSON.[/]")
            output_format = "json"
        except Exception as e_yaml:
            console.print(f"[red]Ошибка форматирования вывода в YAML: {e_yaml}. Попробуйте JSON.[/]")
            output_format = "json"
    
    if output_format == "json":
        json_output_str = json.dumps(config_dict, indent=2, ensure_ascii=False)
        syntax = Syntax(json_output_str, "json", theme="native", line_numbers=True, word_wrap=True)
        console.print(syntax)
        
    console.print(f"\n[dim]Конфигурация загружена с учетом дефолтов, '{USER_CONFIG_FILENAME}', и переменных окружения.[/dim]")
    if not show_defaults:
        console.print("[dim]Значения по умолчанию не показаны. Используйте --show-defaults для их отображения.[/dim]")