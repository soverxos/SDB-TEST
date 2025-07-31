# run_bot.py
# Этот файл является основной точкой входа для запуска Telegram-бота SwiftDevBot.

import asyncio
import sys
from pathlib import Path
import os

# --- Настройка sys.path для корректного импорта 'core' и других пакетов проекта ---
current_script_dir = Path(__file__).resolve().parent
if str(current_script_dir) not in sys.path:
    sys.path.insert(0, str(current_script_dir))

# Импортируем основную функцию запуска бота из ядра
try:
    from core.bot_entrypoint import run_sdb_bot 
except ImportError as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось импортировать компоненты из 'core.bot_entrypoint'.", file=sys.stderr)
    print(f"Ошибка: {e}", file=sys.stderr)
    print("Убедитесь, что структура проекта верна и все зависимости ядра установлены.", file=sys.stderr)
    print(f"Текущий sys.path: {sys.path}", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    exit_code: int = 1 

    try:
        exit_code = asyncio.run(run_sdb_bot())
        
        if exit_code == 0:
            if os.environ.get("SDB_SHOULD_WRITE_PID", "false").lower() != "true":
                print("Бот SwiftDevBot штатно завершил свою работу.")
        else:
            if os.environ.get("SDB_SHOULD_WRITE_PID", "false").lower() != "true":
                print(f"Бот SwiftDevBot завершил работу с кодом ошибки: {exit_code}", file=sys.stderr)

    except KeyboardInterrupt:
        if os.environ.get("SDB_SHOULD_WRITE_PID", "false").lower() != "true":
            print("\n🤖 Бот остановлен пользователем (Ctrl+C). Выход...", file=sys.stderr)
        exit_code = 0 
    except ImportError as e_runtime_import:
        print(f"ОШИБКА ИМПОРТА ВО ВРЕМЯ ВЫПОЛНЕНИЯ: {e_runtime_import}", file=sys.stderr)
        print("Возможно, отсутствуют зависимости для одного из активных модулей.", file=sys.stderr)
        exit_code = 3
    except Exception as e_global:
        print(f"КРИТИЧЕСКАЯ НЕОБРАБОТАННАЯ ОШИБКА НА ВЕРХНЕМ УРОВНЕ: {type(e_global).__name__}: {e_global}", file=sys.stderr)
        print("Смотрите логи для получения полного трейсбека ошибки.", file=sys.stderr)
        exit_code = 1
    finally:
        pass

    sys.exit(exit_code)