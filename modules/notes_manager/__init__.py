# modules/notes_manager/__init__.py

from aiogram import Dispatcher, Bot, Router
from loguru import logger

# Импортируем роутер и MODULE_NAME
from .handlers import notes_router, MODULE_NAME 
# Импортируем базовое разрешение для доступа к UI модуля
from .permissions import PERM_ACCESS_USER_FEATURES 

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from core.module_loader import ModuleInfo

async def setup_module(dp: Dispatcher, bot: Bot, services: 'BotServicesProvider'):
    """
    Функция настройки модуля "Менеджер Заметок".
    
    Вызывается автоматически при загрузке модуля системой.
    Здесь регистрируются роутеры и UI-точки входа.
    """
    
    # 1. ОБЯЗАТЕЛЬНО: Регистрация роутера модуля в Dispatcher
    if hasattr(notes_router, 'name'):
        dp.include_router(notes_router)
        logger.info(f"[{MODULE_NAME}] Роутер '{notes_router.name}' успешно зарегистрирован.")
    else:
        logger.error(f"[{MODULE_NAME}] Ошибка: 'notes_router' не является экземпляром aiogram.Router.")

    # 2. РЕКОМЕНДУЕТСЯ: Регистрация UI-точки входа модуля в UIRegistry ядра
    # Это позволит модулю появиться в общем списке "Модули" в UI ядра.
    
    # Получаем информацию о модуле из загрузчика
    module_info: Optional['ModuleInfo'] = services.modules.get_module_info(MODULE_NAME)
    display_name = "📝 Менеджер Заметок"
    if module_info and module_info.manifest:
        display_name = module_info.manifest.display_name
        
    # Импортируем фабрику ModuleMenuEntry из ядра
    from core.ui.callback_data_factories import ModuleMenuEntry 

    entry_cb_data = ModuleMenuEntry(module_name=MODULE_NAME).pack()
    
    icon = "📝" # Можно взять из манифеста, если там будет такое поле для UI Entry
    if module_info.manifest.commands: # Попробуем взять иконку из первой команды
        primary_command = next((cmd for cmd in module_info.manifest.commands if cmd.command == "notes"), None)
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
        # ВАЖНО: Указываем разрешение для отображения кнопки модуля в UI
        required_permission_to_view=PERM_ACCESS_USER_FEATURES # Используем импортированное разрешение
    )
    logger.info(f"[{MODULE_NAME}] UI-точка входа для модуля '{display_name}' зарегистрирована в UIRegistry.")

    logger.success(f"✅ Модуль '{MODULE_NAME}' ({display_name}) успешно настроен.")