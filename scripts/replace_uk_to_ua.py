# SwiftDevBot/scripts/replace_uk_to_ua.py
import os
from pathlib import Path
import re

# --- Настройки ---
PROJECT_ROOT = Path(".")  # Запускать из корня проекта SwiftDevBot
FILE_EXTENSIONS_TO_PROCESS = {".py", ".yaml", ".yml", ".json", ".md", ".env", ".po", ".pot", ".example", ".ini"}
EXCLUDE_DIRS_SCRIPT = {".git", ".venv", "__pycache__", "docs", "site", "build", "dist", "project_snapshot.txt"} 
DRY_RUN = False # Если True, скрипт только покажет, что он бы заменил, но не будет изменять файлы

REPLACEMENT_PATTERNS = {
    r"(['\"])uk\1": r"\1ua\1",
    r"(\buk\b)(?=[/\s,\]\}])": r"ua",
    r"Language: ua": r"Language: ua",
    r'(available_locales:\s*\[[^\]]*?)(\buk\b)([^\]]*?\])': r'\1ua\3', 
    r'(default_locale:\s*[\'"])uk([\'"])': r'\1ua\2', 
    r'(SDB_I18N_AVAILABLE_LOCALES\s*=\s*[\'"])([^\'"]*?)(\buk\b)([^\'"]*)([\'"])': r'\1\2ua\4\5', 
    r'(SDB_I18N_DEFAULT_LOCALE\s*=\s*[\'"])uk([\'"])': r'\1ua\2', 
}

RENAME_PATTERNS = {
    lambda p: p.is_dir() and p.name == "ua" and p.parent.name == "locales" and p.parent.parent == PROJECT_ROOT.resolve(): lambda p: p.with_name("ua"),
}

changed_content_files = set()
renamed_paths_log = []


def process_file_content(file_path: Path, dry_run: bool) -> int:
    global changed_content_files
    changes_count = 0
    try:
        content = file_path.read_text(encoding="utf-8")
        # original_content = content # Не используется, можно убрать
        
        file_actually_changed_by_script = False
        current_content_for_file = content # Работаем с этой переменной

        for pattern, replacement in REPLACEMENT_PATTERNS.items():
            # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # re.subn(pattern, replacement, string, ...)
            new_content_after_sub, num_subs = re.subn(pattern, replacement, current_content_for_file, flags=re.IGNORECASE)
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
            if num_subs > 0:
                current_content_for_file = new_content_after_sub # Применяем изменение для следующего паттерна
                changes_count += num_subs
                file_actually_changed_by_script = True
                if dry_run:
                    # Для DRY_RUN просто сообщаем о потенциальном изменении, не меняя 'content' для записи
                    print(f"[DRY RUN] Would change content in {file_path} (pattern: '{pattern}') - {num_subs} occurrences")
                else:
                    print(f"Changed content in {file_path} (pattern: '{pattern}') - {num_subs} occurrences")
        
        if file_actually_changed_by_script: 
            changed_content_files.add(file_path.relative_to(PROJECT_ROOT)) 
            if not dry_run:
                # Записываем финальный измененный контент
                file_path.write_text(current_content_for_file, encoding="utf-8")
            
    except Exception as e:
        print(f"Error processing file content {file_path}: {e}")
    return changes_count

def rename_paths_script(root_path: Path, dry_run: bool):
    global renamed_paths_log
    local_renamed_paths_log = [] 

    paths_to_rename_candidates = []
    for path_obj in root_path.rglob("*"): 
        if any(excluded_dir in path_obj.parts for excluded_dir in EXCLUDE_DIRS_SCRIPT):
            continue
        for matcher_func, new_name_func in RENAME_PATTERNS.items():
            if matcher_func(path_obj):
                new_path = new_name_func(path_obj)
                if new_path != path_obj:
                     paths_to_rename_candidates.append((path_obj, new_path))
                break 

    paths_to_rename_candidates.sort(key=lambda x: len(x[0].parts), reverse=True)

    for old_path, new_path in paths_to_rename_candidates:
        if old_path.exists(): 
            log_entry = f"{old_path.relative_to(PROJECT_ROOT)} -> {new_path.relative_to(PROJECT_ROOT)}"
            if dry_run:
                print(f"[DRY RUN] Would rename: {log_entry}")
                local_renamed_paths_log.append(log_entry)
            else:
                try:
                    if new_path.exists():
                        print(f"Warning: Target path {new_path} already exists. Skipping rename of {old_path}")
                        continue
                    old_path.rename(new_path)
                    print(f"Renamed: {log_entry}")
                    local_renamed_paths_log.append(log_entry)
                except Exception as e:
                    print(f"Error renaming {old_path} to {new_path}: {e}")
    
    renamed_paths_log.extend(local_renamed_paths_log) 
    return bool(local_renamed_paths_log)


def main():
    global changed_content_files, renamed_paths_log
    total_files_processed = 0
    total_changes_made = 0

    print(f"Starting replacement process in {PROJECT_ROOT.resolve()}")
    if DRY_RUN:
        print("DRY RUN mode: No files will be modified.")

    print("\n--- Renaming paths ---")
    renamed_anything_paths = rename_paths_script(PROJECT_ROOT, DRY_RUN)
    if not DRY_RUN and renamed_anything_paths:
        print("Some paths were renamed. Content processing will use new paths if applicable.")
    elif not renamed_anything_paths:
        print("No paths matched renaming patterns.")

    print("\n--- Processing file content ---")
    for root_str, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        root_path = Path(root_str)
        
        if any(excluded_dir in root_path.relative_to(PROJECT_ROOT).parts for excluded_dir in EXCLUDE_DIRS_SCRIPT):
            dirs[:] = [] 
            continue

        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS_SCRIPT]
        
        for filename in files:
            file_path = root_path / filename
            if file_path.suffix.lower() in FILE_EXTENSIONS_TO_PROCESS:
                if any(excluded_dir in file_path.relative_to(PROJECT_ROOT).parts for excluded_dir in EXCLUDE_DIRS_SCRIPT):
                    continue
                
                changes = process_file_content(file_path, DRY_RUN)
                if changes > 0:
                    total_changes_made += changes
                total_files_processed += 1
    
    print("\n" + "="*20 + " SCRIPT EXECUTION SUMMARY " + "="*20)
    if DRY_RUN:
        print("\n⚠️  THIS WAS A DRY RUN. NO ACTUAL CHANGES WERE MADE TO FILES OR PATHS. ⚠️")

    print(f"\nTotal unique files with content changes: {len(changed_content_files)}")
    if changed_content_files:
        print("Files with content changes (relative to project root):")
        for f_path in sorted(list(changed_content_files)):
            print(f"  - {f_path}")
    
    print(f"\nTotal paths renamed: {len(renamed_paths_log)}")
    if renamed_paths_log:
        print("Renamed paths:")
        for entry in renamed_paths_log:
            print(f"  - {entry}")
            
    print(f"\nTotal individual text replacements made: {total_changes_made}")
    print(f"Total files scanned for content processing: {total_files_processed}")
    
    if not DRY_RUN and (changed_content_files or renamed_paths_log):
        print("\nRECOMMENDATION: Review all changes with 'git diff' before committing!")
    elif not DRY_RUN:
        print("No changes were made to file contents or paths.")

if __name__ == "__main__":
    if not DRY_RUN:
        confirm = input(
            "This script will attempt to modify project files and rename paths to replace 'ua' with 'ua'.\n"
            "🔥 MAKE SURE YOU HAVE A RELIABLE BACKUP (e.g., committed to Git). 🔥\n"
            "This operation can have unintended consequences if patterns are not precise.\n"
            "It's highly recommended to run with DRY_RUN=True first and review the output.\n\n"
            "Type 'YES_I_AM_ABSOLUTELY_SURE' to proceed with actual changes: "
        )
        if confirm != "YES_I_AM_ABSOLUTELY_SURE":
            print("Aborted by user.")
            exit()
    main()