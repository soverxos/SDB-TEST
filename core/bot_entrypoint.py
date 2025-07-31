# core/bot_entrypoint.py

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING 
from datetime import datetime, timezone

from loguru import logger as global_logger

if not (hasattr(global_logger, '_core') and hasattr(global_logger._core, 'handlers') and global_logger._core.handlers):
    try:
        global_logger.remove() 
        global_logger.add(sys.stderr, level="DEBUG") 
        print("!!! [SDB bot_entrypoint WARNING] Loguru handlers был пуст или недоступен, добавлен stderr по умолчанию. !!!", file=sys.stderr)
    except Exception as e_loguru_init_fallback_entry:
        print(f"!!! [SDB bot_entrypoint CRITICAL] Loguru handlers пуст и не удалось добавить stderr: {e_loguru_init_fallback_entry} !!!", file=sys.stderr)


from aiogram import Bot, Dispatcher, __version__ as aiogram_version
from aiogram.types import BotCommand 
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramRetryAfter

# Ленивый импорт RedisStorage - только когда нужен
try:
    from aiogram.fsm.storage.redis import RedisStorage
    REDIS_STORAGE_AVAILABLE = True
except ImportError:
    RedisStorage = None  # type: ignore
    REDIS_STORAGE_AVAILABLE = False

from core.app_settings import settings 
from core.services_provider import BotServicesProvider
from core.module_loader import ModuleLoader 
from core.ui.handlers_core_ui import core_ui_router 
from core.i18n.middleware import I18nMiddleware 
from core.i18n.translator import Translator 
from core.users.middleware import UserStatusMiddleware 
from core.logging_manager import LoggingManager 
from core.admin_auto_setup import AdminAutoSetup 

if TYPE_CHECKING:
    pass

PID_FILENAME = "sdb_bot.pid" 
CORE_COMMANDS_DESCRIPTIONS = { 
    "start": "🚀 Запустить бота / Показать главное меню",
    "help": "❓ Помощь и список команд бота",
}

try:
    from core.admin import admin_router 
    ADMIN_ROUTER_AVAILABLE = True
    global_logger.info("Главный админ-роутер (core.admin.admin_router) успешно импортирован.")
except ImportError:
    admin_router = None 
    ADMIN_ROUTER_AVAILABLE = False
    global_logger.info("Главный админ-роутер не найден или не может быть импортирован. Админ-панель будет неактивна.")


async def _setup_bot_commands(bot: Bot, services: 'BotServicesProvider', admin_router_available: bool):
    module_name_for_log = "CoreBotSetup"
    global_logger.debug(f"[{module_name_for_log}] Начало установки команд бота в Telegram...")
    
    final_commands_dict: Dict[str, str] = {}

    for cmd_name, cmd_desc in CORE_COMMANDS_DESCRIPTIONS.items():
        if cmd_name not in final_commands_dict:
            final_commands_dict[cmd_name] = cmd_desc
    global_logger.trace(f"[{module_name_for_log}] Добавлены базовые команды ядра: {list(CORE_COMMANDS_DESCRIPTIONS.keys())}")

    all_loaded_plugin_modules_info = services.modules.get_loaded_modules_info(include_system=False, include_plugins=True)
    for module_info in all_loaded_plugin_modules_info:
        if module_info.manifest and module_info.manifest.commands:
            global_logger.trace(f"[{module_name_for_log}] Проверка команд для плагина: {module_info.name}")
            for cmd_manifest in module_info.manifest.commands:
                if not cmd_manifest.admin_only: 
                    if cmd_manifest.command not in final_commands_dict:
                        final_commands_dict[cmd_manifest.command] = cmd_manifest.description
    
    if admin_router_available: 
        admin_panel_commands = {"admin": "🛠 Открыть панель администратора"} 
        
        for cmd_name, cmd_desc in admin_panel_commands.items():
            if cmd_name not in final_commands_dict:
                 final_commands_dict[cmd_name] = cmd_desc
        global_logger.trace(f"[{module_name_for_log}] Добавлены команды админ-панели: {list(admin_panel_commands.keys())}")

    final_bot_commands = [
        BotCommand(command=name, description=desc) for name, desc in final_commands_dict.items()
    ]
            
    if final_bot_commands:
        try:
            await bot.set_my_commands(final_bot_commands)
            global_logger.success(f"[{module_name_for_log}] Установлено {len(final_bot_commands)} команд бота в Telegram: "
                                  f"{[cmd.command for cmd in final_bot_commands]}")
        except Exception as e:
            global_logger.error(f"[{module_name_for_log}] Ошибка при установке команд бота: {e}", exc_info=True)
    else:
        global_logger.warning(f"[{module_name_for_log}] Нет команд для установки в Telegram.")


async def run_sdb_bot() -> int:
    if not settings.telegram.token:
        global_logger.critical("Невозможно запустить бота: токен не найден.")
        global_logger.critical("Пожалуйста, создайте .env файл с BOT_TOKEN=... или укажите его в config.yaml.")
        return 1
        
    current_process_start_time = datetime.now(timezone.utc)
    sdb_version = settings.core.sdb_version
    
    logging_manager = LoggingManager(app_settings=settings)
    await logging_manager.initialize_logging() 
    
    global_logger.info(f"Система логирования инициализирована. "
                       f"Уровень консольного лога: {settings.core.log_level.upper()} (может быть переопределен SDB_CLI_DEBUG_MODE_FOR_LOGGING). "
                       f"Уровень файлового лога всегда DEBUG (или TRACE, если так задано в LoggingManager).")

    global_logger.info(f"🚀 Запуск SwiftDevBot (SDB) v{sdb_version} в {current_process_start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}...")
    global_logger.info(f"🐍 Используется Python v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    global_logger.info(f"🤖 Используется Aiogram v{aiogram_version}")
    global_logger.debug(f"Каталог запуска (CWD): {Path.cwd()}")
    global_logger.debug(f"Корень проекта: {settings.core.project_data_path.parent}")
    global_logger.debug(f"Директория данных проекта: {settings.core.project_data_path}")

    pid_file_actual_path = settings.core.project_data_path / PID_FILENAME
    bot: Optional[Bot] = None 
    services: Optional[BotServicesProvider] = None
    exit_code_internal = 1 

    if pid_file_actual_path.exists():
        try:
            old_pid = int(pid_file_actual_path.read_text().strip())
            if sys.platform != "win32": 
                os.kill(old_pid, 0) 
                global_logger.error(f"Обнаружен активный PID-файл ({pid_file_actual_path}) для работающего процесса PID {old_pid}. "
                                   f"Новый запуск SDB (PID: {os.getpid()}) не может быть выполнен. Остановите предыдущий экземпляр.")
                if logging_manager: await logging_manager.shutdown_logging() 
                return 1 
        except (OSError, ValueError): 
            global_logger.info(f"Удаление устаревшего или некорректного PID-файла: {pid_file_actual_path}")
            pid_file_actual_path.unlink(missing_ok=True)
        except Exception as e_pid_precheck:
             global_logger.warning(f"Ошибка при предварительной проверке PID-файла: {e_pid_precheck}")

    should_write_pid = os.environ.get("SDB_SHOULD_WRITE_PID", "false").lower() == "true"
    if should_write_pid:
        try:
            pid_file_actual_path.parent.mkdir(parents=True, exist_ok=True)
            with open(pid_file_actual_path, "w") as f:
                f.write(str(os.getpid()))
            global_logger.info(f"PID {os.getpid()} записан в {pid_file_actual_path}")
        except Exception as e_pid_write:
            global_logger.error(f"Не удалось создать/записать PID-файл {pid_file_actual_path}: {e_pid_write}. "
                               "Бот продолжит работу, но управление через PID-файл может быть нарушено.")
    try:
        services = BotServicesProvider(settings=settings)
        await services.setup_services() 
        global_logger.success("✅ BotServicesProvider и все его базовые сервисы успешно инициализированы.")
        
        bot = Bot(
            token=services.config.telegram.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        me = await bot.get_me()
        global_logger.info(f"🤖 Экземпляр Telegram Bot успешно создан: @{me.username} (ID: {me.id})")

        storage: Union[MemoryStorage, Any]
        if (services.config.cache.type == "redis" and 
            services.cache.is_available() and 
            REDIS_STORAGE_AVAILABLE):
            redis_client_instance = await services.cache.get_redis_client_instance()
            if redis_client_instance:
                storage = RedisStorage(redis=redis_client_instance)
                global_logger.info("FSM Storage: используется RedisStorage.")
            else:
                global_logger.warning("Redis сконфигурирован для кэша, но клиент Redis недоступен для FSM. Используется MemoryStorage.")
                storage = MemoryStorage()
        else:
            storage = MemoryStorage()
            global_logger.info("FSM Storage: используется MemoryStorage.")

        dp = Dispatcher(storage=storage, services_provider=services)
        global_logger.info("🚦 Dispatcher и FSM Storage инициализированы.")

        translator = Translator(
            locales_dir=settings.core.i18n.locales_dir,
            domain=settings.core.i18n.domain,
            default_locale=settings.core.i18n.default_locale,
            available_locales=settings.core.i18n.available_locales
        )
        dp.update.outer_middleware(I18nMiddleware(translator))
        global_logger.info("I18nMiddleware зарегистрирован для всех Update.")
        
        dp.update.outer_middleware(UserStatusMiddleware()) 
        global_logger.info("UserStatusMiddleware зарегистрирован для всех Update.")

        dp.include_router(core_ui_router) 
        global_logger.info(f"Базовый UI-роутер ядра '{core_ui_router.name}' зарегистрирован.")

        if ADMIN_ROUTER_AVAILABLE and admin_router:
            dp.include_router(admin_router)
            global_logger.info(f"✅ Главный админ-роутер '{admin_router.name}' успешно зарегистрирован")
        
        module_loader: ModuleLoader = services.modules 
        await module_loader.initialize_and_setup_modules(dp=dp, bot=bot)
        
        if settings.core.setup_bot_commands_on_startup:
            await _setup_bot_commands(bot, services, admin_router_available=ADMIN_ROUTER_AVAILABLE)
        else:
            global_logger.info("Автоматическая установка команд бота отключена в настройках.")

        @dp.startup()
        async def on_bot_startup():
            nonlocal sdb_version 
            bot_info = await bot.get_me() 
            services.logger.info(f"⚡ Событие startup для Dispatcher (бот: @{bot_info.username})...")
            
            admin_setup = AdminAutoSetup(services)
            await admin_setup.initialize()
            
            # <-- ИЗМЕНЕНИЕ: запускаем фоновую задачу очистки кеша callback_data
            from core.ui.callback_data_manager import callback_data_manager
            asyncio.create_task(callback_data_manager.cleanup_expired_hashes_task())
            
            await bot.delete_webhook(drop_pending_updates=True)
            services.logger.info("Webhook удален, ожидающие обновления сброшены.")
            
            services.logger.success(f"✅ Бот SDB @{bot_info.username} успешно запущен и готов к работе!")
            if services.config.core.super_admins:
                for admin_id in services.config.core.super_admins:
                    try:
                        await bot.send_message(admin_id, f"🚀 Бот SDB @{bot_info.username} (v{sdb_version}) успешно запущен!")
                    except Exception as e_send:
                        services.logger.warning(f"Не удалось отправить уведомление о запуске админу {admin_id}: {e_send}")

        @dp.shutdown()
        async def on_bot_shutdown():
            nonlocal logging_manager 
            bot_info = await bot.get_me()
            services.logger.info(f"⏳ Событие shutdown для Dispatcher. Начало остановки бота @{bot_info.username}...")
            
            if logging_manager: 
                await logging_manager.shutdown_logging()

            if pid_file_actual_path.is_file():
                try:
                    if int(pid_file_actual_path.read_text().strip()) == os.getpid():
                        pid_file_actual_path.unlink()
                except: pass

            global_logger.info(f"🏁 Процедура остановки бота @{bot_info.username} почти завершена.")

        bot_username_for_log = (await bot.get_me()).username
        global_logger.info(f"📡 Запуск Telegram Bot Polling для @{bot_username_for_log}...")
        
        await dp.start_polling(bot) 
        exit_code_internal = 0 
        
    except (KeyboardInterrupt, SystemExit) as e_exit:
        global_logger.info(f"🚨 Получен сигнал остановки ({type(e_exit).__name__}). Поллинг прерывается...")
        exit_code_internal = 0 
    except Exception as e_main_run:
        global_logger.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в основной функции run_sdb_bot: {e_main_run}", exc_info=True)
        exit_code_internal = 1
    finally:
        global_logger.info("Блок finally в run_sdb_bot.")
        
        if services:
            await services.close_services()
        
        if logging_manager and logging_manager._is_initialized: 
            await logging_manager.shutdown_logging() 
        
        if pid_file_actual_path.is_file():
            try:
                if int(pid_file_actual_path.read_text().strip()) == os.getpid():
                    pid_file_actual_path.unlink()
            except: pass
            
        global_logger.info(f"🏁 Работа бота завершена. Внутренний код выхода: {exit_code_internal}")
        return exit_code_internal