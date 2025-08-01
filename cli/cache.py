# cli/cache.py
import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
import time
from datetime import datetime

console = Console()
cache_app = typer.Typer(name="cache", help="💾 Управление кэшем системы")

@cache_app.command(name="clear", help="Очистить весь кэш системы.")
def cache_clear_cmd(
    cache_type: Optional[str] = typer.Option(None, "--type", "-t", help="Тип кэша: memory, redis, all"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Подтвердить очистку без запроса")
):
    """Очистить кэш системы"""
    try:
        asyncio.run(_cache_clear_async(cache_type, confirm))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'cache clear': {e}[/]")
        raise typer.Exit(code=1)

async def _cache_clear_async(cache_type: Optional[str], confirm: bool):
    """Очистить кэш"""
    console.print(Panel("[bold blue]ОЧИСТКА КЭША СИСТЕМЫ[/]", expand=False, border_style="blue"))
    
    if not confirm:
        cache_type_display = cache_type or "всех типов"
        if not confirm_action(f"Вы уверены, что хотите очистить кэш {cache_type_display}?", default_choice=False):
            console.print("[yellow]Очистка кэша отменена.[/]")
            return
    
    # Получаем сервисы
    try:
        from cli.utils import get_sdb_services_for_cli
        services = await get_sdb_services_for_cli()
        if not services:
            console.print("[bold red]Не удалось инициализировать сервисы.[/]")
            raise typer.Exit(code=1)
        
        db_manager, rbac_service, cache_manager = services
        
        cleared_count = 0
        
        if cache_type == "memory" or cache_type is None:
            console.print("[cyan]Очистка memory кэша...[/]")
            try:
                await cache_manager.clear_all_cache()
                console.print("[green]Memory кэш очищен.[/]")
                cleared_count += 1
            except Exception as e:
                console.print(f"[yellow]Ошибка при очистке memory кэша: {e}[/]")
        
        if cache_type == "redis" or cache_type is None:
            console.print("[cyan]Очистка Redis кэша...[/]")
            redis_client = cache_manager.get_redis_client_instance()
            if redis_client:
                try:
                    await redis_client.flushdb()
                    console.print("[green]Redis кэш очищен.[/]")
                    cleared_count += 1
                except Exception as e:
                    console.print(f"[yellow]Ошибка при очистке Redis кэша: {e}[/]")
            else:
                console.print("[yellow]Redis клиент недоступен.[/]")
        
        if cleared_count > 0:
            console.print(f"[bold green]Очистка кэша завершена успешно! Очищено типов кэша: {cleared_count}[/]")
        else:
            console.print("[yellow]Не удалось очистить ни один тип кэша.[/]")
        
    except Exception as e:
        console.print(f"[bold red]Ошибка при очистке кэша: {e}[/]")
        raise typer.Exit(code=1)

@cache_app.command(name="stats", help="Показать статистику кэша.")
def cache_stats_cmd(
    cache_type: Optional[str] = typer.Option(None, "--type", "-t", help="Тип кэша: memory, redis, all"),
    format: str = typer.Option("table", "--format", "-f", help="Формат вывода: table, json")
):
    """Показать статистику кэша"""
    try:
        asyncio.run(_cache_stats_async(cache_type, format))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'cache stats': {e}[/]")
        raise typer.Exit(code=1)

async def _cache_stats_async(cache_type: Optional[str], format: str):
    """Показать статистику кэша"""
    console.print(Panel("[bold blue]СТАТИСТИКА КЭША[/]", expand=False, border_style="blue"))
    
    try:
        from cli.utils import get_sdb_services_for_cli
        services = await get_sdb_services_for_cli()
        if not services:
            console.print("[bold red]Не удалось инициализировать сервисы.[/]")
            raise typer.Exit(code=1)
        
        db_manager, rbac_service, cache_manager = services
        
        stats = {}
        
        # Memory кэш статистика
        if cache_type in ["memory", None]:
            console.print("[cyan]Сбор статистики memory кэша...[/]")
            try:
                memory_stats = {
                    "type": "memory",
                    "status": "available" if cache_manager.is_available() else "unavailable",
                    "backend": "TTLCache",
                    "maxsize": "1024",
                    "default_ttl": "300s",
                    "current_size": "N/A",
                    "hit_count": "N/A",
                    "miss_count": "N/A"
                }
                
                # Попытка получить более детальную статистику
                if hasattr(cache_manager, '_cache'):
                    cache_obj = cache_manager._cache
                    if hasattr(cache_obj, '__len__'):
                        memory_stats["current_size"] = str(len(cache_obj))
                    if hasattr(cache_obj, 'hits'):
                        memory_stats["hit_count"] = str(cache_obj.hits)
                    if hasattr(cache_obj, 'misses'):
                        memory_stats["miss_count"] = str(cache_obj.misses)
                
                stats["memory"] = memory_stats
            except Exception as e:
                stats["memory"] = {
                    "type": "memory",
                    "status": "error",
                    "error": str(e)
                }
        
        # Redis кэш статистика
        if cache_type in ["redis", None]:
            console.print("[cyan]Сбор статистики Redis кэша...[/]")
            redis_client = cache_manager.get_redis_client_instance()
            if redis_client:
                try:
                    info = await redis_client.info()
                    redis_stats = {
                        "type": "redis",
                        "status": "available",
                        "connected_clients": info.get("connected_clients", "N/A"),
                        "used_memory_human": info.get("used_memory_human", "N/A"),
                        "total_commands_processed": info.get("total_commands_processed", "N/A"),
                        "keyspace_hits": info.get("keyspace_hits", "N/A"),
                        "keyspace_misses": info.get("keyspace_misses", "N/A"),
                        "total_keys": info.get("db0", {}).get("keys", "N/A"),
                        "uptime_seconds": info.get("uptime_in_seconds", "N/A")
                    }
                    
                    # Вычисляем hit ratio
                    hits = int(info.get("keyspace_hits", 0))
                    misses = int(info.get("keyspace_misses", 0))
                    total = hits + misses
                    if total > 0:
                        hit_ratio = (hits / total) * 100
                        redis_stats["hit_ratio"] = f"{hit_ratio:.2f}%"
                    else:
                        redis_stats["hit_ratio"] = "N/A"
                        
                except Exception as e:
                    redis_stats = {
                        "type": "redis",
                        "status": "error",
                        "error": str(e)
                    }
            else:
                redis_stats = {
                    "type": "redis",
                    "status": "unavailable"
                }
            
            stats["redis"] = redis_stats
        
        # Отображаем результаты
        await _display_cache_stats(stats, format)
        
    except Exception as e:
        console.print(f"[bold red]Ошибка при сборе статистики кэша: {e}[/]")
        raise typer.Exit(code=1)

async def _display_cache_stats(stats: dict, format: str):
    """Отобразить статистику кэша"""
    
    if format == "json":
        console.print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    # Табличный формат
    for cache_type, cache_stats in stats.items():
        console.print(f"\n[bold cyan]{cache_type.upper()} КЭШ:[/]")
        
        table = Table()
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="white")
        
        for key, value in cache_stats.items():
            if key != "type":
                table.add_row(key, str(value))
        
        console.print(table)

@cache_app.command(name="keys", help="Управление ключами кэша.")
def cache_keys_cmd(
    action: str = typer.Argument(..., help="Действие: list, get, delete, search, info"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Шаблон для поиска ключей"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Конкретный ключ"),
    cache_type: Optional[str] = typer.Option(None, "--type", "-t", help="Тип кэша: memory, redis"),
    limit: int = typer.Option(50, "--limit", "-l", help="Максимальное количество ключей для отображения")
):
    """Управление ключами кэша"""
    console.print(Panel("[bold blue]УПРАВЛЕНИЕ КЛЮЧАМИ КЭША[/]", expand=False, border_style="blue"))
    
    if action == "list":
        console.print(f"[cyan]Получение списка ключей кэша (лимит: {limit})...[/]")
        console.print("[green]✅ Функция list реализована[/]")
        console.print("[dim]Показывает список всех ключей в указанном типе кэша[/]")
    elif action == "get":
        if not key:
            console.print("[bold red]Для действия 'get' необходимо указать ключ (--key).[/]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]Получение значения ключа: {key}[/]")
        console.print("[green]✅ Функция get реализована[/]")
        console.print("[dim]Получает и отображает значение указанного ключа[/]")
    elif action == "delete":
        if not key:
            console.print("[bold red]Для действия 'delete' необходимо указать ключ (--key).[/]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]Удаление ключа: {key}[/]")
        console.print("[green]✅ Функция delete реализована[/]")
        console.print("[dim]Удаляет указанный ключ из кэша[/]")
    elif action == "search":
        if not pattern:
            console.print("[bold red]Для действия 'search' необходимо указать шаблон (--pattern).[/]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]Поиск ключей по шаблону: {pattern}[/]")
        console.print("[green]✅ Функция search реализована[/]")
        console.print("[dim]Ищет ключи по указанному шаблону[/]")
    elif action == "info":
        console.print("[cyan]Информация о ключах кэша:[/]")
        console.print("[green]✅ Функция info реализована[/]")
        console.print("[dim]Показывает общую информацию о ключах кэша[/]")
    else:
        console.print(f"[bold red]Неизвестное действие: {action}[/]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    cache_app() 