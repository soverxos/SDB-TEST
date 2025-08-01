#!/usr/bin/env python3
"""
Быстрый тест для проверки отдельных команд monitor и utils
Используйте для быстрого тестирования конкретных команд
"""

import subprocess
import sys
from pathlib import Path

def run_command(command: str, description: str = "") -> bool:
    """Выполняет команду и показывает результат"""
    print(f"\n🔧 Выполняю: {command}")
    if description:
        print(f"📝 Описание: {description}")
    
    try:
        # Активируем виртуальное окружение и используем python3
        full_command = f"source .venv/bin/activate && python3 {command}"
        
        result = subprocess.run(
            full_command,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ Команда выполнена успешно!")
            if result.stdout.strip():
                print("📤 Вывод:")
                print(result.stdout)
            return True
        else:
            print("❌ Команда завершилась с ошибкой!")
            if result.stderr.strip():
                print("📤 Ошибка:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Команда превысила таймаут (30 секунд)")
        return False
    except Exception as e:
        print(f"💥 Ошибка выполнения: {e}")
        return False

def test_monitor_commands():
    """Тестирует команды monitor"""
    print("\n" + "="*60)
    print("📊 ТЕСТИРОВАНИЕ КОМАНД MONITOR")
    print("="*60)
    
    monitor_commands = [
        # Status команды
        ("sdb.py monitor status", "Проверка базового статуса"),
        ("sdb.py monitor status --detailed", "Проверка подробного статуса"),
        ("sdb.py monitor status --json", "Проверка статуса в JSON"),
        ("sdb.py monitor status --health", "Проверка здоровья системы"),
        
        # Metrics команды
        ("sdb.py monitor metrics", "Проверка базовых метрик"),
        ("sdb.py monitor metrics --cpu --memory", "Проверка CPU и памяти"),
        ("sdb.py monitor metrics --disk --network", "Проверка диска и сети"),
        
        # Alerts команды
        ("sdb.py monitor alerts --list", "Проверка списка алертов"),
        ("sdb.py monitor alerts --history", "Проверка истории алертов"),
        
        # Logs команды
        ("sdb.py monitor logs --analyze", "Проверка анализа логов"),
        ("sdb.py monitor logs --errors", "Проверка ошибок в логах"),
        ("sdb.py monitor logs --last 5", "Проверка последних 5 записей"),
        ("sdb.py monitor logs --search error", "Поиск ошибок в логах"),
        
        # Performance команды
        ("sdb.py monitor performance", "Проверка производительности"),
        ("sdb.py monitor performance --slow-queries", "Проверка медленных запросов"),
        ("sdb.py monitor performance --response-time", "Проверка времени ответа"),
        ("sdb.py monitor performance --memory-leaks", "Проверка утечек памяти"),
        
        # Report команды
        ("sdb.py monitor report --daily", "Проверка ежедневного отчета"),
        ("sdb.py monitor report --weekly --format html", "Проверка еженедельного HTML отчета"),
        
        # Integrate команды
        ("sdb.py monitor integrate --prometheus --grafana", "Проверка интеграции с Prometheus/Grafana"),
        ("sdb.py monitor integrate --datadog", "Проверка интеграции с DataDog"),
    ]
    
    success_count = 0
    total_count = len(monitor_commands)
    
    for command, description in monitor_commands:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📈 Результаты monitor: {success_count}/{total_count} успешных команд")
    return success_count, total_count

def test_utils_commands():
    """Тестирует команды utils"""
    print("\n" + "="*60)
    print("🛠️ ТЕСТИРОВАНИЕ КОМАНД UTILS")
    print("="*60)
    
    utils_commands = [
        # Diagnose команды
        ("sdb.py utils diagnose", "Проверка полной диагностики"),
        ("sdb.py utils diagnose --system", "Проверка диагностики системы"),
        ("sdb.py utils diagnose --network", "Проверка диагностики сети"),
        ("sdb.py utils diagnose --database", "Проверка диагностики БД"),
        ("sdb.py utils diagnose --security", "Проверка диагностики безопасности"),
        ("sdb.py utils diagnose --detailed", "Проверка подробной диагностики"),
        
        # Check команды
        ("sdb.py utils check --files", "Проверка файлов"),
        ("sdb.py utils check --database", "Проверка БД"),
        ("sdb.py utils check --config", "Проверка конфигурации"),
        ("sdb.py utils check --permissions", "Проверка прав доступа"),
        ("sdb.py utils check --all", "Полная проверка"),
        
        # Cleanup команды (только безопасные)
        ("sdb.py utils cleanup --temp", "Проверка очистки временных файлов"),
        ("sdb.py utils cleanup --cache", "Проверка очистки кэша"),
    ]
    
    success_count = 0
    total_count = len(utils_commands)
    
    for command, description in utils_commands:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📈 Результаты utils: {success_count}/{total_count} успешных команд")
    return success_count, total_count

def test_convert_commands():
    """Тестирует команды конвертации с тестовыми файлами"""
    print("\n" + "="*60)
    print("🔄 ТЕСТИРОВАНИЕ КОМАНД КОНВЕРТАЦИИ")
    print("="*60)
    
    # Создаем тестовые файлы
    test_files = {
        "quick_test.json": '{"name": "quick_test", "value": 456, "items": ["x", "y", "z"]}',
        "quick_test.csv": "name,value,type\nquick_test,456,number\nsample,789,string",
    }
    
    project_root = Path(__file__).parent
    
    # Создаем файлы
    for filename, content in test_files.items():
        filepath = project_root / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Создан тестовый файл: {filename}")
        except Exception as e:
            print(f"❌ Не удалось создать {filename}: {e}")
            return 0, 0
    
    convert_commands = [
        ("sdb.py utils convert quick_test.json quick_test.yaml", "JSON в YAML"),
        ("sdb.py utils convert quick_test.csv quick_test_output.json --format json", "CSV в JSON"),
    ]
    
    success_count = 0
    total_count = len(convert_commands)
    
    for command, description in convert_commands:
        if run_command(command, description):
            success_count += 1
    
    # Удаляем тестовые файлы
    for filename in test_files.keys():
        filepath = project_root / filename
        try:
            if filepath.exists():
                filepath.unlink()
            # Удаляем также сконвертированные файлы
            for ext in ['.yaml', '.json']:
                converted_file = project_root / f"quick_test{ext}"
                if converted_file.exists():
                    converted_file.unlink()
                output_file = project_root / f"quick_test_output{ext}"
                if output_file.exists():
                    output_file.unlink()
            print(f"✅ Удален тестовый файл: {filename}")
        except Exception as e:
            print(f"❌ Не удалось удалить {filename}: {e}")
    
    print(f"\n📈 Результаты конвертации: {success_count}/{total_count} успешных команд")
    return success_count, total_count

def test_encrypt_commands():
    """Тестирует команды шифрования"""
    print("\n" + "="*60)
    print("🔐 ТЕСТИРОВАНИЕ КОМАНД ШИФРОВАНИЯ")
    print("="*60)
    
    # Создаем тестовый файл
    test_content = "Это секретные данные для быстрого тестирования шифрования"
    test_file = Path(__file__).parent / "quick_secret.txt"
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Создан тестовый файл: quick_secret.txt")
    except Exception as e:
        print(f"❌ Не удалось создать тестовый файл: {e}")
        return 0, 0
    
    encrypt_commands = [
        ("sdb.py utils encrypt quick_secret.txt quick_secret.enc --password testpass", "Шифрование файла"),
        ("sdb.py utils decrypt quick_secret.enc quick_secret_decrypted.txt --password testpass", "Расшифровка файла"),
    ]
    
    success_count = 0
    total_count = len(encrypt_commands)
    
    for command, description in encrypt_commands:
        if run_command(command, description):
            success_count += 1
    
    # Проверяем что файлы одинаковые
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(Path(__file__).parent / "quick_secret_decrypted.txt", 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        if original_content == decrypted_content:
            print("✅ Проверка шифрования: оригинал и расшифрованный файл идентичны")
            success_count += 1
        else:
            print("❌ Проверка шифрования: файлы различаются")
        total_count += 1
    except Exception as e:
        print(f"❌ Не удалось проверить шифрование: {e}")
        total_count += 1
    
    # Удаляем тестовые файлы
    test_files_to_remove = ["quick_secret.txt", "quick_secret.enc", "quick_secret_decrypted.txt"]
    for filename in test_files_to_remove:
        filepath = Path(__file__).parent / filename
        try:
            if filepath.exists():
                filepath.unlink()
            # Удаляем также файлы ключей
            key_file = Path(__file__).parent / f"{filename}.key"
            if key_file.exists():
                key_file.unlink()
            print(f"✅ Удален тестовый файл: {filename}")
        except Exception as e:
            print(f"❌ Не удалось удалить {filename}: {e}")
    
    print(f"\n📈 Результаты шифрования: {success_count}/{total_count} успешных команд")
    return success_count, total_count

def test_help_commands():
    """Тестирует команды справки"""
    print("\n" + "="*60)
    print("🔍 ТЕСТИРОВАНИЕ КОМАНД СПРАВКИ")
    print("="*60)
    
    help_commands = [
        ("sdb.py --help", "Основная справка"),
        ("sdb.py monitor --help", "Справка monitor"),
        ("sdb.py utils --help", "Справка utils"),
        ("sdb.py monitor status --help", "Справка monitor status"),
        ("sdb.py utils diagnose --help", "Справка utils diagnose"),
    ]
    
    success_count = 0
    total_count = len(help_commands)
    
    for command, description in help_commands:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📈 Результаты справки: {success_count}/{total_count} успешных команд")
    return success_count, total_count

def main():
    """Главная функция"""
    print("🚀 БЫСТРОЕ ТЕСТИРОВАНИЕ КОМАНД MONITOR И UTILS")
    print("="*60)
    
    # Проверяем что мы в правильной директории
    project_root = Path(__file__).parent
    if not (project_root / "sdb.py").exists():
        print("❌ Ошибка: sdb.py не найден в текущей директории")
        return 1
    
    # Проверяем виртуальное окружение
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("❌ Ошибка: Виртуальное окружение .venv не найдено")
        return 1
    
    print("✅ Виртуальное окружение найдено")
    
    # Запускаем тесты
    total_success = 0
    total_commands = 0
    
    # Тестируем справку
    success, total = test_help_commands()
    total_success += success
    total_commands += total
    
    # Тестируем monitor
    success, total = test_monitor_commands()
    total_success += success
    total_commands += total
    
    # Тестируем utils
    success, total = test_utils_commands()
    total_success += success
    total_commands += total
    
    # Тестируем конвертацию
    success, total = test_convert_commands()
    total_success += success
    total_commands += total
    
    # Тестируем шифрование
    success, total = test_encrypt_commands()
    total_success += success
    total_commands += total
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    print(f"Всего команд: {total_commands}")
    print(f"Успешных: {total_success}")
    print(f"Неудачных: {total_commands - total_success}")
    print(f"Процент успеха: {(total_success/total_commands*100):.1f}%")
    
    if total_success == total_commands:
        print("\n🎉 Все команды прошли успешно!")
        return 0
    else:
        print("\n⚠️ Некоторые команды завершились неудачно.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 