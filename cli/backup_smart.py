# --- Файл: cli/backup_smart.py ---
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="backup-smart",
    help="\U0001F50D Умный резерв с хешами и синхронизацией данных",
    no_args_is_help=True
)

console = Console()

# === Утилиты ===
def sha256(file_path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_directory(path: Path, excludes: Optional[list[str]] = None) -> dict[str, str]:
    hashes = {}
    excludes = excludes or []
    for file in path.rglob("*"):
        if file.is_file():
            rel_path = file.relative_to(path).as_posix()
            # Проверяем, не исключён ли файл
            if any(rel_path.startswith(exclude) for exclude in excludes):
                continue
            hashes[rel_path] = sha256(file)
    return hashes

# === Команды ===
@app.command("scan")
def scan(
    path: Path = typer.Argument(..., help="Путь к директории, которую нужно просканировать"),
    out: Path = typer.Option("hashes.json", help="Путь, куда сохранить hashes.json")
):
    """Просканировать директорию и сохранить хеши файлов."""
    hashes = scan_directory(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)
    console.print(f"[green]✅ Хеши сохранены в [bold]{out}[/] ({len(hashes)} файлов)")

@app.command("diff")
def diff(
    path: Path = typer.Argument(..., help="Текущая директория с файлами"),
    ref: Path = typer.Option("hashes.json", help="Файл с эталонными хешами")
):
    """Сравнить текущие файлы с сохранёнными хешами."""
    current = scan_directory(path)
    with open(ref, encoding="utf-8") as f:
        old = json.load(f)

    table = Table(title="\U0001F4CA Изменения")
    table.add_column("Файл", style="cyan")
    table.add_column("Статус", style="magenta")

    found_changes = False

    for k, v in current.items():
        if k not in old:
            table.add_row(k, "[green]Новый[/]")
            found_changes = True
        elif old[k] != v:
            table.add_row(k, "[yellow]Изменён[/]")
            found_changes = True

    for k in old:
        if k not in current:
            table.add_row(k, "[red]Удалён[/]")
            found_changes = True

    if found_changes:
        console.print(table)
    else:
        console.print("[green]✔ Нет изменений. Все файлы совпадают с эталоном.[/]")

@app.command("sync")
def sync(
    path: Path = typer.Argument(..., help="Директория с исходными файлами"),
    ref: Path = typer.Option("hashes.json", help="Файл с хешами для сравнения"),
    to: Path = typer.Option(..., help="Куда копировать новые/изменённые файлы")
):
    """Синхронизировать новые/изменённые файлы с бэкап-папкой."""
    current = scan_directory(path)
    with open(ref, encoding="utf-8") as f:
        old = json.load(f)

    changed = [k for k in current if k not in old or old[k] != current[k]]

    console.print(f"[cyan]\U0001F4E6 Копируется: {len(changed)} файлов[/]")
    for rel_path in changed:
        src = path / rel_path
        dest = to / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    # Обновить hashes.json в целевой папке
    to_hash_path = to / "hashes.json"
    with open(to_hash_path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    console.print(f"[green]✅ Синхронизация завершена. Обновлён [bold]{to_hash_path}[/]")

@app.command("full")
def full_backup(
    source: Path = typer.Argument(..., help="Путь к директории, которую бэкапим"),
    path: Optional[Path] = typer.Option(None, "--path", help="Путь к папке, куда будет создан бэкап (по умолчанию ./backup/smart_<timestamp>)"),
    dest: Optional[Path] = typer.Option(None, "--dest", help="Синоним --path. Путь к папке, куда будет создан бэкап (по умолчанию ./backup/smart_<timestamp>)"),
    exclude: Optional[list[str]] = typer.Option(None, "--exclude", help="Список путей для исключения (например: project_data, .git, .venv)")
):
    """Полный умный бэкап: scan + sync."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Используем папку backup в корне проекта
    project_root = Path(__file__).resolve().parent.parent
    backup_dir = project_root / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = path or dest or backup_dir / f"smart_{timestamp}"
    target = Path(target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    hash_file = target / "hashes.json"
    console.print(f"[bold cyan]\nНачинается полный бэкап...[/]")
    if exclude:
        console.print(f"[yellow]Исключаемые пути: {', '.join(exclude)}[/]")

    hashes = scan_directory(source, excludes=exclude)
    with open(hash_file, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)

    for rel_path in hashes:
        src = source / rel_path
        dest_path = target / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_path)

    console.print(f"[green]✅ Полный бэкап завершён в [bold]{target}[/]")

# --- Конец cli/backup_smart.py ---
