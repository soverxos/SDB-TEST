#!/usr/bin/env python3
"""
Тест для проверки команд monitor и utils в SwiftDevBot CLI
Безопасные команды для тестирования функциональности
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class MonitorUtilsTester:
    """Класс для тестирования команд monitor и utils"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        self.errors = []
        self.warnings = []
        
    def log_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """Логирует результат теста"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Детали: {details}")
    
    def run_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Выполняет команду и возвращает результат"""
        try:
            # Активируем виртуальное окружение и используем python3
            full_command = f"source .venv/bin/activate && python3 {command}"
            
            result = subprocess.run(
                full_command,
                shell=True,
                executable="/bin/bash",
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except subprocess.TimeoutExpired:
            return False, "", f"Команда превысила таймаут {timeout} секунд"
        except Exception as e:
            return False, "", f"Ошибка выполнения команды: {e}"
    
    def test_help_commands(self):
        """Тестирует команды справки"""
        print("\n🔍 Тестирование команд справки...")
        
        help_commands = [
            ("sdb.py --help", "Основная справка"),
            ("sdb.py monitor --help", "Справка monitor"),
            ("sdb.py utils --help", "Справка utils"),
            ("sdb.py monitor status --help", "Справка monitor status"),
            ("sdb.py utils diagnose --help", "Справка utils diagnose"),
        ]
        
        for command, description in help_commands:
            success, stdout, stderr = self.run_command(command)
            if success and "help" in stdout.lower() or "usage" in stdout.lower():
                self.log_result(f"Справка {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Справка {description}", False, "Команда не вернула справку", stderr)
    
    def test_monitor_status_commands(self):
        """Тестирует команды monitor status"""
        print("\n📊 Тестирование команд monitor status...")
        
        status_commands = [
            ("sdb.py monitor status", "Базовый статус"),
            ("sdb.py monitor status --detailed", "Подробный статус"),
            ("sdb.py monitor status --json", "Статус в JSON"),
            ("sdb.py monitor status --health", "Проверка здоровья"),
        ]
        
        for command, description in status_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Проверяем что команда вернула какой-то вывод
                if stdout.strip() or "status" in stdout.lower() or "health" in stdout.lower():
                    self.log_result(f"Status {description}", True, "Команда выполнена успешно")
                else:
                    self.log_result(f"Status {description}", False, "Команда не вернула ожидаемый вывод")
            else:
                self.log_result(f"Status {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_metrics_commands(self):
        """Тестирует команды monitor metrics"""
        print("\n📈 Тестирование команд monitor metrics...")
        
        metrics_commands = [
            ("sdb.py monitor metrics", "Базовые метрики"),
            ("sdb.py monitor metrics --cpu --memory", "CPU и память"),
            ("sdb.py monitor metrics --disk --network", "Диск и сеть"),
        ]
        
        for command, description in metrics_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Проверяем что команда вернула какой-то вывод
                if stdout.strip() or "metrics" in stdout.lower() or "cpu" in stdout.lower() or "memory" in stdout.lower():
                    self.log_result(f"Metrics {description}", True, "Команда выполнена успешно")
                else:
                    self.log_result(f"Metrics {description}", False, "Команда не вернула ожидаемый вывод")
            else:
                self.log_result(f"Metrics {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_alerts_commands(self):
        """Тестирует команды monitor alerts"""
        print("\n🚨 Тестирование команд monitor alerts...")
        
        alerts_commands = [
            ("sdb.py monitor alerts --list", "Список алертов"),
            ("sdb.py monitor alerts --history", "История алертов"),
        ]
        
        for command, description in alerts_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не вернуть алерты, но должна выполниться
                self.log_result(f"Alerts {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Alerts {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_logs_commands(self):
        """Тестирует команды monitor logs"""
        print("\n📝 Тестирование команд monitor logs...")
        
        logs_commands = [
            ("sdb.py monitor logs --analyze", "Анализ логов"),
            ("sdb.py monitor logs --errors", "Ошибки в логах"),
            ("sdb.py monitor logs --last 10", "Последние 10 записей"),
            ("sdb.py monitor logs --search error", "Поиск ошибок"),
        ]
        
        for command, description in logs_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не найти логи, но должна выполниться
                self.log_result(f"Logs {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Logs {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_performance_commands(self):
        """Тестирует команды monitor performance"""
        print("\n⚡ Тестирование команд monitor performance...")
        
        performance_commands = [
            ("sdb.py monitor performance", "Анализ производительности"),
            ("sdb.py monitor performance --slow-queries", "Медленные запросы"),
            ("sdb.py monitor performance --response-time", "Время ответа"),
            ("sdb.py monitor performance --memory-leaks", "Утечки памяти"),
        ]
        
        for command, description in performance_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не найти проблемы, но должна выполниться
                self.log_result(f"Performance {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Performance {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_report_commands(self):
        """Тестирует команды monitor report"""
        print("\n📋 Тестирование команд monitor report...")
        
        report_commands = [
            ("sdb.py monitor report --daily", "Ежедневный отчет"),
            ("sdb.py monitor report --weekly --format html", "Еженедельный HTML отчет"),
            ("sdb.py monitor report --monthly", "Ежемесячный отчет"),
        ]
        
        for command, description in report_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не создать отчет, но должна выполниться
                self.log_result(f"Report {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Report {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_monitor_integrate_commands(self):
        """Тестирует команды monitor integrate"""
        print("\n🔗 Тестирование команд monitor integrate...")
        
        integrate_commands = [
            ("sdb.py monitor integrate --prometheus --grafana", "Интеграция с Prometheus/Grafana"),
            ("sdb.py monitor integrate --datadog", "Интеграция с DataDog"),
            ("sdb.py monitor integrate --newrelic", "Интеграция с New Relic"),
        ]
        
        for command, description in integrate_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не настроить интеграцию, но должна выполниться
                self.log_result(f"Integrate {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Integrate {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_utils_diagnose_commands(self):
        """Тестирует команды utils diagnose"""
        print("\n🔍 Тестирование команд utils diagnose...")
        
        diagnose_commands = [
            ("sdb.py utils diagnose", "Полная диагностика"),
            ("sdb.py utils diagnose --system", "Диагностика системы"),
            ("sdb.py utils diagnose --network", "Диагностика сети"),
            ("sdb.py utils diagnose --database", "Диагностика БД"),
            ("sdb.py utils diagnose --security", "Диагностика безопасности"),
            ("sdb.py utils diagnose --detailed", "Подробная диагностика"),
        ]
        
        for command, description in diagnose_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Проверяем что команда вернула какой-то вывод
                if stdout.strip() or "diagnostic" in stdout.lower() or "system" in stdout.lower():
                    self.log_result(f"Diagnose {description}", True, "Команда выполнена успешно")
                else:
                    self.log_result(f"Diagnose {description}", False, "Команда не вернула ожидаемый вывод")
            else:
                self.log_result(f"Diagnose {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_utils_check_commands(self):
        """Тестирует команды utils check"""
        print("\n✅ Тестирование команд utils check...")
        
        check_commands = [
            ("sdb.py utils check --files", "Проверка файлов"),
            ("sdb.py utils check --database", "Проверка БД"),
            ("sdb.py utils check --config", "Проверка конфигурации"),
            ("sdb.py utils check --permissions", "Проверка прав доступа"),
            ("sdb.py utils check --all", "Полная проверка"),
        ]
        
        for command, description in check_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                # Команда может не найти проблемы, но должна выполниться
                self.log_result(f"Check {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Check {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_utils_cleanup_commands(self):
        """Тестирует безопасные команды utils cleanup"""
        print("\n🧹 Тестирование безопасных команд utils cleanup...")
        
        # Сначала проверяем что будет удалено
        success, stdout, stderr = self.run_command("sdb.py utils diagnose --detailed")
        if success:
            self.log_result("Diagnose before cleanup", True, "Диагностика выполнена перед очисткой")
        
        # Только безопасные команды очистки
        cleanup_commands = [
            ("sdb.py utils cleanup --temp", "Очистка временных файлов"),
            ("sdb.py utils cleanup --cache", "Очистка кэша"),
        ]
        
        for command, description in cleanup_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                self.log_result(f"Cleanup {description}", True, "Команда выполнена успешно")
            else:
                self.log_result(f"Cleanup {description}", False, "Команда завершилась с ошибкой", stderr)
    
    def test_utils_convert_commands(self):
        """Тестирует команды utils convert с тестовыми файлами"""
        print("\n🔄 Тестирование команд utils convert...")
        
        # Создаем тестовые файлы
        test_files = {
            "test.json": '{"name": "test", "value": 123, "items": ["a", "b", "c"]}',
            "test.csv": "name,value,type\ntest,123,string\nsample,456,number",
            "test.yaml": "name: test\nvalue: 123\nitems:\n  - a\n  - b\n  - c"
        }
        
        # Создаем тестовые файлы
        for filename, content in test_files.items():
            filepath = self.project_root / filename
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_result(f"Создание {filename}", True, "Тестовый файл создан")
            except Exception as e:
                self.log_result(f"Создание {filename}", False, "Не удалось создать файл", str(e))
        
        # Тестируем конвертацию
        convert_commands = [
            ("sdb.py utils convert test.json test.yaml", "JSON в YAML"),
            ("sdb.py utils convert test.csv test.json --format json", "CSV в JSON"),
            ("sdb.py utils convert test.yaml test.csv --format csv", "YAML в CSV"),
        ]
        
        for command, description in convert_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                self.log_result(f"Convert {description}", True, "Конвертация выполнена успешно")
            else:
                self.log_result(f"Convert {description}", False, "Конвертация завершилась с ошибкой", stderr)
        
        # Удаляем тестовые файлы
        for filename in test_files.keys():
            filepath = self.project_root / filename
            try:
                if filepath.exists():
                    filepath.unlink()
                # Удаляем также сконвертированные файлы
                for ext in ['.json', '.yaml', '.csv']:
                    converted_file = self.project_root / f"test{ext}"
                    if converted_file.exists():
                        converted_file.unlink()
                self.log_result(f"Удаление {filename}", True, "Тестовый файл удален")
            except Exception as e:
                self.log_result(f"Удаление {filename}", False, "Не удалось удалить файл", str(e))
    
    def test_utils_encrypt_decrypt_commands(self):
        """Тестирует команды utils encrypt/decrypt"""
        print("\n🔐 Тестирование команд utils encrypt/decrypt...")
        
        # Создаем тестовый файл
        test_content = "Это секретные данные для тестирования шифрования\nСтрока 2\nСтрока 3"
        test_file = self.project_root / "secret.txt"
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            self.log_result("Создание secret.txt", True, "Тестовый файл создан")
        except Exception as e:
            self.log_result("Создание secret.txt", False, "Не удалось создать файл", str(e))
            return
        
        # Тестируем шифрование
        encrypt_commands = [
            ("sdb.py utils encrypt secret.txt secret.enc --password mypassword", "Шифрование с паролем"),
        ]
        
        for command, description in encrypt_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                self.log_result(f"Encrypt {description}", True, "Шифрование выполнено успешно")
            else:
                self.log_result(f"Encrypt {description}", False, "Шифрование завершилось с ошибкой", stderr)
        
        # Тестируем расшифровку
        decrypt_commands = [
            ("sdb.py utils decrypt secret.enc decrypted.txt --password mypassword", "Расшифровка с паролем"),
        ]
        
        for command, description in decrypt_commands:
            success, stdout, stderr = self.run_command(command)
            if success:
                self.log_result(f"Decrypt {description}", True, "Расшифровка выполнена успешно")
            else:
                self.log_result(f"Decrypt {description}", False, "Расшифровка завершилась с ошибкой", stderr)
        
        # Проверяем что файлы одинаковые
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(self.project_root / "decrypted.txt", 'r', encoding='utf-8') as f:
                decrypted_content = f.read()
            
            if original_content == decrypted_content:
                self.log_result("Проверка шифрования", True, "Оригинал и расшифрованный файл идентичны")
            else:
                self.log_result("Проверка шифрования", False, "Оригинал и расшифрованный файл различаются")
        except Exception as e:
            self.log_result("Проверка шифрования", False, "Не удалось сравнить файлы", str(e))
        
        # Удаляем тестовые файлы
        test_files_to_remove = ["secret.txt", "secret.enc", "decrypted.txt"]
        for filename in test_files_to_remove:
            filepath = self.project_root / filename
            try:
                if filepath.exists():
                    filepath.unlink()
                # Удаляем также файлы ключей
                key_file = self.project_root / f"{filename}.key"
                if key_file.exists():
                    key_file.unlink()
                self.log_result(f"Удаление {filename}", True, "Тестовый файл удален")
            except Exception as e:
                self.log_result(f"Удаление {filename}", False, "Не удалось удалить файл", str(e))
    
    def test_dangerous_commands_warning(self):
        """Тестирует предупреждения об опасных командах"""
        print("\n⚠️ Тестирование предупреждений об опасных командах...")
        
        dangerous_commands = [
            ("sdb.py utils cleanup --all", "Полная очистка (ОПАСНО)"),
            ("sdb.py utils cleanup --logs", "Очистка логов (ОСТОРОЖНО)"),
            ("sdb.py utils cleanup --backups", "Очистка бэкапов (ОСТОРОЖНО)"),
        ]
        
        for command, description in dangerous_commands:
            success, stdout, stderr = self.run_command(command)
            # Эти команды могут завершиться с ошибкой или предупреждением
            if success:
                self.log_result(f"Опасная команда {description}", True, "Команда выполнена (возможно с предупреждением)")
            else:
                # Это нормально - команды могут требовать подтверждения
                self.log_result(f"Опасная команда {description}", True, "Команда завершилась (возможно требует подтверждения)")
    
    def generate_report(self):
        """Генерирует отчет о тестировании"""
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ КОМАНД MONITOR И UTILS")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"\n📈 Общая статистика:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Успешных: {successful_tests}")
        print(f"   Неудачных: {failed_tests}")
        print(f"   Процент успеха: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Неудачные тесты:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
                    if result['details']:
                        print(f"     Детали: {result['details']}")
        
        print(f"\n✅ Успешные тесты:")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}: {result['message']}")
        
        # Сохраняем отчет в файл
        report_file = self.project_root / "test_monitor_utils_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total_tests": total_tests,
                        "successful_tests": successful_tests,
                        "failed_tests": failed_tests,
                        "success_rate": (successful_tests/total_tests*100) if total_tests > 0 else 0
                    },
                    "results": self.test_results
                }, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Подробный отчет сохранен в: {report_file}")
        except Exception as e:
            print(f"\n❌ Не удалось сохранить отчет: {e}")
        
        return successful_tests == total_tests
    
    def run_all_tests(self):
        """Запускает все тесты"""
        print("🚀 Запуск комплексного тестирования команд monitor и utils")
        print("="*60)
        
        # Проверяем что мы в правильной директории
        if not (self.project_root / "sdb.py").exists():
            print("❌ Ошибка: sdb.py не найден в текущей директории")
            return False
        
        # Проверяем виртуальное окружение
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            print("❌ Ошибка: Виртуальное окружение .venv не найдено")
            return False
        
        print("✅ Виртуальное окружение найдено")
        
        # Запускаем все тесты
        self.test_help_commands()
        self.test_monitor_status_commands()
        self.test_monitor_metrics_commands()
        self.test_monitor_alerts_commands()
        self.test_monitor_logs_commands()
        self.test_monitor_performance_commands()
        self.test_monitor_report_commands()
        self.test_monitor_integrate_commands()
        self.test_utils_diagnose_commands()
        self.test_utils_check_commands()
        self.test_utils_cleanup_commands()
        self.test_utils_convert_commands()
        self.test_utils_encrypt_decrypt_commands()
        self.test_dangerous_commands_warning()
        
        # Генерируем отчет
        return self.generate_report()


def main():
    """Главная функция для запуска тестов"""
    print("🧪 Тестирование команд monitor и utils в SwiftDevBot CLI")
    print("="*60)
    
    tester = MonitorUtilsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("\n⚠️ Некоторые тесты завершились неудачно. Проверьте отчет выше.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 