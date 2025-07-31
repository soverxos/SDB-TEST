from pathlib import Path

# Имя корневой папки проекта (если скрипт внутри нее, то ".")
PROJECT_ROOT_NAME = "." # Если скрипт в корне SwiftDevBot
# Если скрипт снаружи, то PROJECT_ROOT_NAME = "SwiftDevBot"

def create_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    print(f"Создана директория: {path}")

def create_file(path: Path, content: str = ""):
    path.touch(exist_ok=True)
    if content:
        path.write_text(content, encoding='utf-8')
    print(f"Создан файл: {path}")

def main():
    project_root = Path(PROJECT_ROOT_NAME).resolve()
    
    if PROJECT_ROOT_NAME != ".": # Если скрипт не в корне, создаем корень
        create_dir(project_root)

    print(f"Создание структуры для проекта: {project_root}")

    # 1. Файлы и папки в корне проекта
    create_file(project_root / ".env")
    create_file(project_root / "run_bot.py")
    create_file(project_root / "sdb.py") # Или sdb без расширения, если потом сделаешь исполняемым
    create_file(project_root / "requirements.txt")
    create_file(project_root / "requirements-dev.txt")
    create_file(project_root / "alembic.ini")
    create_file(project_root / "config.yaml", "# Шаблон/дефолтный конфиг")
    
    # 2. Директория ядра core/
    core_path = project_root / "core"
    core_subdirs = ["database", "cache", "http_client", "ui", "rbac", "utils_core", "i18n", "events"]
    for subdir in core_subdirs:
        create_dir(core_path / subdir)
        create_file(core_path / subdir / "__init__.py")

    create_file(core_path / "__init__.py")
    create_file(core_path / "app_settings.py")
    create_file(core_path / "services_provider.py")
    create_file(core_path / "bot_entrypoint.py")
    create_file(core_path / "module_loader.py")

    create_file(core_path / "database" / "base.py")
    create_file(core_path / "database" / "manager.py")
    create_file(core_path / "database" / "core_models.py")

    create_file(core_path / "cache" / "manager.py")
    create_file(core_path / "http_client" / "manager.py")

    create_file(core_path / "ui" / "keyboards_core.py")
    create_file(core_path / "ui" / "navigation_core.py")
    create_file(core_path / "ui" / "registry_ui.py")
    # create_file(core_path / "ui" / "callback_data_factories.py")

    create_file(core_path / "i18n" / "middleware.py")
    create_file(core_path / "i18n" / "translator.py")

    create_file(core_path / "events" / "dispatcher.py")
    
    create_file(core_path / "rbac" / "service.py")
    create_file(core_path / "utils_core" / "__init__.py") # Уже создан выше, но для полноты
    # create_file(core_path / "utils_core" / "command_utils.py")

    # 3. Директория модулей modules/
    modules_path = project_root / "modules"
    create_dir(modules_path)
    create_file(modules_path / "__init__.py")
    create_file(modules_path / ".gitkeep")

    system_module_path = modules_path / "system_base_module"
    create_dir(system_module_path)
    create_file(system_module_path / "__init__.py")
    create_file(system_module_path / "handlers_system.py")
    create_file(system_module_path / "keyboards_system.py")
    create_file(system_module_path / "manifest.yaml") # или .json

    example_module_path = modules_path / "example_module"
    create_dir(example_module_path)
    create_file(example_module_path / "__init__.py")
    create_file(example_module_path / "handlers_example.py")
    create_file(example_module_path / "keyboards_example.py")
    create_file(example_module_path / "models_example.py")
    create_file(example_module_path / "manifest.yaml") # или .json

    # 4. Директория для логики CLI команд cli_commands/
    cli_commands_path = project_root / "cli_commands"
    create_dir(cli_commands_path)
    create_file(cli_commands_path / "__init__.py")
    create_file(cli_commands_path / "setup_cmd.py")
    create_file(cli_commands_path / "db_cmd.py")
    create_file(cli_commands_path / "module_cmd.py")
    create_file(cli_commands_path / "user_cmd.py")
    create_file(cli_commands_path / "backup_cmd.py")
    create_file(cli_commands_path / "system_cmd.py")
    create_file(cli_commands_path / "cli_utils.py")

    # 5. Директория для миграций Alembic alembic_migrations/
    alembic_path = project_root / "alembic_migrations"
    create_dir(alembic_path / "versions") # versions создается alembic init
    create_file(alembic_path / "versions" / ".gitkeep") # Чтобы versions папка была
    # Для env.py и script.py.mako лучше, чтобы их создал alembic init
    # Но можно создать пустые заглушки, если alembic init не запускать сразу
    create_file(alembic_path / "env.py", "# Alembic env.py - настройте для SDB") 
    create_file(alembic_path / "script.py.mako", '"""${message} ..."""\n# ... (стандартный шаблон)')


    # 6. Директория для данных проекта project_data/
    project_data_path = project_root / "project_data"
    data_subdirs = ["Config", "Logs", "Cache_data", "Database_files", "module_backups", "core_backups"]
    for subdir in data_subdirs:
        create_dir(project_data_path / subdir)
        create_file(project_data_path / subdir / ".gitkeep")
    
    create_file(project_data_path / ".gitignore", "*\n!.gitignore\n!*/\n!.gitkeep\n")
    # create_file(project_data_path / "Config" / "core_settings.yaml") # Создастся через sdb setup
    # create_file(project_data_path / "Config" / "enabled_modules.json")

    # 7. Папка для локализации locales/
    locales_path = project_root / "locales"
    create_dir(locales_path / "en" / "LC_MESSAGES")
    create_dir(locales_path / "ua" / "LC_MESSAGES")
    create_file(locales_path / "bot.pot")
    create_file(locales_path / "en" / "LC_MESSAGES" / "bot.po")
    create_file(locales_path / "ua" / "LC_MESSAGES" / "bot.po")
    
    # 8. Папка для тестов tests/ (опционально)
    # tests_path = project_root / "tests"
    # tests_subdirs = ["core_tests", "module_tests", "cli_tests"]
    # create_dir(tests_path)
    # create_file(tests_path / "__init__.py")
    # for subdir in tests_subdirs:
    #     create_dir(tests_path / subdir)
    #     create_file(tests_path / subdir / "__init__.py")
    # create_file(tests_path / "smoke_test_cli.py")

    print("\nСтруктура проекта SwiftDevBot создана с использованием Python скрипта!")
    print("Рекомендации:")
    print("1. Выполните 'alembic init alembic_migrations' в корне проекта, если хотите, чтобы Alembic сам создал env.py и script.py.mako.")
    print("   (перед этим удалите alembic_migrations/env.py и alembic_migrations/script.py.mako, если они были созданы этим скриптом).")
    print("2. Не забудьте настроить alembic.ini (script_location = alembic_migrations) и сам alembic_migrations/env.py.")
    print("3. Настройте .gitignore в корне проекта.")

if __name__ == "__main__":
    main()