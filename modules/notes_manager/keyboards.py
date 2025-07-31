# modules/notes_manager/keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import TYPE_CHECKING, List

from .callback_data_factories import NotesAction
from .permissions import PERM_CREATE_NOTES, PERM_EDIT_NOTES, PERM_DELETE_NOTES
from core.ui.callback_data_factories import CoreMenuNavigate

if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession
    from .models import UserNote

async def get_notes_main_menu_keyboard(
    services_provider: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession'
) -> InlineKeyboardMarkup:
    """Клавиатура главного меню модуля заметок"""
    builder = InlineKeyboardBuilder()
    
    # Просмотр заметок (всегда доступно если есть доступ к модулю)
    builder.button(
        text="📋 Мои заметки",
        callback_data=NotesAction(action="list").pack()
    )
    
    # Создать заметку
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_CREATE_NOTES):
        builder.button(
            text="➕ Создать заметку",
            callback_data=NotesAction(action="create").pack()
        )
    
    # Кнопка "Назад к модулям"
    builder.button(
        text="⬅️ Назад к модулям",
        callback_data=CoreMenuNavigate(target_menu="modules_list").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

async def get_notes_list_keyboard(notes: List['UserNote']) -> InlineKeyboardMarkup:
    """Клавиатура со списком заметок"""
    builder = InlineKeyboardBuilder()
    
    for note in notes:
        # Ограничиваем длину названия для кнопки
        title = note.title if len(note.title) <= 30 else note.title[:27] + "..."
        builder.button(
            text=f"📝 {title}",
            callback_data=NotesAction(action="view", note_id=note.id).pack()
        )
    
    # Кнопка "Назад в главное меню"
    builder.button(
        text="⬅️ Назад",
        callback_data=NotesAction(action="back_to_main").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

async def get_note_actions_keyboard(
    note_id: int, 
    services_provider: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession'
) -> InlineKeyboardMarkup:
    """Клавиатура действий с конкретной заметкой"""
    builder = InlineKeyboardBuilder()
    
    # Редактировать (если есть права)
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_EDIT_NOTES):
        builder.button(
            text="✏️ Редактировать",
            callback_data=NotesAction(action="edit", note_id=note_id).pack()
        )
    
    # Удалить (если есть права)
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_DELETE_NOTES):
        builder.button(
            text="🗑️ Удалить",
            callback_data=NotesAction(action="delete", note_id=note_id).pack()
        )
    
    # Назад к списку
    builder.button(
        text="⬅️ К списку заметок",
        callback_data=NotesAction(action="back_to_list").pack()
    )
    
    builder.adjust(2, 1)  # 2 кнопки в первом ряду, 1 во втором
    return builder.as_markup()
