# modules/example_module/keyboards_example.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импортируем фабрику для навигации ядра, чтобы сделать кнопку "Назад"
from core.ui.callback_data_factories import CoreMenuNavigate, ModuleMenuEntry # <--- ДОБАВЛЕН ИМПОРТ ModuleMenuEntry
# Импортируем свою фабрику для этого модуля
from .callback_data_factories_example import ExampleModuleAction 
# Импортируем имена разрешений из нового файла
from .permissions import (
    PERM_VIEW_MODULE_SETTINGS,
    PERM_VIEW_SECRET_INFO,
    PERM_PERFORM_BASIC_ACTION,
    PERM_PERFORM_ADVANCED_ACTION,
    PERM_MANAGE_OWN_NOTES
)
from .models import UserNote # Для отображения заметок

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_example_module_main_menu_keyboard(
    services: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession' 
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Показать настройки модуля"
    if await services.rbac.user_has_permission(session, user_id, PERM_VIEW_MODULE_SETTINGS):
        builder.button(
            text="⚙️ Настройки модуля (глоб.)",
            callback_data=ExampleModuleAction(action="show_module_settings").pack()
        )
    
    # Кнопка "Показать секретную информацию"
    if await services.rbac.user_has_permission(session, user_id, PERM_VIEW_SECRET_INFO):
        builder.button(
            text="🤫 Секретная информация",
            callback_data=ExampleModuleAction(action="show_secret_info").pack()
        )

    # Кнопка "Базовое действие"
    if await services.rbac.user_has_permission(session, user_id, PERM_PERFORM_BASIC_ACTION):
        builder.button(
            text="▶️ Базовое действие",
            callback_data=ExampleModuleAction(action="do_basic_action").pack()
        )

    # Кнопка "Продвинутое действие"
    if await services.rbac.user_has_permission(session, user_id, PERM_PERFORM_ADVANCED_ACTION):
        builder.button(
            text="🚀 Продвинутое действие",
            callback_data=ExampleModuleAction(action="do_advanced_action").pack()
        )
    
    # Кнопка "Мои заметки"
    if await services.rbac.user_has_permission(session, user_id, PERM_MANAGE_OWN_NOTES):
        builder.button(
            text="📝 Мои заметки",
            callback_data=ExampleModuleAction(action="my_notes_list").pack()
        )

    if not builder.export(): 
        builder.button(
            text="🤷‍♂️ Для вас здесь пока нет доступных действий",
            callback_data="example_module:no_actions" 
        )

    builder.button(
        text="⬅️ Назад к списку модулей",
        callback_data=CoreMenuNavigate(target_menu="modules_list", page=1).pack() 
    )
    
    builder.adjust(1) 
    return builder.as_markup()

async def get_my_notes_keyboard(
    notes: List[UserNote], 
    services: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession'
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if notes:
        for note in notes:
            status_icon = "✅" if note.is_done else "📝"
            note_text_short = note.note_text[:30] + "..." if len(note.note_text) > 30 else note.note_text
            builder.button(
                text=f"{status_icon} {note_text_short}",
                callback_data=ExampleModuleAction(action="view_note_details", item_id=note.id).pack()
            )
        builder.adjust(1)
    else:
        builder.button(text="У вас пока нет заметок.", callback_data="example_module:no_notes_dummy")

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить заметку",
            callback_data=ExampleModuleAction(action="add_note_start").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ В меню модуля",
            # Здесь используется ModuleMenuEntry, который мы теперь правильно импортируем
            callback_data=ModuleMenuEntry(module_name="example_module").pack() 
        )
    )
    return builder.as_markup()

async def get_note_details_keyboard(
    note: UserNote,
    services: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession'
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    toggle_done_text = "📝 Снять отметку" if note.is_done else "✅ Отметить как сделано"
    builder.button(
        text=toggle_done_text,
        callback_data=ExampleModuleAction(action="toggle_note_done", item_id=note.id).pack()
    )
    builder.button(
        text="🗑️ Удалить заметку",
        callback_data=ExampleModuleAction(action="delete_note_confirm", item_id=note.id).pack()
    )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ К моим заметкам",
            callback_data=ExampleModuleAction(action="my_notes_list").pack()
        )
    )
    return builder.as_markup()