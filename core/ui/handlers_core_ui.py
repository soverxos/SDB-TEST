# SwiftDevBot/core/ui/handlers_core_ui.py
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart, Command, StateFilter 
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup 
from aiogram.utils.markdown import hbold, hitalic, hcode 
import html # <--- ИМПОРТИРУЕМ СТАНДАРТНЫЙ МОДУЛЬ html
from loguru import logger
from aiogram.exceptions import TelegramBadRequest 
from aiogram.types import ReplyKeyboardRemove 

from .callback_data_factories import CoreMenuNavigate, ModuleMenuEntry, CoreServiceAction 
from .keyboards_core import (
    get_main_menu_reply_keyboard,
    get_modules_list_keyboard, 
    get_welcome_confirmation_keyboard, 
    get_profile_menu_keyboard,         
    get_language_selection_keyboard, 
    TEXTS_CORE_KEYBOARDS_EN 
)
from core.database.core_models import User as DBUser 
from core.ui.registry_ui import ModuleUIEntry 
from sqlalchemy import select 
from core.i18n.translator import Translator 

from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession 

core_ui_router = Router(name="sdb_core_ui_handlers")
MODULE_NAME_FOR_LOG = "CoreUI"

class FSMFeedback(StatesGroup):
    waiting_for_feedback_message = State()

async def show_main_menu_reply(
    message_or_query: types.Message | types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    text_override: Optional[str] = None,
    state: Optional[FSMContext] = None 
):
    if state: 
        current_fsm_state = await state.get_state()
        if current_fsm_state is not None:
            logger.info(f"[{MODULE_NAME_FOR_LOG}] Сброс состояния FSM ({current_fsm_state}) перед показом главного reply-меню для пользователя {sdb_user.telegram_id}.")
            await state.clear()

    user_id = sdb_user.telegram_id
    user_display_name = sdb_user.full_name 
    logger.debug(f"[{MODULE_NAME_FOR_LOG}] User {user_id} ({user_display_name}) showing main reply menu.")
    
    texts = TEXTS_CORE_KEYBOARDS_EN
    default_text = f"🏠 {hbold('Главное меню SwiftDevBot')}\nС возвращением, {hbold(user_display_name)}! Выберите действие:"
    text_to_send = text_override if text_override else default_text
    
    keyboard = await get_main_menu_reply_keyboard(services_provider=services_provider, user_telegram_id=user_id)
    
    target_chat_id = message_or_query.chat.id if isinstance(message_or_query, types.Message) else message_or_query.message.chat.id # type: ignore

    if isinstance(message_or_query, types.CallbackQuery) and message_or_query.message:
        try:
            if message_or_query.message.reply_markup: 
                 await message_or_query.message.edit_reply_markup(reply_markup=None)
        except Exception as e_del_edit:
            logger.warning(f"Не удалось изменить/удалить старое сообщение перед показом reply menu: {e_del_edit}")
    
    await bot.send_message(target_chat_id, text_to_send, reply_markup=keyboard)
    
    if isinstance(message_or_query, types.CallbackQuery):
        await message_or_query.answer()


@core_ui_router.message(CommandStart())
async def handle_start_command(
    message: types.Message,
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser, 
    state: FSMContext, 
    user_was_just_created: Optional[bool] = False 
):
    user_tg = message.from_user 
    if not user_tg: return

    logger.info(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_tg.id} (@{user_tg.username or 'N/A'}) вызвал /start. "
                f"SDB_User DB ID: {sdb_user.id}. Был только что создан (в middleware): {user_was_just_created}.")

    texts = TEXTS_CORE_KEYBOARDS_EN
    is_owner_from_config = sdb_user.telegram_id in services_provider.config.core.super_admins
    user_display_name = sdb_user.full_name 

    if is_owner_from_config or not user_was_just_created: 
        logger.info(f"[{MODULE_NAME_FOR_LOG}] Пользователь {sdb_user.telegram_id} ({'Владелец' if is_owner_from_config else 'существующий'}). Показ главного reply-меню.")
        await show_main_menu_reply(message, bot, services_provider, sdb_user, state=state) 
    else: 
        logger.info(f"[{MODULE_NAME_FOR_LOG}] Пользователь {sdb_user.telegram_id} новый. Показ приветственного сообщения.")
        welcome_title = texts.get("welcome_message_title", "Добро пожаловать!")
        welcome_body = texts.get("welcome_message_body", "Описание бота...")
        full_welcome_text = f"{hbold(welcome_title)}\n\n{welcome_body}"
        welcome_keyboard = get_welcome_confirmation_keyboard()
        await message.answer(full_welcome_text, reply_markup=welcome_keyboard)


@core_ui_router.callback_query(CoreServiceAction.filter(F.action == "confirm_registration"))
async def cq_confirm_registration_and_show_main_menu(
    query: types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    state: FSMContext 
):
    user_id = sdb_user.telegram_id 
    user_full_name = sdb_user.full_name
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_id} ({user_full_name}) подтвердил регистрацию, показ главного reply-меню.")
    
    if query.message:
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение с приветствием: {e}")
            
    await show_main_menu_reply(query, bot, services_provider, sdb_user, 
                               text_override=f"Отлично, {hbold(user_full_name)}! Вот главное меню:",
                               state=state) 


@core_ui_router.callback_query(CoreServiceAction.filter(F.action == "cancel_registration"))
async def cq_cancel_registration(
    query: types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider', 
    state: FSMContext 
):
    user_id = query.from_user.id 
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_id} отменил регистрацию/продолжение.")
    await state.clear() 
    
    texts = TEXTS_CORE_KEYBOARDS_EN
    cancel_text = texts.get("registration_cancelled_message", "Регистрация отменена.")

    if query.message:
        try:
            await query.message.delete()
        except Exception as e_delete:
            logger.warning(f"[{MODULE_NAME_FOR_LOG}] Не удалось удалить сообщение после отмены регистрации (user: {user_id}): {e_delete}")
    
    await bot.send_message(user_id, cancel_text, reply_markup=ReplyKeyboardRemove())
    await query.answer()


@core_ui_router.message(F.text == TEXTS_CORE_KEYBOARDS_EN["main_menu_reply_modules"], StateFilter(None)) 
async def handle_text_modules_list(message: types.Message, bot:Bot, services_provider: 'BotServicesProvider', sdb_user: DBUser):
    logger.info(f"Пользователь {sdb_user.telegram_id} нажал reply-кнопку 'Модули'")
    await send_modules_list_message(message.chat.id, bot, services_provider, sdb_user, page=1)

@core_ui_router.message(F.text == TEXTS_CORE_KEYBOARDS_EN["main_menu_reply_profile"], StateFilter(None))
async def handle_text_profile(message: types.Message, bot: Bot, services_provider: 'BotServicesProvider', sdb_user: DBUser):
    logger.info(f"Пользователь {sdb_user.telegram_id} нажал reply-кнопку 'Профиль'")
    await send_profile_message(message.chat.id, bot, services_provider, sdb_user)

@core_ui_router.message(F.text == TEXTS_CORE_KEYBOARDS_EN["main_menu_reply_feedback"], StateFilter(None))
async def handle_text_feedback_start_fsm(
    message: types.Message, 
    services_provider: 'BotServicesProvider', 
    sdb_user: DBUser, 
    state: FSMContext
):
    logger.info(f"Пользователь {sdb_user.telegram_id} нажал reply-кнопку 'Обратная связь', вход в FSM.")
    text = (
        "✍️ Пожалуйста, напишите ваше сообщение для обратной связи.\n"
        f"{hitalic('Для отмены введите /cancel_feedback')}"
    )
    await state.set_state(FSMFeedback.waiting_for_feedback_message)
    await message.answer(text) 

@core_ui_router.message(StateFilter(FSMFeedback.waiting_for_feedback_message), F.text)
async def process_feedback_message(
    message: types.Message, 
    bot: Bot, 
    services_provider: 'BotServicesProvider', 
    sdb_user: DBUser, 
    state: FSMContext
):
    feedback_text = message.text
    user_id = sdb_user.telegram_id
    # ИСПОЛЬЗУЕМ html.escape
    user_full_name_escaped = html.escape(sdb_user.full_name) 
    username_escaped = f"@{html.escape(sdb_user.username)}" if sdb_user.username else "(нет username)"
    
    logger.info(f"Получено сообщение обратной связи от {user_id} ({username_escaped}): '{feedback_text[:100]}...'")

    admin_message_header = (
        f"📬 {hbold('Новый отзыв от пользователя!')}\n\n"
        f"👤 От: {user_full_name_escaped}\n"
        f"🆔 Telegram ID: {hcode(str(user_id))}\n"
        f"🔗 Username: {username_escaped}\n"
        f"🕒 Время: {message.date.strftime('%Y-%m-%d %H:%M:%S %Z') if message.date else 'N/A'}\n"
    )
    admin_message_body = f"\n📝 {hbold('Текст отзыва:')}\n{html.escape(feedback_text)}" # ИСПОЛЬЗУЕМ html.escape
    full_admin_message = admin_message_header + admin_message_body
    
    sent_to_admins_count = 0
    if services_provider.config.core.super_admins:
        for admin_tg_id in services_provider.config.core.super_admins:
            try:
                await bot.send_message(admin_tg_id, full_admin_message)
                sent_to_admins_count += 1
            except Exception as e:
                logger.error(f"Не удалось отправить обратную связь админу {admin_tg_id}: {e}")
        if sent_to_admins_count > 0:
            logger.info(f"Отзыв успешно отправлен {sent_to_admins_count} супер-администраторам.")
        else:
            logger.warning("Отзыв не был отправлен ни одному супер-администратору (возможно, список пуст или произошли ошибки).")
    else:
        logger.warning("Список супер-администраторов пуст. Отзыв не будет отправлен.")
    
    await message.reply("Спасибо за ваш отзыв! Мы его получили.")
    await show_main_menu_reply(message, bot, services_provider, sdb_user, text_override="Главное меню:", state=state)

@core_ui_router.message(Command("cancel_feedback"), StateFilter(FSMFeedback.waiting_for_feedback_message))
async def cancel_feedback_fsm(
    message: types.Message, 
    bot: Bot,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    state: FSMContext
):
    logger.info(f"Пользователь {sdb_user.telegram_id} отменил ввод обратной связи.")
    await message.reply("Ввод обратной связи отменен.")
    await show_main_menu_reply(message, bot, services_provider, sdb_user, text_override="Главное меню:", state=state)


@core_ui_router.message(F.text == TEXTS_CORE_KEYBOARDS_EN["main_menu_reply_admin_panel"], StateFilter(None))
async def handle_text_admin_panel(message: types.Message, bot:Bot, services_provider: 'BotServicesProvider', sdb_user: DBUser, state: FSMContext): 
    logger.info(f"Пользователь {sdb_user.telegram_id} нажал reply-кнопку 'Админ-панель'")
    await state.clear() 
    from core.admin.entry.handlers_entry import send_admin_main_menu 
    await send_admin_main_menu(message, services_provider) 


@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "main_reply"))
async def cq_nav_to_main_menu_reply(
    query: types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    state: FSMContext 
):
    await show_main_menu_reply(query, bot, services_provider, sdb_user, state=state) 


async def send_modules_list_message(
    chat_id: int, 
    bot: Bot, 
    services_provider: 'BotServicesProvider', 
    sdb_user: DBUser, 
    page: int = 1,
    message_to_edit: Optional[types.Message] = None 
):
    user_id = sdb_user.telegram_id
    texts = TEXTS_CORE_KEYBOARDS_EN
    items_per_page = 5
    keyboard = await get_modules_list_keyboard(services_provider, user_id, page, items_per_page)
    
    num_module_buttons = 0; total_accessible_items = 0
    if keyboard.inline_keyboard: 
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith(ModuleMenuEntry.__prefix__):
                    num_module_buttons +=1

    all_module_ui_entries_temp = services_provider.ui_registry.get_all_module_entries()
    if all_module_ui_entries_temp:
        async with services_provider.db.get_session() as session:
            for entry_temp in all_module_ui_entries_temp:
                if entry_temp.required_permission_to_view:
                    if await services_provider.rbac.user_has_permission(session, user_id, entry_temp.required_permission_to_view):
                        total_accessible_items +=1
                else: total_accessible_items +=1
    
    total_pages = (total_accessible_items + items_per_page - 1) // items_per_page
    total_pages = max(1, total_pages)

    if num_module_buttons == 0 and page == 1: text = texts["modules_list_no_modules"]
    else: text = texts["modules_list_title_template"].format(current_page=page, total_pages=total_pages)
    
    if message_to_edit: 
        try:
            if message_to_edit.text != text or message_to_edit.reply_markup != keyboard:
                await message_to_edit.edit_text(text, reply_markup=keyboard)
            return 
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning(f"Не удалось edit modules list (inline pagination): {e}")
            return
        except Exception as e:
            logger.error(f"Ошибка в send_modules_list_message (edit): {e}", exc_info=True)
            return
    
    await bot.send_message(chat_id, text, reply_markup=keyboard)


async def send_profile_message(
    chat_id: int, 
    bot: Bot, 
    services_provider: 'BotServicesProvider', 
    sdb_user: DBUser,
    message_to_edit: Optional[types.Message] = None
):
    texts = TEXTS_CORE_KEYBOARDS_EN
    reg_date_str = sdb_user.created_at.strftime('%d.%m.%Y %H:%M') if sdb_user.created_at else texts["profile_no_reg_date"]
    username_str = f"@{sdb_user.username}" if sdb_user.username else texts["profile_no_username"] 
    current_lang = sdb_user.preferred_language_code or services_provider.config.core.i18n.default_locale
    lang_display_name = current_lang.upper()

    profile_text = texts["profile_info_template"].format(
        user_id=hcode(str(sdb_user.telegram_id)),
        full_name=hbold(sdb_user.full_name),
        username=username_str,
        registration_date=reg_date_str,
        current_language=lang_display_name
    )
    final_text = f"{hbold(texts['profile_title'])}\n\n{profile_text}"
    keyboard = await get_profile_menu_keyboard(sdb_user, services_provider)
    
    if message_to_edit:
        try:
            if message_to_edit.text != final_text or message_to_edit.reply_markup != keyboard:
                await message_to_edit.edit_text(final_text, reply_markup=keyboard)
            return
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning(f"Не удалось edit profile (inline nav): {e}")
            return
        except Exception as e:
            logger.error(f"Ошибка в send_profile_message (edit): {e}", exc_info=True)
            return
            
    await bot.send_message(chat_id, final_text, reply_markup=keyboard)


@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "modules_list"))
async def cq_nav_to_modules_list(
    query: types.CallbackQuery, 
    callback_data: CoreMenuNavigate, 
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    user_id = sdb_user.telegram_id
    page = callback_data.page if callback_data.page is not None else 1
    logger.debug(f"[{MODULE_NAME_FOR_LOG}] User {user_id} requested modules list (inline nav), page: {page}")
    
    if query.message:
        await send_modules_list_message(query.message.chat.id, bot, services_provider, sdb_user, page, message_to_edit=query.message)
    await query.answer()


@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "profile"))
async def cq_nav_to_profile( 
    query: types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser 
):
    if query.message:
        await send_profile_message(query.message.chat.id, bot, services_provider, sdb_user, message_to_edit=query.message)
    await query.answer()


@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "profile_change_lang_list"))
async def cq_profile_show_language_list(
    query: types.CallbackQuery,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    user_id = sdb_user.telegram_id
    logger.debug(f"[{MODULE_NAME_FOR_LOG}] User {user_id} requested language selection list.")
    
    texts = TEXTS_CORE_KEYBOARDS_EN
    i18n_settings = services_provider.config.core.i18n
    
    current_lang = sdb_user.preferred_language_code or i18n_settings.default_locale
    available_langs = i18n_settings.available_locales
    
    text = texts.get("profile_select_language_title", "Выберите язык:")
    keyboard = await get_language_selection_keyboard(current_lang, available_langs)
    
    if query.message:
        try:
            if query.message.text != text or query.message.reply_markup != keyboard: 
                await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer()
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                 logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка edit_text в cq_profile_show_language_list: {e}")
            await query.answer() 
        except Exception as e:
            logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка в cq_profile_show_language_list: {e}", exc_info=True)
            await query.answer("Ошибка отображения.")

@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "profile_set_lang"))
async def cq_profile_set_language(
    query: types.CallbackQuery,
    callback_data: CoreMenuNavigate,
    bot: Bot, 
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    translator: Translator 
):
    new_lang_code = callback_data.payload
    user_id = sdb_user.telegram_id
    
    if not new_lang_code or new_lang_code not in services_provider.config.core.i18n.available_locales:
        logger.warning(f"[{MODULE_NAME_FOR_LOG}] User {user_id} попытался установить некорректный язык: {new_lang_code}")
        await query.answer("Выбран некорректный язык.", show_alert=True)
        if query.message: 
            await send_profile_message(query.message.chat.id, bot, services_provider, sdb_user, message_to_edit=query.message)
        return

    logger.info(f"[{MODULE_NAME_FOR_LOG}] User {user_id} устанавливает язык: {new_lang_code}")
    
    user_service = services_provider.user_service 
    async with services_provider.db.get_session() as session: 
        user_in_session = await session.get(DBUser, sdb_user.id) 
        if user_in_session:
            if await user_service.update_user_language(user_in_session, new_lang_code, session):
                try:
                    await session.commit()
                    sdb_user.preferred_language_code = new_lang_code 
                    
                    logger.success(f"[{MODULE_NAME_FOR_LOG}] Язык для пользователя {user_id} успешно изменен на {new_lang_code} в БД.")
                    await query.answer(f"Language changed to {new_lang_code.upper()}", show_alert=False)
                except Exception as e_commit:
                    await session.rollback()
                    logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка commit при смене языка для {user_id}: {e_commit}", exc_info=True)
                    await query.answer("Ошибка сохранения языка.", show_alert=True)
            else:
                await query.answer(f"Язык уже установлен на {new_lang_code.upper()}.", show_alert=False)
        else: 
            await query.answer("Ошибка: пользователь не найден для обновления языка.", show_alert=True)
            
    if query.message:
        await send_profile_message(query.message.chat.id, bot, services_provider, sdb_user, message_to_edit=query.message)
    

@core_ui_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "feedback_fsm_start"))
async def cq_nav_to_feedback_fsm_start( 
    query: types.CallbackQuery, 
    bot: Bot, 
    services_provider: 'BotServicesProvider', 
    sdb_user: DBUser, 
    state: FSMContext
):
    user_id = query.from_user.id
    logger.debug(f"[{MODULE_NAME_FOR_LOG}] User {user_id} запросил обратную связь (FSM через callback).")
    text = (
        "✍️ Пожалуйста, напишите ваше сообщение для обратной связи.\n"
        f"{hitalic('Для отмены введите /cancel_feedback')}"
    )
    await state.set_state(FSMFeedback.waiting_for_feedback_message)
    
    if query.message:
        try: 
            await query.message.edit_text(text, reply_markup=None) 
        except TelegramBadRequest as e:
             if "message is not modified" not in str(e).lower():
                logger.warning(f"Не удалось отредактировать сообщение перед вводом feedback (callback): {e}")
                await bot.send_message(user_id, text) 
        except Exception as e_edit_fb:
            logger.warning(f"Не удалось отредактировать сообщение перед вводом feedback (callback): {e_edit_fb}")
            await bot.send_message(user_id, text)
    else: 
        await bot.send_message(user_id, text)
    await query.answer()


@core_ui_router.callback_query(CoreServiceAction.filter(F.action == "delete_this_message"))
async def cq_service_action_delete_message(query: types.CallbackQuery, bot: Bot):
    user_id = query.from_user.id
    message_id = query.message.message_id if query.message else "N/A"
    logger.debug(f"[{MODULE_NAME_FOR_LOG}] User {user_id} requested to delete message_id: {message_id}")
    
    try:
        if query.message:
            await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await query.answer("Сообщение удалено.") 
        else:
            logger.warning(f"[{MODULE_NAME_FOR_LOG}] Не найдено сообщение для удаления по запросу от user {user_id}.")
            await query.answer("Не найдено сообщение для удаления.")
    except TelegramBadRequest as e: 
        logger.warning(f"[{MODULE_NAME_FOR_LOG}] Не удалось удалить сообщение {message_id} для user {user_id}: {e} (возможно, уже удалено или нет прав).")
        await query.answer() 
    except Exception as e:
        logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка при удалении сообщения {message_id} для user {user_id}: {e}", exc_info=True)
        await query.answer("Ошибка при удалении сообщения.", show_alert=True)