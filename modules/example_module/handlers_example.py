# modules/example_module/handlers_example.py
from aiogram import Router, types, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold, hcode, hitalic
from aiogram.exceptions import TelegramBadRequest 
from loguru import logger
from sqlalchemy import select, delete as sql_delete, func 

from .keyboards_example import (
    get_example_module_main_menu_keyboard,
    get_my_notes_keyboard,
    get_note_details_keyboard
)
from .callback_data_factories_example import ExampleModuleAction
from core.ui.callback_data_factories import ModuleMenuEntry, CoreMenuNavigate 
from .permissions import ( 
    MODULE_NAME, 
    PERM_ACCESS_USER_FEATURES,
    PERM_VIEW_MODULE_SETTINGS,
    PERM_VIEW_SECRET_INFO,
    PERM_PERFORM_BASIC_ACTION,
    PERM_PERFORM_ADVANCED_ACTION,
    PERM_MANAGE_OWN_NOTES,
    PERM_ADMIN_VIEW_ALL_NOTES,
    PERM_ADMIN_MANAGE_MODULE 
)
from .models import UserNote 

from typing import TYPE_CHECKING, Any, List, Optional
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession

example_module_router = Router(name="sdb_example_module_handlers")

class FSMExampleDialog(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()

class FSMAddNote(StatesGroup):
    waiting_for_note_text = State()

async def check_permission(
    user_id: int, 
    permission_name: str, 
    services: 'BotServicesProvider', 
    session: 'AsyncSession'
) -> bool:
    has_perm = await services.rbac.user_has_permission(session, user_id, permission_name)
    if not has_perm:
        logger.warning(f"[{MODULE_NAME}] Пользователь {user_id} попытался получить доступ к функции, требующей права '{permission_name}', но не имеет его.")
    return has_perm

@example_module_router.message(Command("example"))
async def handle_example_command(
    message: types.Message, 
    services_provider: 'BotServicesProvider'
):
    user_id = message.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вызвал команду /example.")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await message.answer("У вас нет доступа к этому модулю.")
            return

    module_info = services_provider.modules.get_module_info(MODULE_NAME)
    display_name = module_info.manifest.display_name if module_info and module_info.manifest else MODULE_NAME
    
    text = (f"Добро пожаловать в {hbold(display_name)}!\n"
            f"Выберите действие:")
    async with services_provider.db.get_session() as session: 
        keyboard = await get_example_module_main_menu_keyboard(services_provider, user_id, session)
    await message.answer(text, reply_markup=keyboard)

@example_module_router.callback_query(ModuleMenuEntry.filter(F.module_name == MODULE_NAME))
async def cq_show_example_module_main_menu(
    query: types.CallbackQuery, 
    callback_data: ModuleMenuEntry, 
    services_provider: 'BotServicesProvider'
):
    user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вошел в главное меню модуля.")

    async with services_provider.db.get_session() as session: 
        if not await check_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await query.answer("У вас нет доступа к этому меню.", show_alert=True)
            return

        module_info = services_provider.modules.get_module_info(MODULE_NAME)
        display_name = module_info.manifest.display_name if module_info and module_info.manifest else MODULE_NAME

        text = (f"Добро пожаловать в {hbold(display_name)}!\n"
                f"Выберите действие:")
        keyboard = await get_example_module_main_menu_keyboard(services_provider, user_id, session)
    
        if query.message:
            try:
                if query.message.text != text or query.message.reply_markup != keyboard:
                    await query.message.edit_text(text, reply_markup=keyboard)
                await query.answer()
            except TelegramBadRequest as e: # Используем импортированный TelegramBadRequest
                if "message is not modified" in str(e).lower(): await query.answer()
                else: logger.warning(f"[{MODULE_NAME}] Ошибка edit_text в меню модуля: {e}")
            except Exception as e: 
                logger.error(f"[{MODULE_NAME}] Ошибка в cq_show_example_module_main_menu: {e}", exc_info=True)
                await query.answer("Произошла ошибка.", show_alert=True)
        else:
            await query.answer()

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "show_module_settings"))
async def cq_action_show_module_settings(
    query: types.CallbackQuery, 
    services_provider: 'BotServicesProvider'
):
    user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} запросил показать глобальные настройки модуля.")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_VIEW_MODULE_SETTINGS, services_provider, session):
            await query.answer("У вас нет прав для просмотра этой информации.", show_alert=True)
            return

        actual_module_settings = services_provider.modules.get_module_settings(MODULE_NAME)
        settings_text_parts = [f"⚙️ {hbold('Глобальные настройки модуля')} {hcode(MODULE_NAME)}:"]
        if actual_module_settings:
            for key, value in actual_module_settings.items():
                settings_text_parts.append(f"  ▫️ {hcode(key)}: {hcode(str(value))}")
        else:
            settings_text_parts.append("Настройки не найдены или не загружены.")
        
        text = "\n".join(settings_text_parts)
        keyboard = await get_example_module_main_menu_keyboard(services_provider, user_id, session)
    
        if query.message:
            try:
                if query.message.text != text: await query.message.edit_text(text, reply_markup=keyboard)
                await query.answer()
            except TelegramBadRequest as e: # Используем импортированный TelegramBadRequest
                if "message is not modified" not in str(e).lower(): logger.warning(f"[{MODULE_NAME}] Ошибка edit_text (настройки): {e}")
                await query.answer()
            except Exception as e:
                logger.error(f"[{MODULE_NAME}] Ошибка в cq_action_show_module_settings: {e}", exc_info=True)
                await query.answer("Произошла ошибка.", show_alert=True)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "show_secret_info"))
async def cq_action_show_secret_info(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_VIEW_SECRET_INFO, services_provider, session):
            await query.answer("🤫 Это секретная информация, доступ ограничен!", show_alert=True)
            return
    await query.answer("🎉 Поздравляю! У вас есть доступ к этой супер-секретной информации! 🎉", show_alert=True)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "do_basic_action"))
async def cq_action_do_basic_action(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_PERFORM_BASIC_ACTION, services_provider, session):
            await query.answer("Действие недоступно.", show_alert=True)
            return
    await query.answer("✅ Базовое действие выполнено!", show_alert=True)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "do_advanced_action"))
async def cq_action_do_advanced_action(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_PERFORM_ADVANCED_ACTION, services_provider, session):
            await query.answer("🚀 Это действие требует особых прав!", show_alert=True)
            return
    await query.answer("💥 Продвинутое действие успешно выполнено! 💥", show_alert=True)

@example_module_router.message(Command("fsm_example"))
async def cmd_fsm_start(message: types.Message, state: FSMContext, services_provider: 'BotServicesProvider'):
    user_id = message.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} начал FSM-диалог (/fsm_example).")
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session): 
            await message.answer("У вас нет доступа к этой функции.")
            return
    await state.set_state(FSMExampleDialog.waiting_for_name)
    await message.answer("Как тебя зовут в этом FSM-диалоге?")

@example_module_router.message(StateFilter(FSMExampleDialog.waiting_for_name))
async def process_fsm_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not message.text:
        await message.answer("Пожалуйста, введи свое имя текстом.")
        return
    await state.update_data(name=message.text)
    await state.set_state(FSMExampleDialog.waiting_for_age)
    logger.info(f"[{MODULE_NAME}] FSM: Пользователь {user_id} ввел имя: {message.text}")
    await message.answer(f"Приятно, {hitalic(message.text)}! А сколько тебе лет (FSM)?")

@example_module_router.message(StateFilter(FSMExampleDialog.waiting_for_age))
async def process_fsm_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not message.text or not message.text.isdigit():
        await message.answer("Пожалуйста, введи свой возраст цифрами.")
        return
    age = int(message.text)
    if not (0 < age < 120):
        await message.answer("Необычный возраст. Попробуй еще раз.")
        return
    user_data = await state.get_data()
    name = user_data.get("name", "Незнакомец")
    logger.info(f"[{MODULE_NAME}] FSM: Пользователь {user_id} (имя: {name}) ввел возраст: {age}")
    await message.answer(
        f"Запомнил, {hitalic(name)} ({age} лет)!\n"
        f"FSM диалог завершен. Состояние сброшено."
    )
    await state.clear() 

@example_module_router.message(Command("cancel_fsm"), StateFilter(FSMExampleDialog)) 
async def cancel_fsm_dialog(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(f"[{MODULE_NAME}] Пользователь {message.from_user.id} отменил FSM диалог из состояния {current_state}")
    await state.clear()
    await message.answer("FSM диалог отменен.")

@example_module_router.message(Command("my_notes"))
async def cmd_my_notes(message: types.Message, services_provider: 'BotServicesProvider'):
    user_id = message.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} запросил свои заметки (/my_notes).")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await message.answer("У вас нет прав для управления заметками.")
            return

        stmt = select(UserNote).where(UserNote.user_telegram_id == user_id).order_by(UserNote.created_at.desc())
        result = await session.execute(stmt)
        notes: List[UserNote] = list(result.scalars().all())
        
        text = f"📝 {hbold('Ваши заметки')}:"
        if not notes:
            text += "\nУ вас пока нет заметок. Можете добавить новую."
            
        keyboard = await get_my_notes_keyboard(notes, services_provider, user_id, session)
        await message.answer(text, reply_markup=keyboard)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "my_notes_list"))
async def cq_my_notes_list(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} запросил список своих заметок (callback).")
    
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await query.answer("У вас нет прав для управления заметками.", show_alert=True)
            return

        stmt = select(UserNote).where(UserNote.user_telegram_id == user_id).order_by(UserNote.created_at.desc())
        result = await session.execute(stmt)
        notes: List[UserNote] = list(result.scalars().all())
        
        text = f"📝 {hbold('Ваши заметки')}:"
        if not notes:
            text += "\nУ вас пока нет заметок. Можете добавить новую."
            
        keyboard = await get_my_notes_keyboard(notes, services_provider, user_id, session)
        if query.message:
            try:
                if query.message.text != text or query.message.reply_markup != keyboard:
                    await query.message.edit_text(text, reply_markup=keyboard)
                await query.answer()
            except TelegramBadRequest as e: # Используем импортированный TelegramBadRequest
                if "message is not modified" not in str(e).lower(): logger.warning(f"Ошибка edit_text в cq_my_notes_list: {e}")
                await query.answer()
            except Exception as e:
                logger.error(f"Ошибка в cq_my_notes_list: {e}", exc_info=True)
                await query.answer("Ошибка.", show_alert=True)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "add_note_start"))
async def cq_add_note_start(query: types.CallbackQuery, state: FSMContext, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await query.answer("У вас нет прав для добавления заметок.", show_alert=True)
            return
    
    module_settings = services_provider.modules.get_module_settings(MODULE_NAME)
    max_notes = module_settings.get("max_notes_per_user", 5) if module_settings else 5
    
    async with services_provider.db.get_session() as session: 
        count_stmt = select(func.count(UserNote.id)).where(UserNote.user_telegram_id == user_id)
        notes_count_res = await session.execute(count_stmt)
        notes_count = notes_count_res.scalar_one_or_none() or 0

    if notes_count >= max_notes:
        await query.answer(f"Достигнут лимит заметок ({max_notes} шт.). Удалите старые, чтобы добавить новые.", show_alert=True)
        return

    await state.set_state(FSMAddNote.waiting_for_note_text)
    await query.message.answer("Введите текст вашей новой заметки:") # type: ignore
    await query.answer()

@example_module_router.message(StateFilter(FSMAddNote.waiting_for_note_text))
async def process_add_note_text(message: types.Message, state: FSMContext, services_provider: 'BotServicesProvider'):
    user_id = message.from_user.id
    if not message.text:
        await message.answer("Текст заметки не может быть пустым. Попробуйте еще раз или введите /cancel_note.")
        return

    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await message.answer("У вас нет прав для добавления заметок.")
            await state.clear()
            return
        
        new_note = UserNote(user_telegram_id=user_id, note_text=message.text)
        session.add(new_note)
        try:
            await session.commit()
            logger.info(f"[{MODULE_NAME}] Пользователь {user_id} добавил новую заметку: '{message.text[:30]}...'")
            await message.answer(f"✅ Заметка добавлена!\nИспользуйте /my_notes для просмотра.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сохранения заметки для {user_id}: {e}", exc_info=True)
            await message.answer("Не удалось сохранить заметку. Попробуйте позже.")
        finally:
            await state.clear()

@example_module_router.message(Command("cancel_note"), StateFilter(FSMAddNote))
async def cancel_add_note_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление заметки отменено.")

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "view_note_details"))
async def cq_view_note_details(query: types.CallbackQuery, callback_data: ExampleModuleAction, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    note_id = callback_data.item_id
    if note_id is None:
        await query.answer("Ошибка: ID заметки не указан.", show_alert=True); return

    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await query.answer("У вас нет прав для просмотра этой заметки.", show_alert=True); return
        
        note = await session.get(UserNote, note_id)
        if not note or note.user_telegram_id != user_id:
            await query.answer("Заметка не найдена или у вас нет к ней доступа.", show_alert=True); return
            
        text = f"📝 {hbold('Детали заметки:')}\n\n{hitalic(note.note_text)}\n\nСтатус: {'✅ Выполнено' if note.is_done else '🔘 В процессе'}"
        keyboard = await get_note_details_keyboard(note, services_provider, user_id, session)
        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
                await query.answer()
            except Exception as e: logger.error(f"Ошибка в cq_view_note_details: {e}")

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "toggle_note_done"))
async def cq_toggle_note_done(query: types.CallbackQuery, callback_data: ExampleModuleAction, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    note_id = callback_data.item_id
    if note_id is None: await query.answer("Ошибка ID.", show_alert=True); return

    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await query.answer("Нет прав.", show_alert=True); return
        
        note = await session.get(UserNote, note_id)
        if not note or note.user_telegram_id != user_id:
            await query.answer("Заметка не найдена/нет доступа.", show_alert=True); return
            
        note.is_done = not note.is_done
        session.add(note)
        alert_text = ""
        try:
            await session.commit()
            alert_text = "Статус заметки изменен."
            logger.info(f"Статус заметки ID {note.id} изменен на {note.is_done} пользователем {user_id}.")
            text = f"📝 {hbold('Детали заметки:')}\n\n{hitalic(note.note_text)}\n\nСтатус: {'✅ Выполнено' if note.is_done else '🔘 В процессе'}"
            keyboard = await get_note_details_keyboard(note, services_provider, user_id, session)
            if query.message: await query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await session.rollback()
            alert_text = "Ошибка сохранения."
            logger.error(f"Ошибка toggle_note_done: {e}")
        await query.answer(alert_text)

@example_module_router.callback_query(ExampleModuleAction.filter(F.action == "delete_note_confirm"))
async def cq_delete_note_confirm(query: types.CallbackQuery, callback_data: ExampleModuleAction, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    note_id = callback_data.item_id
    if note_id is None: await query.answer("Ошибка ID.", show_alert=True); return

    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_MANAGE_OWN_NOTES, services_provider, session):
            await query.answer("Нет прав.", show_alert=True); return
        
        stmt = sql_delete(UserNote).where(UserNote.id == note_id, UserNote.user_telegram_id == user_id)
        result = await session.execute(stmt)
        alert_text = ""
        if result.rowcount > 0:
            try:
                await session.commit()
                alert_text = "Заметка удалена."
                logger.info(f"Заметка ID {note_id} удалена пользователем {user_id}.")
                notes_stmt = select(UserNote).where(UserNote.user_telegram_id == user_id).order_by(UserNote.created_at.desc())
                notes_res = await session.execute(notes_stmt)
                notes: List[UserNote] = list(notes_res.scalars().all())
                list_text = f"📝 {hbold('Ваши заметки')}:" + ("\nУ вас пока нет заметок." if not notes else "")
                list_kb = await get_my_notes_keyboard(notes, services_provider, user_id, session)
                if query.message: await query.message.edit_text(list_text, reply_markup=list_kb)
            except Exception as e:
                await session.rollback()
                alert_text = "Ошибка удаления."
                logger.error(f"Ошибка commit при удалении заметки: {e}")
        else:
            alert_text = "Заметка не найдена или уже удалена."
        await query.answer(alert_text)

@example_module_router.message(Command("example_admin"))
async def cmd_example_admin(message: types.Message, services_provider: 'BotServicesProvider'):
    user_id = message.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_permission(user_id, PERM_ADMIN_MANAGE_MODULE, services_provider, session):
            await message.answer("У вас нет прав для этой команды.")
            return
    await message.answer("Вы выполнили административную команду модуля Example!")