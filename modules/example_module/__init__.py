# modules/example_module/__init__.py

from aiogram import Dispatcher, Bot, Router
from loguru import logger

# Импортируем роутер и MODULE_NAME
from .handlers_example import example_module_router, MODULE_NAME 
# Импортируем базовое разрешение для доступа к UI модуля
from .permissions import PERM_ACCESS_USER_FEATURES 

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from core.module_loader import ModuleInfo

async def setup_module(dp: Dispatcher, bot: Bot, services: 'BotServicesProvider'):
    module_info: Optional[ModuleInfo] = services.modules.get_module_info(MODULE_NAME)
    
    if not module_info or not module_info.manifest:
        logger.error(f"Не удалось получить информацию или манифест для модуля '{MODULE_NAME}'. "
                     "Модуль не будет настроен.")
        return

    display_name = module_info.manifest.display_name
    version = module_info.manifest.version
    logger.info(f"[{MODULE_NAME}] Настройка модуля: {display_name} v{version}...")

    if isinstance(example_module_router, Router):
        dp.include_router(example_module_router)
        logger.info(f"[{MODULE_NAME}] Роутер '{example_module_router.name}' успешно зарегистрирован.")
    else:
        logger.error(f"[{MODULE_NAME}] Ошибка: 'example_module_router' не является экземпляром aiogram.Router.")

    from core.ui.callback_data_factories import ModuleMenuEntry 

    entry_cb_data = ModuleMenuEntry(module_name=MODULE_NAME).pack()
    
    icon = "🌟" # Можно взять из манифеста, если там будет такое поле для UI Entry
    if module_info.manifest.commands: # Попробуем взять иконку из первой команды
        primary_command = next((cmd for cmd in module_info.manifest.commands if cmd.command == "example"), None)
        if primary_command and primary_command.icon:
            icon = primary_command.icon

    description = module_info.manifest.description or f"Модуль {display_name}"

    services.ui_registry.register_module_entry(
        module_name=MODULE_NAME, 
        display_name=display_name,
        entry_callback_data=entry_cb_data, 
        icon=icon,
        description=description,
        order=100,
        required_permission_to_view=PERM_ACCESS_USER_FEATURES # Используем импортированное разрешение
    )
    logger.info(f"[{MODULE_NAME}] UI-точка входа для модуля '{display_name}' зарегистрирована в UIRegistry.")

    logger.success(f"✅ Модуль '{MODULE_NAME}' ({display_name}) успешно настроен.")