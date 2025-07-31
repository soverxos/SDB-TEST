# cli_commands/license_cmd.py
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dataclasses import asdict
import asyncio

from core.license_manager import get_license_manager, LicenseType

console = Console()

license_app = typer.Typer(
    name="license",
    help="🔑 Управление лицензией SwiftDevBot.",
    rich_markup_mode="rich"
)

async def update_stats_async():
    """Асинхронно собирает и обновляет статистику использования."""
    from core.services_provider import BotServicesProvider
    from core.app_settings import settings
    from sqlalchemy import select, func

    stats = {}
    try:
        # Инициализируем сервисы для доступа к БД и модулям
        services = BotServicesProvider(settings)
        await services.setup_services()

        # Пользователи
        if services.db:
            async with services.db.get_session() as session:
                from core.database.core_models import User
                user_count = await session.scalar(select(func.count(User.id)))
                stats['max_users'] = user_count or 0
        
        # Модули
        if services.modules:
            stats['max_modules'] = len(services.modules.enabled_plugin_names)

        await services.close_services()
    except Exception as e:
        console.print(f"[bold red]Ошибка при обновлении статистики: {e}[/bold red]")

    return stats


@license_app.command(name="info", help="Показать информацию о текущей лицензии и лимитах.")
def show_license_info():
    """Показывает детальную информацию о текущей лицензии и использовании."""
    console.print("[cyan]Обновление статистики использования...[/cyan]")
    
    # Обновляем статистику перед показом
    try:
        updated_stats = asyncio.run(update_stats_async())
        manager = get_license_manager()
        manager.update_usage_stats(**updated_stats)
    except Exception as e:
        console.print(f"[bold red]Не удалось полностью обновить статистику: {e}[/bold red]")
        manager = get_license_manager() # Все равно получаем менеджер

    info = manager.license_info
    
    title_style = {
        LicenseType.LITE: "[bold cyan]🆓 SwiftDevBot LITE[/bold cyan]",
        LicenseType.PRO: "[bold yellow]🚀 SwiftDevBot PRO[/bold yellow]",
        LicenseType.PRO_PLUS: "[bold magenta]💎 SwiftDevBot PRO+[/bold magenta]",
    }
    
    console.print(Panel.fit(title_style.get(info.type, "Статус лицензии"), border_style="blue", title_align="left"))
    
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column("Параметр", style="cyan", width=18)
    info_table.add_column("Значение")
    
    info_table.add_row("Тип лицензии", info.type.value.upper())
    if info.key:
        info_table.add_row("Ключ", f"****-****-{info.key[-4:]}")
    if info.activated_at:
        info_table.add_row("Активирована", info.activated_at.strftime('%Y-%m-%d %H:%M:%S'))
    
    console.print(info_table)

    console.print("\n[bold]⚖️ Лимиты и Использование:[/bold]")
    limits_table = Table(box=None, padding=(0, 1))
    limits_table.add_column("Ограничение", style="cyan")
    limits_table.add_column("Текущее", style="yellow", justify="right")
    limits_table.add_column("Лимит", style="green", justify="right")
    limits_table.add_column("Статус", justify="center")

    limits_dict = asdict(info.limits)
    for limit_name, limit_value in limits_dict.items():
        if limit_name.startswith("max_"):
            current_value = manager.get_current_usage(limit_name)
            is_ok, limit = manager.check_limit(limit_name, current_value)
            status = "✅" if is_ok else "⚠️"
            limit_str = "Безлимитно" if limit == -1 else str(limit)
            limits_table.add_row(limit_name.replace("max_", "").replace("_", " ").capitalize(), str(current_value), limit_str, status)

    console.print(limits_table)
    
    console.print("\n[bold]🔧 Функциональность:[/bold]")
    features_table = Table(box=None, padding=(0, 1))
    features_table.add_column("Функция", style="cyan")
    features_table.add_column("Доступность")
    
    for feature_name, _ in limits_dict.items():
        if feature_name.startswith("allow_"):
            is_available = manager.is_feature_available(feature_name)
            status = "[green]✅ Доступно[/green]" if is_available else "[red]❌ Недоступно[/red]"
            features_table.add_row(feature_name.replace("allow_", "").replace("_", " ").capitalize(), status)
            
    console.print(features_table)

@license_app.command(name="activate", help="Активировать лицензию PRO или PRO+.")
def activate_license_key(
    key: str = typer.Argument(..., help="Лицензионный ключ для активации.")
):
    """Активирует лицензию и обновляет статус бота."""
    console.print(Panel(f"Попытка активации ключа: [yellow]****-{key[-4:]}[/yellow]", title="Активация лицензии"))
    manager = get_license_manager()
    
    if manager.activate_license(key):
        console.print("\n[bold green]✅ Лицензия успешно активирована![/bold green]")
        console.print("Перезапустите бота, чтобы все изменения вступили в силу: [cyan]./sdb restart[/cyan]")
        show_license_info()
    else:
        console.print("\n[bold red]❌ Ошибка: предоставленный ключ недействителен.[/bold red]")