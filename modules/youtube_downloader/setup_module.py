# modules/youtube_downloader/setup_module.py
"""
Функция установки модуля для YouTube Downloader
"""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aiogram import Dispatcher, Bot
    from core.services_provider import BotServicesProvider
    from core.module_loader import ModuleInfo

logger = logging.getLogger(__name__)

async def setup_module(
    dp: "Dispatcher", 
    bot: "Bot",
    services: "BotServicesProvider"
) -> None:
    """
    Настройка и регистрация YouTube Downloader модуля
    
    Args:
        dp: Dispatcher Aiogram для регистрации роутеров
        bot: Экземпляр бота
        services: Провайдер сервисов бота
    """
    MODULE_NAME = "youtube_downloader"
    
    module_info: Optional["ModuleInfo"] = services.modules.get_module_info(MODULE_NAME)
    
    if not module_info or not module_info.manifest:
        logger.error(f"Не удалось получить информацию или манифест для модуля '{MODULE_NAME}'. "
                     "Модуль не будет настроен.")
        return

    display_name = module_info.manifest.display_name
    version = module_info.manifest.version
    logger.info(f"[{MODULE_NAME}] Настройка модуля: {display_name} v{version}...")
    
    # Импортируем роутер для регистрации обработчиков
    from .handlers import youtube_router
    
    # Регистрируем роутер в диспетчере
    dp.include_router(youtube_router)
    logger.info(f"[{MODULE_NAME}] Роутер '{youtube_router.name}' успешно зарегистрирован.")
    
    # Запускаем веб-сервер для больших файлов
    try:
        from .web_server import start_download_server_if_needed
        server = await start_download_server_if_needed()
        if server:
            logger.info(f"[{MODULE_NAME}] Веб-сервер для скачивания файлов запущен на порту 8080")
        else:
            logger.warning(f"[{MODULE_NAME}] Не удалось запустить веб-сервер для скачивания файлов")
    except Exception as e:
        logger.error(f"[{MODULE_NAME}] Ошибка при запуске веб-сервера: {e}")
    
    # Регистрируем точку входа в UI-реестре для отображения в меню модулей
    ui_registry = services.ui_registry
    
    # Создаем callback data для входа в модуль
    from core.ui.callback_data_factories import ModuleMenuEntry
    entry_cb_data = ModuleMenuEntry(module_name=MODULE_NAME).pack()
    
    # Получаем иконку из команды
    icon = "📺"
    if module_info.manifest.commands:
        primary_command = next((cmd for cmd in module_info.manifest.commands if cmd.command == "youtube"), None)
        if primary_command and primary_command.icon:
            icon = primary_command.icon
    
    description = module_info.manifest.description or f"Модуль {display_name}"
    
    ui_registry.register_module_entry(
        module_name=MODULE_NAME,
        display_name=display_name,
        entry_callback_data=entry_cb_data,
        icon=icon,
        description=description,
        order=100,
        required_permission_to_view="youtube_downloader.access_user_features"
    )
    
    logger.info(f"[{MODULE_NAME}] UI-точка входа для модуля '{display_name}' зарегистрирована в UIRegistry.")
    logger.info(f"✅ Модуль '{MODULE_NAME}' ({display_name}) успешно настроен.")
