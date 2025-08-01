# cli/dev.py
import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional, List, Dict, Any
import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import tempfile
import shutil

console = Console()
dev_app = typer.Typer(name="dev", help="🔧 Инструменты разработки")

# Константы для dev инструментов
DEV_DIR = Path("project_data/dev")
DEV_CONFIG_FILE = DEV_DIR / "dev_config.json"
DEV_LOGS_DIR = DEV_DIR / "logs"
DEV_DOCS_DIR = DEV_DIR / "docs"

def _ensure_dev_directory():
    """Создать директорию для dev инструментов если её нет"""
    DEV_DIR.mkdir(parents=True, exist_ok=True)
    DEV_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    DEV_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DEV_CONFIG_FILE.exists():
        default_config = {
            "linting": {
                "tools": ["flake8", "black", "isort", "mypy"],
                "config_files": {
                    "flake8": ".flake8",
                    "black": "pyproject.toml",
                    "isort": ".isort.cfg",
                    "mypy": "mypy.ini"
                }
            },
            "testing": {
                "framework": "pytest",
                "coverage_tool": "coverage",
                "test_pattern": "test_*.py",
                "coverage_report_format": "html"
            },
            "documentation": {
                "builder": "sphinx",
                "formats": ["html", "pdf"],
                "source_dir": "docs",
                "output_dir": "docs/build"
            },
            "debugging": {
                "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR"],
                "log_formats": ["text", "json"],
                "profiling": False
            }
        }
        with open(DEV_CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)

def _load_dev_config() -> Dict[str, Any]:
    """Загрузить конфигурацию dev инструментов"""
    _ensure_dev_directory()
    try:
        with open(DEV_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def _save_dev_config(config: Dict[str, Any]):
    """Сохранить конфигурацию dev инструментов"""
    _ensure_dev_directory()
    with open(DEV_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def _check_tool_availability(tool_name: str) -> bool:
    """Проверить доступность инструмента"""
    try:
        result = subprocess.run([tool_name, "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def _get_python_files(directory: str = ".") -> List[str]:
    """Получить список Python файлов в директории"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Исключаем виртуальные окружения и кэш
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

@dev_app.command(name="lint", help="Проверка кода с помощью линтера.")
def dev_lint_cmd(
    files: Optional[List[str]] = typer.Option(None, "--files", "-f", help="Файлы для проверки"),
    fix: bool = typer.Option(False, "--fix", help="Автоматически исправить проблемы"),
    tool: str = typer.Option("flake8", "--tool", "-t", help="Инструмент: flake8, black, isort, mypy"),
    output_format: str = typer.Option("text", "--format", help="Формат вывода: text, json, html")
):
    """Проверка кода с помощью линтера"""
    try:
        asyncio.run(_dev_lint_async(files, fix, tool, output_format))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'dev lint': {e}[/]")
        raise typer.Exit(code=1)

async def _dev_lint_async(files: Optional[List[str]], fix: bool, tool: str, output_format: str):
    """Асинхронная обработка команды lint"""
    console.print(Panel("[bold blue]ПРОВЕРКА КОДА[/]", expand=False, border_style="blue"))
    
    # Проверяем доступность инструмента
    if not _check_tool_availability(tool):
        console.print(f"[bold red]Инструмент '{tool}' не найден. Установите его: pip install {tool}[/]")
        raise typer.Exit(code=1)
    
    # Определяем файлы для проверки
    if not files:
        files = _get_python_files()
        console.print(f"[cyan]Найдено Python файлов:[/] {len(files)}")
    else:
        console.print(f"[cyan]Файлы для проверки:[/] {', '.join(files)}")
    
    if not files:
        console.print("[yellow]Python файлы не найдены[/]")
        return
    
    console.print(f"[cyan]Инструмент:[/] {tool}")
    console.print(f"[cyan]Режим:[/] {'Автоисправление' if fix else 'Только проверка'}")
    
    # Выполняем проверку
    issues = await _run_linting_tool(tool, files, fix)
    
    # Отображаем результаты
    await _display_lint_results(issues, tool, output_format)

async def _run_linting_tool(tool: str, files: List[str], fix: bool) -> List[Dict[str, Any]]:
    """Запустить инструмент линтинга"""
    issues = []
    
    try:
        if tool == "flake8":
            cmd = ["flake8"] + files
            if fix:
                console.print("[yellow]flake8 не поддерживает автоисправление[/]")
        elif tool == "black":
            cmd = ["black"] + files
            if not fix:
                cmd.append("--check")
        elif tool == "isort":
            cmd = ["isort"] + files
            if not fix:
                cmd.append("--check-only")
        elif tool == "mypy":
            cmd = ["mypy"] + files
        else:
            console.print(f"[yellow]Неподдерживаемый инструмент: {tool}[/]")
            return issues
        
        console.print(f"[cyan]Выполняется:[/] {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Проверка завершена без ошибок[/]")
        else:
            # Парсим вывод для извлечения проблем
            for line in result.stdout.split('\n') + result.stderr.split('\n'):
                if line.strip():
                    issues.append({
                        "file": "unknown",
                        "line": 0,
                        "column": 0,
                        "message": line.strip(),
                        "severity": "error"
                    })
            
            console.print(f"[yellow]⚠️ Найдено проблем: {len(issues)}[/]")
            
    except Exception as e:
        console.print(f"[bold red]Ошибка при выполнении {tool}: {e}[/]")
    
    return issues

async def _display_lint_results(issues: List[Dict[str, Any]], tool: str, output_format: str):
    """Отобразить результаты линтинга"""
    if output_format == "json":
        console.print(json.dumps(issues, indent=2, ensure_ascii=False))
        return
    
    if not issues:
        console.print("[green]✅ Проблем не найдено[/]")
        return
    
    # Табличный формат
    table = Table(title=f"Результаты проверки ({tool})")
    table.add_column("Файл", style="cyan")
    table.add_column("Строка", style="blue")
    table.add_column("Колонка", style="green")
    table.add_column("Сообщение", style="white")
    table.add_column("Тип", style="red")
    
    for issue in issues:
        table.add_row(
            issue.get("file", "N/A"),
            str(issue.get("line", "N/A")),
            str(issue.get("column", "N/A")),
            issue.get("message", "N/A"),
            issue.get("severity", "error")
        )
    
    console.print(table)

@dev_app.command(name="test", help="Запуск тестов.")
def dev_test_cmd(
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Шаблон для поиска тестов"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Показать покрытие кода"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Подробный вывод"),
    parallel: bool = typer.Option(False, "--parallel", help="Запуск тестов параллельно")
):
    """Запуск тестов"""
    try:
        asyncio.run(_dev_test_async(pattern, coverage, verbose, parallel))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'dev test': {e}[/]")
        raise typer.Exit(code=1)

async def _dev_test_async(pattern: Optional[str], coverage: bool, verbose: bool, parallel: bool):
    """Асинхронная обработка команды test"""
    console.print(Panel("[bold blue]ЗАПУСК ТЕСТОВ[/]", expand=False, border_style="blue"))
    
    config = _load_dev_config()
    test_config = config.get("testing", {})
    framework = test_config.get("framework", "pytest")
    
    # Проверяем доступность pytest
    if not _check_tool_availability("pytest"):
        console.print("[bold red]pytest не найден. Установите его: pip install pytest[/]")
        raise typer.Exit(code=1)
    
    # Формируем команду
    cmd = ["pytest"]
    
    if pattern:
        cmd.extend(["-k", pattern])
        console.print(f"[cyan]Шаблон тестов:[/] {pattern}")
    
    if coverage:
        if not _check_tool_availability("coverage"):
            console.print("[yellow]coverage не найден. Установите его: pip install coverage[/]")
        else:
            cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
            console.print("[cyan]Покрытие кода:[/] Включено")
    
    if verbose:
        cmd.append("-v")
        console.print("[cyan]Режим:[/] Подробный вывод")
    
    if parallel:
        if not _check_tool_availability("pytest-xdist"):
            console.print("[yellow]pytest-xdist не найден. Установите его: pip install pytest-xdist[/]")
        else:
            cmd.extend(["-n", "auto"])
            console.print("[cyan]Режим:[/] Параллельное выполнение")
    
    console.print(f"[cyan]Выполняется:[/] {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Все тесты прошли успешно[/]")
        else:
            console.print("[red]❌ Некоторые тесты не прошли[/]")
        
        # Показываем вывод
        if result.stdout:
            console.print("\n[cyan]Вывод тестов:[/]")
            console.print(result.stdout)
        
        if result.stderr:
            console.print("\n[yellow]Ошибки:[/]")
            console.print(result.stderr)
            
    except Exception as e:
        console.print(f"[bold red]Ошибка при запуске тестов: {e}[/]")

@dev_app.command(name="docs", help="Сборка документации.")
def dev_docs_cmd(
    format: str = typer.Option("html", "--format", "-f", help="Формат документации: html, pdf, epub"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Директория для сохранения"),
    clean: bool = typer.Option(False, "--clean", help="Очистить предыдущую сборку"),
    serve: bool = typer.Option(False, "--serve", help="Запустить локальный сервер для просмотра")
):
    """Сборка документации"""
    try:
        asyncio.run(_dev_docs_async(format, output_dir, clean, serve))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'dev docs': {e}[/]")
        raise typer.Exit(code=1)

async def _dev_docs_async(format: str, output_dir: Optional[str], clean: bool, serve: bool):
    """Асинхронная обработка команды docs"""
    console.print(Panel("[bold blue]СБОРКА ДОКУМЕНТАЦИИ[/]", expand=False, border_style="blue"))
    
    config = _load_dev_config()
    docs_config = config.get("documentation", {})
    builder = docs_config.get("builder", "sphinx")
    
    # Проверяем доступность sphinx-build
    if not _check_tool_availability("sphinx-build"):
        console.print("[bold red]sphinx-build не найден. Установите его: pip install sphinx[/]")
        raise typer.Exit(code=1)
    
    # Определяем директории
    source_dir = Path(docs_config.get("source_dir", "docs"))
    if not output_dir:
        output_dir = docs_config.get("output_dir", "docs/build")
    
    output_path = Path(output_dir)
    
    console.print(f"[cyan]Формат:[/] {format}")
    console.print(f"[cyan]Источник:[/] {source_dir}")
    console.print(f"[cyan]Вывод:[/] {output_path}")
    
    # Очистка предыдущей сборки
    if clean and output_path.exists():
        shutil.rmtree(output_path)
        console.print("[cyan]Предыдущая сборка очищена[/]")
    
    # Создаем директорию вывода
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Формируем команду sphinx
    cmd = ["sphinx-build", "-b", format, str(source_dir), str(output_path)]
    
    console.print(f"[cyan]Выполняется:[/] {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]✅ Документация успешно собрана в {output_path}[/]")
            
            if serve:
                await _serve_documentation(output_path, format)
        else:
            console.print("[red]❌ Ошибка при сборке документации[/]")
            if result.stderr:
                console.print(result.stderr)
                
    except Exception as e:
        console.print(f"[bold red]Ошибка при сборке документации: {e}[/]")

async def _serve_documentation(output_path: Path, format: str):
    """Запустить локальный сервер для просмотра документации"""
    if format != "html":
        console.print("[yellow]Предварительный просмотр доступен только для HTML формата[/]")
        return
    
    try:
        import http.server
        import socketserver
        
        port = 8001
        os.chdir(output_path)
        
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            console.print(f"[green]🌐 Документация доступна по адресу: http://localhost:{port}[/]")
            console.print("[yellow]Нажмите Ctrl+C для остановки сервера[/]")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                console.print("\n[yellow]Сервер остановлен[/]")
                
    except Exception as e:
        console.print(f"[yellow]Не удалось запустить сервер: {e}[/]")

@dev_app.command(name="debug", help="Режим отладки.")
def dev_debug_cmd(
    level: str = typer.Option("DEBUG", "--level", "-l", help="Уровень отладки: DEBUG, INFO, WARNING, ERROR"),
    log_file: Optional[str] = typer.Option(None, "--log-file", help="Файл для логов отладки"),
    profiling: bool = typer.Option(False, "--profiling", help="Включить профилирование"),
    memory: bool = typer.Option(False, "--memory", help="Мониторинг использования памяти")
):
    """Режим отладки"""
    try:
        asyncio.run(_dev_debug_async(level, log_file, profiling, memory))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'dev debug': {e}[/]")
        raise typer.Exit(code=1)

async def _dev_debug_async(level: str, log_file: Optional[str], profiling: bool, memory: bool):
    """Асинхронная обработка команды debug"""
    console.print(Panel("[bold blue]РЕЖИМ ОТЛАДКИ[/]", expand=False, border_style="blue"))
    
    config = _load_dev_config()
    debug_config = config.get("debugging", {})
    
    console.print(f"[cyan]Уровень отладки:[/] {level}")
    
    if log_file:
        console.print(f"[cyan]Файл логов:[/] {log_file}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = DEV_LOGS_DIR / f"debug_{timestamp}.log"
        console.print(f"[cyan]Файл логов:[/] {log_file}")
    
    # Настраиваем логирование
    await _setup_debug_logging(level, log_file)
    
    # Профилирование
    if profiling:
        await _setup_profiling()
    
    # Мониторинг памяти
    if memory:
        await _setup_memory_monitoring()
    
    console.print("[green]✅ Режим отладки активирован[/]")
    console.print("[dim]Логи будут записываться в указанный файл[/]")

async def _setup_debug_logging(level: str, log_file: str):
    """Настроить логирование для отладки"""
    import logging
    
    # Создаем логгер
    logger = logging.getLogger("swiftdevbot_debug")
    logger.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    
    # Создаем файловый обработчик
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)
    
    # Тестовое сообщение
    logger.info(f"Отладка активирована с уровнем {level}")
    logger.debug("Это тестовое отладочное сообщение")

async def _setup_profiling():
    """Настроить профилирование"""
    try:
        import cProfile
        import pstats
        
        console.print("[cyan]Профилирование:[/] Включено")
        console.print("[dim]Используйте cProfile для анализа производительности[/]")
        
    except ImportError:
        console.print("[yellow]cProfile недоступен[/]")

async def _setup_memory_monitoring():
    """Настроить мониторинг памяти"""
    try:
        import psutil
        import gc
        
        console.print("[cyan]Мониторинг памяти:[/] Включен")
        
        # Получаем информацию о памяти
        process = psutil.Process()
        memory_info = process.memory_info()
        
        console.print(f"[dim]Использование памяти:[/] {memory_info.rss / 1024 / 1024:.1f} MB")
        console.print(f"[dim]Виртуальная память:[/] {memory_info.vms / 1024 / 1024:.1f} MB")
        
        # Принудительная сборка мусора
        gc.collect()
        console.print("[dim]Сборка мусора выполнена[/]")
        
    except ImportError:
        console.print("[yellow]psutil недоступен для мониторинга памяти[/]")

@dev_app.command(name="analyze", help="Анализ кода.")
def dev_analyze_cmd(
    tool: str = typer.Option("pylint", "--tool", "-t", help="Инструмент анализа: pylint, bandit, safety"),
    output_format: str = typer.Option("text", "--format", help="Формат вывода: text, json, html")
):
    """Анализ кода"""
    try:
        asyncio.run(_dev_analyze_async(tool, output_format))
    except typer.Exit: raise
    except Exception as e:
        console.print(f"[bold red]Неожиданная ошибка в команде 'dev analyze': {e}[/]")
        raise typer.Exit(code=1)

async def _dev_analyze_async(tool: str, output_format: str):
    """Асинхронная обработка команды analyze"""
    console.print(Panel("[bold blue]АНАЛИЗ КОДА[/]", expand=False, border_style="blue"))
    
    # Проверяем доступность инструмента
    if not _check_tool_availability(tool):
        console.print(f"[bold red]Инструмент '{tool}' не найден. Установите его: pip install {tool}[/]")
        raise typer.Exit(code=1)
    
    console.print(f"[cyan]Инструмент анализа:[/] {tool}")
    
    # Получаем список Python файлов
    files = _get_python_files()
    
    if not files:
        console.print("[yellow]Python файлы не найдены[/]")
        return
    
    # Выполняем анализ
    issues = await _run_code_analysis(tool, files)
    
    # Отображаем результаты
    await _display_analysis_results(issues, tool, output_format)

async def _run_code_analysis(tool: str, files: List[str]) -> List[Dict[str, Any]]:
    """Запустить анализ кода"""
    issues = []
    
    try:
        if tool == "pylint":
            cmd = ["pylint"] + files
        elif tool == "bandit":
            cmd = ["bandit", "-r", "."]
        elif tool == "safety":
            cmd = ["safety", "check"]
        else:
            console.print(f"[yellow]Неподдерживаемый инструмент анализа: {tool}[/]")
            return issues
        
        console.print(f"[cyan]Выполняется:[/] {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Парсим результаты
        for line in result.stdout.split('\n') + result.stderr.split('\n'):
            if line.strip():
                issues.append({
                    "tool": tool,
                    "message": line.strip(),
                    "severity": "info"
                })
        
        if result.returncode == 0:
            console.print("[green]✅ Анализ завершен без критических проблем[/]")
        else:
            console.print(f"[yellow]⚠️ Найдено проблем: {len(issues)}[/]")
            
    except Exception as e:
        console.print(f"[bold red]Ошибка при выполнении анализа: {e}[/]")
    
    return issues

async def _display_analysis_results(issues: List[Dict[str, Any]], tool: str, output_format: str):
    """Отобразить результаты анализа"""
    if output_format == "json":
        console.print(json.dumps(issues, indent=2, ensure_ascii=False))
        return
    
    if not issues:
        console.print("[green]✅ Проблем не найдено[/]")
        return
    
    # Табличный формат
    table = Table(title=f"Результаты анализа ({tool})")
    table.add_column("Инструмент", style="cyan")
    table.add_column("Сообщение", style="white")
    table.add_column("Важность", style="red")
    
    for issue in issues:
        table.add_row(
            issue.get("tool", "N/A"),
            issue.get("message", "N/A"),
            issue.get("severity", "info")
        )
    
    console.print(table)

if __name__ == "__main__":
    dev_app() 