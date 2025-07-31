# modules/notes_manager/handlers.py
from aiogram import Router, types, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold, hcode, hitalic
from aiogram.exceptions import TelegramBadRequest 
from loguru import logger
from sqlalchemy import select, delete as sql_delete, func 
from datetime import datetime

from .keyboards import (
    get_notes_main_menu_keyboard,
    get_notes_list_keyboard,
    get_note_actions_keyboard
)
from .callback_data_factories import NotesAction
from core.ui.callback_data_factories import ModuleMenuEntry, CoreMenuNavigate 
from .permissions import ( 
    MODULE_NAME, 
    PERM_ACCESS_USER_FEATURES,
    PERM_VIEW_NOTES,
    PERM_CREATE_NOTES,
    PERM_EDIT_NOTES,
    PERM_DELETE_NOTES,
)
from .models import UserNote 

from typing import TYPE_CHECKING, Any, List, Optional
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession

notes_router = Router(name="sdb_notes_manager_handlers")

class FSMCreateNote(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()

class FSMEditNote(StatesGroup):
    edit_title = State()
    edit_content = State()

async def check_permission(
    user_id: int, 
    permission_name: str, 
    services_provider: 'BotServicesProvider', 
    session: 'AsyncSession'
) -> bool:
    """Проверка разрешения пользователя"""
    has_perm = await services_provider.rbac.user_has_permission(session, user_id, permission_name)
    if not has_perm:
        logger.warning(f"[{MODULE_NAME}] Пользователь {user_id} попытался выполнить действие, требующее права '{permission_name}', но не имеет его.")
    return has_perm

# === ОСНОВНЫЕ ОБРАБОТЧИКИ ===

@notes_router.message(Command("notes"))
async def cmd_notes_entry(message: types.Message, services_provider: 'BotServicesProvider'):
    """Команда входа в модуль заметок"""
    user_id = message.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вызвал команду /notes.")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await message.answer("❌ У вас нет доступа к модулю заметок.")
            return
    
    text = f"📝 {hbold('Добро пожаловать в Менеджер Заметок!')}\n\nЗдесь вы можете создавать, просматривать и управлять своими заметками."
    
    async with services_provider.db.get_session() as session:
        keyboard = await get_notes_main_menu_keyboard(services_provider, user_id, session)
    
    await message.answer(text, reply_markup=keyboard)

@notes_router.callback_query(ModuleMenuEntry.filter(F.module_name == MODULE_NAME))
async def cq_notes_main_menu(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    """Обработчик входа в модуль заметок через UI"""
    user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вошел в модуль заметок через UI.")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await query.answer("❌ У вас нет доступа к модулю заметок.", show_alert=True)
            return
        
        text = f"📝 {hbold('Менеджер Заметок')}\n\nЧто хотите сделать?"
        keyboard = await get_notes_main_menu_keyboard(services_provider, user_id, session)
        
        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text в главном меню: {e}")
            await query.answer()

# === ДЕЙСТВИЯ С ЗАМЕТКАМИ ===

@notes_router.callback_query(NotesAction.filter(F.action == "list"))
async def cq_notes_list(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    """Список заметок пользователя"""
    user_id = query.from_user.id
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_VIEW_NOTES, services_provider, session):
            await query.answer("❌ У вас нет прав на просмотр заметок.", show_alert=True)
            return
        
        # Получаем все заметки пользователя
        stmt = select(UserNote).where(UserNote.user_telegram_id == user_id).order_by(UserNote.created_at.desc())
        result = await session.execute(stmt)
        notes = result.scalars().all()
        
        if not notes:
            text = f"📝 {hbold('Ваши заметки')}\n\n❌ У вас пока нет заметок."
            keyboard = await get_notes_main_menu_keyboard(services_provider, user_id, session)
        else:
            text = f"📝 {hbold('Ваши заметки')} ({len(notes)})\n\nВыберите заметку для просмотра:"
            keyboard = await get_notes_list_keyboard(notes)
        
        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text в списке заметок: {e}")
        await query.answer()

@notes_router.callback_query(NotesAction.filter(F.action == "create"))
async def cq_create_note_start(query: types.CallbackQuery, state: FSMContext, services_provider: 'BotServicesProvider'):
    """Начало создания заметки"""
    user_id = query.from_user.id
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_CREATE_NOTES, services_provider, session):
            await query.answer("❌ У вас нет прав на создание заметок.", show_alert=True)
            return
    
    await state.set_state(FSMCreateNote.waiting_for_title)
    text = f"✍️ {hbold('Создание заметки')}\n\n📝 Введите заголовок для новой заметки:"
    
    if query.message:
        try:
            await query.message.edit_text(text)
        except TelegramBadRequest as e:
            logger.warning(f"[{MODULE_NAME}] Ошибка edit_text при создании заметки: {e}")
            await query.message.answer(text)
    await query.answer()

@notes_router.message(StateFilter(FSMCreateNote.waiting_for_title))
async def process_note_title(message: types.Message, state: FSMContext):
    """Обработка заголовка заметки"""
    title = message.text.strip()
    
    if len(title) > 100:
        await message.answer("❌ Заголовок слишком длинный. Максимум 100 символов.")
        return
    
    if len(title) < 1:
        await message.answer("❌ Заголовок не может быть пустым.")
        return
    
    await state.update_data(title=title)
    await state.set_state(FSMCreateNote.waiting_for_content)
    
    text = f"✅ Заголовок: {hbold(title)}\n\n📄 Теперь введите содержание заметки:"
    await message.answer(text)

@notes_router.message(StateFilter(FSMCreateNote.waiting_for_content))
async def process_note_content(message: types.Message, state: FSMContext, services_provider: 'BotServicesProvider'):
    """Обработка содержания заметки и сохранение"""
    content = message.text.strip()
    user_id = message.from_user.id
    
    if len(content) < 1:
        await message.answer("❌ Содержание заметки не может быть пустым.")
        return
    
    if len(content) > 4000:
        await message.answer("❌ Содержание слишком длинное. Максимум 4000 символов.")
        return
    
    # Получаем заголовок из состояния
    data = await state.get_data()
    title = data.get("title", "Без названия")
    
    # Сохраняем заметку в БД
    async with services_provider.db.get_session() as session:
        new_note = UserNote(
            user_telegram_id=user_id,
            title=title,
            content=content
        )
        session.add(new_note)
        await session.commit()
        await session.refresh(new_note)
        
        logger.info(f"[{MODULE_NAME}] Пользователь {user_id} создал заметку ID {new_note.id}: '{title}'")
    
    await state.clear()
    
    text = f"✅ {hbold('Заметка создана!')}\n\n📝 {hbold(title)}\n📄 {content[:200]}{'...' if len(content) > 200 else ''}"
    
    async with services_provider.db.get_session() as session:
        keyboard = await get_notes_main_menu_keyboard(services_provider, user_id, session)
    
    await message.answer(text, reply_markup=keyboard)

@notes_router.callback_query(NotesAction.filter(F.action == "view"))
async def cq_view_note(query: types.CallbackQuery, callback_data: NotesAction, services_provider: 'BotServicesProvider'):
    """Просмотр конкретной заметки"""
    user_id = query.from_user.id
    note_id = callback_data.note_id
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_VIEW_NOTES, services_provider, session):
            await query.answer("❌ У вас нет прав на просмотр заметок.", show_alert=True)
            return
        
        # Получаем заметку
        stmt = select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_telegram_id == user_id
        )
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        
        if not note:
            await query.answer("❌ Заметка не найдена или у вас нет к ней доступа.", show_alert=True)
            return
        
        # Формируем текст
        created_date = note.created_at.strftime("%d.%m.%Y %H:%M")
        text = f"📝 {hbold(note.title)}\n\n📄 {note.content}\n\n🕒 Создана: {created_date}"
        
        keyboard = await get_note_actions_keyboard(note_id, services_provider, user_id, session)
        
        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text при просмотре заметки: {e}")
        await query.answer()

@notes_router.callback_query(NotesAction.filter(F.action == "edit"))
async def cq_edit_note(query: types.CallbackQuery, callback_data: NotesAction, state: FSMContext, services_provider: 'BotServicesProvider'):
    """Начало редактирования заметки"""
    user_id = query.from_user.id
    note_id = callback_data.note_id
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_EDIT_NOTES, services_provider, session):
            await query.answer("❌ У вас нет прав на редактирование заметок.", show_alert=True)
            return
        
        # Получаем заметку
        stmt = select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_telegram_id == user_id
        )
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        
        if not note:
            await query.answer("❌ Заметка не найдена или у вас нет к ней доступа.", show_alert=True)
            return
        
        # Сохраняем данные заметки в состоянии
        await state.set_state(FSMEditNote.edit_title)
        await state.update_data(note_id=note_id, old_title=note.title, old_content=note.content)
        
        text = f"✏️ Редактирование заметки\n\n" \
               f"Текущий заголовок: {hbold(note.title)}\n\n" \
               f"Введите новый заголовок заметки или отправьте /cancel для отмены:"
        
        if query.message:
            try:
                await query.message.edit_text(text)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text при редактировании заметки: {e}")
        await query.answer()

@notes_router.callback_query(NotesAction.filter(F.action == "delete"))
async def cq_delete_note(query: types.CallbackQuery, callback_data: NotesAction, services_provider: 'BotServicesProvider'):
    """Удаление заметки"""
    user_id = query.from_user.id
    note_id = callback_data.note_id
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_DELETE_NOTES, services_provider, session):
            await query.answer("❌ У вас нет прав на удаление заметок.", show_alert=True)
            return
        
        # Получаем и удаляем заметку
        stmt = select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_telegram_id == user_id
        )
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        
        if not note:
            await query.answer("❌ Заметка не найдена или у вас нет к ней доступа.", show_alert=True)
            return
        
        note_title = note.title
        await session.delete(note)
        await session.commit()
        
        logger.info(f"[{MODULE_NAME}] Пользователь {user_id} удалил заметку ID {note_id}: '{note_title}'")
        
        text = f"✅ {hbold('Заметка удалена')}\n\n🗑️ Заметка \"{note_title}\" была удалена."
        keyboard = await get_notes_main_menu_keyboard(services_provider, user_id, session)
        
        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text при удалении заметки: {e}")
        await query.answer("Заметка удалена")

# === НАВИГАЦИЯ ===

@notes_router.callback_query(NotesAction.filter(F.action == "back_to_main"))
async def cq_back_to_main(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    """Возврат в главное меню модуля"""
    await cq_notes_main_menu(query, services_provider)

@notes_router.callback_query(NotesAction.filter(F.action == "back_to_list"))
async def cq_back_to_list(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    """Возврат к списку заметок"""
    await cq_notes_list(query, services_provider)

# === FSM ДЛЯ РЕДАКТИРОВАНИЯ ЗАМЕТОК ===

@notes_router.message(Command("cancel"), StateFilter(FSMEditNote))
async def cmd_cancel_edit(message: types.Message, state: FSMContext):
    """Отмена редактирования заметки"""
    await state.clear()
    await message.answer("❌ Редактирование заметки отменено.")

@notes_router.message(FSMEditNote.edit_title)
async def fsm_edit_note_title(message: types.Message, state: FSMContext, services_provider: 'BotServicesProvider'):
    """Обработка нового заголовка при редактировании"""
    user_id = message.from_user.id
    title = message.text.strip()
    
    # Проверяем длину заголовка
    if len(title) > 100:
        await message.answer("❌ Заголовок слишком длинный. Максимум 100 символов.")
        return
    
    if not title:
        await message.answer("❌ Заголовок не может быть пустым.")
        return
    
    # Сохраняем новый заголовок и переходим к редактированию содержания
    data = await state.get_data()
    await state.update_data(new_title=title)
    await state.set_state(FSMEditNote.edit_content)
    
    old_content = data.get("old_content", "")
    text = f"✏️ Редактирование заметки\n\n" \
           f"Новый заголовок: {hbold(title)}\n\n" \
           f"Текущее содержание:\n{old_content}\n\n" \
           f"Введите новое содержание заметки или отправьте /cancel для отмены:"
    
    await message.answer(text)

@notes_router.message(FSMEditNote.edit_content)
async def fsm_edit_note_content(message: types.Message, state: FSMContext, services_provider: 'BotServicesProvider'):
    """Обработка нового содержания при редактировании"""
    user_id = message.from_user.id
    content = message.text.strip()
    
    # Проверяем длину содержания
    if len(content) > 4000:
        await message.answer("❌ Содержание слишком длинное. Максимум 4000 символов.")
        return
    
    if not content:
        await message.answer("❌ Содержание не может быть пустым.")
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    note_id = data.get("note_id")
    new_title = data.get("new_title")
    
    if not note_id or not new_title:
        await message.answer("❌ Ошибка: данные редактирования потеряны. Попробуйте снова.")
        await state.clear()
        return
    
    # Обновляем заметку в БД
    async with services_provider.db.get_session() as session:
        stmt = select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_telegram_id == user_id
        )
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        
        if not note:
            await message.answer("❌ Заметка не найдена или у вас нет к ней доступа.")
            await state.clear()
            return
        
        # Обновляем поля
        note.title = new_title
        note.content = content
        note.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(note)
        
        logger.info(f"[{MODULE_NAME}] Пользователь {user_id} отредактировал заметку ID {note.id}: '{new_title}'")
    
    await state.clear()
    
    # Показываем обновленную заметку
    created_date = note.created_at.strftime("%d.%m.%Y %H:%M")
    updated_date = note.updated_at.strftime("%d.%m.%Y %H:%M")
    text = f"✅ {hbold('Заметка обновлена')}\n\n" \
           f"📝 {hbold(note.title)}\n\n" \
           f"📄 {note.content}\n\n" \
           f"🕒 Создана: {created_date}\n" \
           f"📝 Изменена: {updated_date}"
    
    async with services_provider.db.get_session() as session:
        keyboard = await get_note_actions_keyboard(note.id, services_provider, user_id, session)
    
    await message.answer(text, reply_markup=keyboard)
