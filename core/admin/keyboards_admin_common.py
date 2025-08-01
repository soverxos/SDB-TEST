# core/admin/keyboards_admin_common.py
from aiogram import types 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder 
from core.ui.callback_data_factories import CoreMenuNavigate, AdminMainMenuNavigate

from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession
    from core.rbac.service import (
        PERMISSION_CORE_USERS_VIEW_LIST,
        PERMISSION_CORE_MODULES_VIEW_LIST,
        PERMISSION_CORE_SYSTEM_VIEW_INFO_BASIC,
        PERMISSION_CORE_SYSTEM_VIEW_INFO_FULL,
        PERMISSION_CORE_ROLES_VIEW
    )

ADMIN_COMMON_TEXTS = {
    "back_to_main_menu_sdb": "🏠 Главное меню SDB",
    "back_to_admin_menu_main": "⬅️ Админ-панель (Главная)",
    "pagination_prev": "⬅️ Пред.",
    "pagination_next": "След. ➡️",
    "confirm_yes": "✅ Да",
    "confirm_no": "❌ Нет",
    "close_message": "❌ Закрыть это сообщение",
    "error_general": "Произошла ошибка. Попробуйте позже.",
    "access_denied": "У вас нет прав для этого действия.",
    "not_found_generic": "Запрошенный элемент не найден.",
    
    # Тексты для кнопок главного меню админки
    "manage_users": "👤 Управление пользователями",
    "manage_roles": "🛡️ Управление ролями",
    "manage_modules": "🧩 Управление модулями",
    "system_info": "⚙️ Информация о системе",

    # Тексты для категорий и групп разрешений (добавлены)
    "perm_category_core": "Разрешения Ядра",
    "perm_category_modules": "Разрешения Модулей",
    "perm_core_group_users": "Пользователи (Ядро)",
    "perm_core_group_roles": "Роли (Ядро)",
    "perm_core_group_modules_core": "Управление модулями (Ядро)", # Изменено для ясности
    "perm_core_group_system": "Система (Ядро)",
    "perm_core_group_settings_core": "Настройки Ядра",
    "perm_core_group_other": "Прочие (Ядро)",
    "back_to_perm_categories": "⬅️ К категориям разрешений",
    "back_to_core_perm_groups": "⬅️ К группам Ядра",
    "back_to_module_list_for_perms": "⬅️ К списку модулей (для прав)",
    "no_modules_with_perms": "Нет модулей с объявлениями прав",
    "no_permissions_in_group": "В этой группе нет разрешений",

    # Тексты для FSM (добавлены)
    "fsm_enter_role_name": "Введите имя новой роли:",
    "fsm_role_name_empty": "Имя роли не может быть пустым.",
    "fsm_role_name_taken": "Роль с именем \"{role_name}\" уже существует.",
    "fsm_enter_role_description": "Введите описание для роли {role_name}:",
    "fsm_command_skip_description": "/skip_description - Пропустить",
    "fsm_command_cancel_role_creation": "/cancel_role_creation - Отменить создание",
    "fsm_role_created_successfully": "Роль \"{role_name}\" успешно создана!",
    "fsm_role_creation_cancelled": "Создание роли отменено.",
    
    "fsm_edit_role_title": "Редактирование роли: {role_name}",
    "fsm_edit_role_name_not_allowed": "Имя стандартной роли {role_name} изменять нельзя.",
    "fsm_enter_new_role_description": "Введите новое описание для роли {role_name} (текущее: {current_description}):",
    "fsm_enter_new_role_name": "Введите новое имя для роли (текущее: {current_name}):",
    "fsm_command_skip_name": "/skip_name - Оставить как есть",
    "fsm_command_cancel_role_edit": "/cancel_role_edit - Отменить редактирование",
    "fsm_role_updated_successfully": "Роль \"{role_name}\" успешно обновлена!",
    "fsm_role_update_cancelled": "Редактирование роли отменено.",

    "delete_role_confirm_text": "Вы уверены, что хотите удалить роль {role_name}?\n{warning_if_users}\nЭто действие необратимо!",
    "role_is_standard_cant_delete": "Стандартную роль \"{role_name}\" удалять нельзя.",
    "role_delete_failed": "Не удалось удалить роль \"{role_name}\".",
    "role_deleted_successfully": "Роль \"{role_name}\" успешно удалена.",
}

def get_back_to_admin_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=ADMIN_COMMON_TEXTS["back_to_admin_menu_main"],
        callback_data=AdminMainMenuNavigate(target_section="main_admin").pack()
    )

def get_back_to_sdb_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=ADMIN_COMMON_TEXTS["back_to_main_menu_sdb"],
        callback_data=CoreMenuNavigate(target_menu="main").pack()
    )

async def get_admin_main_menu_keyboard( 
    services: 'BotServicesProvider',
    user_tg_id: int,
    session: 'AsyncSession' 
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = ADMIN_COMMON_TEXTS 

    rbac = services.rbac
    user_is_owner_from_config = user_tg_id in services.config.core.super_admins

    from core.rbac.service import (
        PERMISSION_CORE_USERS_VIEW_LIST,
        PERMISSION_CORE_MODULES_VIEW_LIST,
        PERMISSION_CORE_SYSTEM_VIEW_INFO_BASIC,
        PERMISSION_CORE_SYSTEM_VIEW_INFO_FULL,
        PERMISSION_CORE_ROLES_VIEW
    )
    
    if user_is_owner_from_config or \
       await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_SYSTEM_VIEW_INFO_BASIC) or \
       await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_SYSTEM_VIEW_INFO_FULL):
        builder.button(
            text=texts["system_info"],
            callback_data=AdminMainMenuNavigate(target_section="sys_info").pack() 
        )

    if user_is_owner_from_config or \
       await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_USERS_VIEW_LIST):
        builder.button(
            text=texts["manage_users"],
            callback_data=AdminMainMenuNavigate(target_section="users").pack() 
        )
    
    if user_is_owner_from_config or \
       await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_ROLES_VIEW): 
        builder.button(
            text=texts["manage_roles"],
            callback_data=AdminMainMenuNavigate(target_section="roles").pack() 
        )

    if user_is_owner_from_config or \
       await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_MODULES_VIEW_LIST):
        builder.button(
            text=texts["manage_modules"],
            callback_data=AdminMainMenuNavigate(target_section="modules").pack() 
        )
    
    # Кнопка для просмотра логов, если нужно
    # from core.rbac.service import PERMISSION_CORE_SYSTEM_VIEW_LOGS_BASIC
    # if user_is_owner_from_config or \
    #    await rbac.user_has_permission(session, user_tg_id, PERMISSION_CORE_SYSTEM_VIEW_LOGS_BASIC):
    #     builder.button(
    #         text="Просмотр логов", # Добавить в ADMIN_COMMON_TEXTS
    #         callback_data=AdminMainMenuNavigate(target_section="logs_view").pack()
    #     )
    
    if builder.export(): 
        builder.adjust(1)

    builder.row(get_back_to_sdb_main_menu_button()) 
    return builder.as_markup()