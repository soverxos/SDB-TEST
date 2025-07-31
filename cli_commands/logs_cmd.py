# cli_commands/logs_cmd.py

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import subprocess
import re

# Создаем приложение для команд логов
logs_app = typer.Typer(help="📋 Просмотр и управление логами SDB.")
console = Console()

try:
    from core.app_settings import load_app_settings
except ImportError:
    load_app_settings = None


def _get_log_directory() -> Path:
    """Получаем директорию логов"""
    try:
        if load_app_settings:
            settings = load_app_settings()
            logs_dir = Path(settings.core.project_data_path) / "Logs"
        else:
            logs_dir = Path.cwd() / "project_data" / "Logs"
        return logs_dir
    except Exception:
        return Path.cwd() / "project_data" / "Logs"


def _find_latest_log_file() -> Optional[Path]:
    """Находим последний файл лога"""
    logs_dir = _get_log_directory()
    
    if not logs_dir.exists():
        return None
    
    # Ищем файлы логов в структуре YYYY/MM-Month/DD/HH_sdb.log
    log_files = []
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith("_sdb.log"):
                log_files.append(Path(root) / file)
    
    if not log_files:
        return None
    
    # Сортируем по времени модификации
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return log_files[0]


def _format_log_line_ultra_compact(line: str) -> str:
    """Супер компактное форматирование - одна чистая строка без Rich markup"""
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s+\| ([^:]+):([^:]+):(\d+) - (.+)'
    
    match = re.match(pattern, line)
    if not match:
        return line
    
    timestamp, level, module, function, line_num, message = match.groups()
    
    # Только время
    time_short = timestamp.split()[1][:8]
    
    # Сокращаем компоненты
    if len(module) > 16:
        module = module[:13] + "..."
    if len(function) > 20:
        function = function[:17] + "..."
    if len(message) > 70:
        message = message[:67] + "..."
    
    # Чистый текст без markup - никаких переносов!
    return f"{time_short} {level:7} {module:16} {function:20} {line_num:>3} | {message}"


def _format_log_line_compact(line: str) -> str:
    """Форматирует строку лога в компактном виде (без переносов) - РЕАЛЬНО компактно"""
    # Паттерн для loguru: YYYY-MM-DD HH:MM:SS.sss | LEVEL | module:function:line - message
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s+\| ([^:]+):([^:]+):(\d+) - (.+)'
    
    match = re.match(pattern, line)
    if not match:
        return line
    
    timestamp, level, module, function, line_num, message = match.groups()
    
    # Цвета для уровней логирования (простые, без markup для компактности)
    level_colors = {
        'DEBUG': 'dim cyan',
        'INFO': 'blue', 
        'SUCCESS': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold red'
    }
    
    level_color = level_colors.get(level, 'white')
    
    # Сокращаем компоненты агрессивно для компактности
    time_short = timestamp.split()[1][:8]  # Только время HH:MM:SS
    
    if len(module) > 18:
        module = module[:15] + "..."
    if len(function) > 22:
        function = function[:19] + "..."
    if len(message) > 80:
        message = message[:77] + "..."
    
    # МАКСИМАЛЬНО компактное форматирование в одну строку
    formatted = f"{time_short} [{level_color}]{level:7}[/{level_color}] {module:18} {function:22} {line_num:>3} | {message}"
    
    return formatted


def _format_log_line(line: str) -> str:
    """Форматирует строку лога для красивого вывода"""
    # Паттерн для loguru: YYYY-MM-DD HH:MM:SS.sss | LEVEL | module:function:line - message
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s+\| ([^:]+):([^:]+):(\d+) - (.+)'
    
    match = re.match(pattern, line)
    if not match:
        return line
    
    timestamp, level, module, function, line_num, message = match.groups()
    
    # Цвета для уровней логирования
    level_colors = {
        'DEBUG': 'dim cyan',
        'INFO': 'blue', 
        'SUCCESS': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold red'
    }
    
    level_color = level_colors.get(level, 'white')
    
    # Обрезаем длинные имена модулей и функций для красоты
    if len(module) > 20:
        module = module[:17] + "..."
    if len(function) > 25:
        function = function[:22] + "..."
    
    # Обрезаем очень длинные сообщения и переносим на новую строку
    max_message_length = 100
    if len(message) > max_message_length:
        # Разбиваем длинное сообщение на части
        parts = []
        current_part = ""
        words = message.split()
        
        for word in words:
            if len(current_part + " " + word) <= max_message_length:
                current_part += (" " + word) if current_part else word
            else:
                if current_part:
                    parts.append(current_part)
                current_part = word
        
        if current_part:
            parts.append(current_part)
        
        # Форматируем первую строку
        formatted = (
            f"[dim]{timestamp}[/dim] "
            f"[{level_color}]{level:8}[/{level_color}] "
            f"[cyan]{module:20}[/cyan]:[bright_cyan]{function:25}[/bright_cyan]:[dim]{line_num:4}[/dim] "
            f"- {parts[0]}"
        )
        
        # Добавляем продолжения с отступом
        for part in parts[1:]:
            formatted += f"\n{' ' * 60}  {part}"
            
        return formatted
    else:
        # Обычное форматирование для коротких сообщений
        formatted = (
            f"[dim]{timestamp}[/dim] "
            f"[{level_color}]{level:8}[/{level_color}] "
            f"[cyan]{module:20}[/cyan]:[bright_cyan]{function:25}[/bright_cyan]:[dim]{line_num:4}[/dim] "
            f"- {message}"
        )
        
        return formatted


@logs_app.command("tail", help="📋 Показать последние строки из лога SDB.")
def tail_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Количество последних строк для показа"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Следить за логом в реальном времени"),
    filter_level: Optional[str] = typer.Option(None, "--level", "-l", help="Фильтр по уровню (DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)"),
    filter_module: Optional[str] = typer.Option(None, "--module", "-m", help="Фильтр по модулю"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Вывод в сыром формате без форматирования"),
    compact: bool = typer.Option(False, "--compact", "-c", help="Компактный вывод (без переносов длинных строк)"),
    ultra_compact: bool = typer.Option(False, "--ultra-compact", "-u", help="Супер компактный вывод (чистые строки без цветов)"),
    frame: bool = typer.Option(False, "--frame", help="Вывод в рамке"),
    sort_by_time: bool = typer.Option(True, "--sort-time", help="Сортировать по времени")
):
    """Показывает последние строки из лога SDB с красивым форматированием"""
    
    log_file = _find_latest_log_file()
    if not log_file or not log_file.exists():
        console.print("[red]❌ Файл лога не найден![/red]")
        console.print(f"[dim]Ожидаемая директория логов: {_get_log_directory()}[/dim]")
        raise typer.Exit(1)
    
    if frame:
        console.print(Panel(f"📋 Читаем лог: {log_file}", style="cyan"))
    else:
        console.print(f"[dim]📋 Читаем лог: {log_file}[/dim]\n")
    
    try:
        if follow:
            # Режим следования за логом (tail -f)
            if frame:
                console.print(Panel("👁️ Режим мониторинга логов (Ctrl+C для выхода)", style="yellow"))
            else:
                console.print("[yellow]👁️ Режим мониторинга логов (Ctrl+C для выхода)[/yellow]\n")
            
            process = subprocess.Popen(
                ["tail", "-f", str(log_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            try:
                for line in iter(process.stdout.readline, ''):
                    line = line.rstrip()
                    if not line:
                        continue
                        
                    # Применяем фильтры
                    if filter_level and filter_level.upper() not in line:
                        continue
                    if filter_module and filter_module not in line:
                        continue
                    
                    if raw:
                        console.print(line)
                    elif ultra_compact:
                        # Супер компактный режим - печатаем как обычный текст без Rich
                        print(_format_log_line_ultra_compact(line))
                    else:
                        formatted_line = _format_log_line(line) if not compact else _format_log_line_compact(line)
                        if frame:
                            console.print(Panel(formatted_line, expand=False))
                        else:
                            console.print(formatted_line, markup=False)
                        
            except KeyboardInterrupt:
                if frame:
                    console.print(Panel("👋 Мониторинг логов остановлен", style="yellow"))
                else:
                    console.print("\n[yellow]👋 Мониторинг логов остановлен[/yellow]")
                process.terminate()
                
        else:
            # Обычный режим tail
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                filtered_lines = []
                for line in last_lines:
                    line = line.rstrip()
                    if not line:
                        continue
                    
                    # Применяем фильтры
                    if filter_level and filter_level.upper() not in line:
                        continue
                    if filter_module and filter_module not in line:
                        continue
                    
                    filtered_lines.append(line)
                
                # Сортируем по времени если нужно
                if sort_by_time and not raw:
                    filtered_lines.sort(key=lambda x: x[:23] if len(x) >= 23 else x)
                
                # Выводим строки
                if frame and filtered_lines:
                    # Группируем строки для красивого вывода в рамках
                    output_text = ""
                    for line in filtered_lines:
                        if raw:
                            output_text += line + "\n"
                        elif ultra_compact:
                            output_text += _format_log_line_ultra_compact(line) + "\n"
                        else:
                            formatted_line = _format_log_line(line) if not compact else _format_log_line_compact(line)
                            output_text += formatted_line + "\n"
                    
                    console.print(Panel(output_text.rstrip(), title="📋 Логи SDB", border_style="blue"))
                else:
                    for line in filtered_lines:
                        if raw:
                            console.print(line)
                        elif ultra_compact:
                            # Супер компактный режим - печатаем как обычный текст без Rich
                            print(_format_log_line_ultra_compact(line))
                        else:
                            formatted_line = _format_log_line(line) if not compact else _format_log_line_compact(line)
                            console.print(formatted_line, markup=False)
                
                if not filtered_lines:
                    if frame:
                        console.print(Panel("⚠️ Нет строк, соответствующих фильтрам", style="yellow"))
                    else:
                        console.print("[yellow]⚠️ Нет строк, соответствующих фильтрам[/yellow]")
                    
    except Exception as e:
        console.print(f"[red]❌ Ошибка при чтении лога: {e}[/red]")
        raise typer.Exit(1)


@logs_app.command("clean", help="🧹 Показать логи в супер-чистом формате (алиас для --ultra-compact).")
def clean_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Количество последних строк для показа"),
    filter_level: Optional[str] = typer.Option(None, "--level", "-l", help="Фильтр по уровню"),
    filter_module: Optional[str] = typer.Option(None, "--module", "-m", help="Фильтр по модулю")
):
    """Показывает логи в супер-чистом формате без каши и переносов"""
    
    log_file = _find_latest_log_file()
    if not log_file or not log_file.exists():
        print("❌ Файл лога не найден!")
        raise typer.Exit(1)
    
    print(f"📋 Логи SDB (чистый формат): {log_file}")
    print()
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            filtered_lines = []
            for line in last_lines:
                line = line.rstrip()
                if not line:
                    continue
                
                # Применяем фильтры
                if filter_level and filter_level.upper() not in line:
                    continue
                if filter_module and filter_module not in line:
                    continue
                
                filtered_lines.append(line)
            
            # Выводим строки в супер чистом формате
            for line in filtered_lines:
                print(_format_log_line_ultra_compact(line))
            
            if not filtered_lines:
                print("⚠️ Нет строк, соответствующих фильтрам")
                
    except Exception as e:
        print(f"❌ Ошибка при чтении лога: {e}")
        raise typer.Exit(1)


@logs_app.command("table", help="📊 Показать логи в виде таблицы.")
def table_logs(
    lines: int = typer.Option(30, "--lines", "-n", help="Количество последних строк для показа"),
    filter_level: Optional[str] = typer.Option(None, "--level", "-l", help="Фильтр по уровню"),
    filter_module: Optional[str] = typer.Option(None, "--module", "-m", help="Фильтр по модулю"),
    sort_by_time: bool = typer.Option(True, "--sort-time", help="Сортировать по времени")
):
    """Показывает логи в виде красивой таблицы"""
    
    log_file = _find_latest_log_file()
    if not log_file or not log_file.exists():
        console.print("[red]❌ Файл лога не найден![/red]")
        raise typer.Exit(1)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Парсим строки логов
            log_entries = []
            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s+\| ([^:]+):([^:]+):(\d+) - (.+)'
            
            for line in last_lines:
                line = line.rstrip()
                if not line:
                    continue
                
                match = re.match(pattern, line)
                if not match:
                    continue
                
                timestamp, level, module, function, line_num, message = match.groups()
                
                # Применяем фильтры
                if filter_level and filter_level.upper() != level:
                    continue
                if filter_module and filter_module not in module:
                    continue
                
                # Обрезаем длинные строки для таблицы
                if len(module) > 20:
                    module = module[:17] + "..."
                if len(function) > 25:
                    function = function[:22] + "..."
                if len(message) > 60:
                    message = message[:57] + "..."
                
                log_entries.append({
                    'time': timestamp.split()[1][:8],  # Только время
                    'level': level,
                    'module': module,
                    'function': function,
                    'line': line_num,
                    'message': message
                })
            
            if not log_entries:
                console.print("[yellow]⚠️ Нет строк, соответствующих фильтрам[/yellow]")
                return
            
            # Сортируем по времени если нужно
            if sort_by_time:
                log_entries.sort(key=lambda x: x['time'])
            
            # Создаем таблицу
            table = Table(title="📊 Логи SDB (табличный вид)")
            table.add_column("Время", style="dim", width=10)
            table.add_column("Уровень", width=10)
            table.add_column("Модуль", style="cyan", width=20)
            table.add_column("Функция", style="bright_cyan", width=25)
            table.add_column("Строка", justify="right", style="dim", width=6)
            table.add_column("Сообщение", width=60)
            
            # Цвета для уровней
            level_colors = {
                'DEBUG': 'dim cyan',
                'INFO': 'blue', 
                'SUCCESS': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold red'
            }
            
            # Добавляем строки в таблицу
            for entry in log_entries:
                level_color = level_colors.get(entry['level'], 'white')
                table.add_row(
                    entry['time'],
                    f"[{level_color}]{entry['level']}[/{level_color}]",
                    entry['module'],
                    entry['function'],
                    entry['line'],
                    entry['message']
                )
            
            console.print(table)
            console.print(f"\n[dim]📊 Показано записей: {len(log_entries)} из {len(last_lines)}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Ошибка при чтении лога: {e}[/red]")
        raise typer.Exit(1)


@logs_app.command("list", help="📂 Показать список доступных файлов логов.")
def list_logs():
    """Показывает список всех доступных файлов логов"""
    
    logs_dir = _get_log_directory()
    
    if not logs_dir.exists():
        console.print(f"[red]❌ Директория логов не найдена: {logs_dir}[/red]")
        raise typer.Exit(1)
    
    # Собираем все файлы логов
    log_files = []
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith("_sdb.log"):
                full_path = Path(root) / file
                stat = full_path.stat()
                log_files.append({
                    'path': full_path,
                    'relative_path': full_path.relative_to(logs_dir),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
    
    if not log_files:
        console.print("[yellow]⚠️ Файлы логов не найдены[/yellow]")
        return
    
    # Сортируем по времени модификации (новые сверху)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    
    # Создаем таблицу
    table = Table(title="📋 Файлы логов SDB")
    table.add_column("Файл", style="cyan")
    table.add_column("Размер", justify="right", style="green")
    table.add_column("Последнее изменение", style="yellow")
    
    for log_info in log_files:
        # Форматируем размер файла
        size = log_info['size']
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        # Форматируем время
        time_str = log_info['modified'].strftime("%Y-%m-%d %H:%M:%S")
        
        table.add_row(
            str(log_info['relative_path']),
            size_str,
            time_str
        )
    
    console.print(table)
    console.print(f"\n[dim]📂 Директория логов: {logs_dir}[/dim]")


@logs_app.command("search", help="🔍 Поиск в логах по ключевым словам.")
def search_logs(
    query: str = typer.Argument(..., help="Поисковый запрос"),
    lines: int = typer.Option(100, "--lines", "-n", help="Максимальное количество строк для поиска с конца"),
    context: int = typer.Option(2, "--context", "-C", help="Количество строк контекста до и после найденной строки"),
    ignore_case: bool = typer.Option(True, "--ignore-case", "-i", help="Игнорировать регистр при поиске"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Вывод в сыром формате без форматирования")
):
    """Поиск по логам с выводом контекста"""
    
    log_file = _find_latest_log_file()
    if not log_file or not log_file.exists():
        console.print("[red]❌ Файл лога не найден![/red]")
        raise typer.Exit(1)
    
    console.print(f"[dim]🔍 Поиск в логе: {log_file}[/dim]")
    console.print(f"[dim]Запрос: [cyan]'{query}'[/cyan][/dim]\n")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            search_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Поиск
        matches = []
        search_query = query.lower() if ignore_case else query
        
        for i, line in enumerate(search_lines):
            search_line = line.lower() if ignore_case else line
            if search_query in search_line:
                matches.append(i)
        
        if not matches:
            console.print("[yellow]⚠️ Ничего не найдено[/yellow]")
            return
        
        console.print(f"[green]✅ Найдено совпадений: {len(matches)}[/green]\n")
        
        # Выводим результаты с контекстом
        for match_idx in matches:
            start_idx = max(0, match_idx - context)
            end_idx = min(len(search_lines), match_idx + context + 1)
            
            console.print(f"[bold blue]--- Совпадение в строке {match_idx + 1} ---[/bold blue]")
            
            for i in range(start_idx, end_idx):
                line = search_lines[i].rstrip()
                if i == match_idx:
                    # Выделяем найденную строку
                    if raw:
                        console.print(f"[bold green]> {line}[/bold green]")
                    else:
                        formatted = _format_log_line(line)
                        console.print(f"[bold green]> [/bold green]{formatted}", markup=False)
                else:
                    # Контекстные строки
                    if raw:
                        console.print(f"  {line}")
                    else:
                        console.print(f"  {_format_log_line(line)}", markup=False)
            
            console.print()
            
    except Exception as e:
        console.print(f"[red]❌ Ошибка при поиске в логе: {e}[/red]")
        raise typer.Exit(1)


@logs_app.command("clear", help="🧹 Очистка старых файлов логов.")
def clear_logs(
    days: int = typer.Option(30, "--days", "-d", help="Удалить логи старше указанного количества дней"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать, что будет удалено, но не удалять"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Не спрашивать подтверждение")
):
    """Очистка старых файлов логов"""
    
    logs_dir = _get_log_directory()
    
    if not logs_dir.exists():
        console.print(f"[red]❌ Директория логов не найдена: {logs_dir}[/red]")
        raise typer.Exit(1)
    
    # Находим старые файлы
    now = datetime.now()
    old_files = []
    
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith("_sdb.log"):
                full_path = Path(root) / file
                modified_time = datetime.fromtimestamp(full_path.stat().st_mtime)
                age_days = (now - modified_time).days
                
                if age_days > days:
                    old_files.append((full_path, age_days))
    
    if not old_files:
        console.print(f"[green]✅ Нет файлов логов старше {days} дней[/green]")
        return
    
    # Показываем что будет удалено
    table = Table(title=f"🧹 Файлы логов старше {days} дней")
    table.add_column("Файл", style="cyan")
    table.add_column("Возраст (дней)", justify="right", style="yellow")
    table.add_column("Размер", justify="right", style="green")
    
    total_size = 0
    for file_path, age in old_files:
        size = file_path.stat().st_size
        total_size += size
        
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        relative_path = file_path.relative_to(logs_dir)
        table.add_row(str(relative_path), str(age), size_str)
    
    console.print(table)
    
    if total_size < 1024:
        total_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        total_str = f"{total_size / 1024:.1f} KB"
    else:
        total_str = f"{total_size / (1024 * 1024):.1f} MB"
    
    console.print(f"\n[bold]Всего файлов: {len(old_files)}, общий размер: {total_str}[/bold]")
    
    if dry_run:
        console.print("\n[yellow]🔍 Пробный прогон - файлы НЕ будут удалены[/yellow]")
        return
    
    # Подтверждение
    if not confirm:
        if not typer.confirm(f"\nВы уверены, что хотите удалить {len(old_files)} файлов логов?"):
            console.print("[yellow]❌ Операция отменена[/yellow]")
            return
    
    # Удаляем файлы
    deleted_count = 0
    for file_path, _ in old_files:
        try:
            file_path.unlink()
            deleted_count += 1
        except Exception as e:
            console.print(f"[red]❌ Ошибка при удалении {file_path}: {e}[/red]")
    
    console.print(f"\n[green]✅ Удалено файлов: {deleted_count} из {len(old_files)}[/green]")


# Экспорт приложения
__all__ = ["logs_app"]
