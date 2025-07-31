# core/ui/navigation_core.py

from aiogram import Router, F, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.markdown import hbold, hitalic
from loguru import logger

from .callback_data_factories import CoreMenuNavigate, ModuleMenuEntry, CoreServiceAction
from .keyboards_core import (
    get_main_menu_keyboard, 
    get_modules_list_keyboard,
    # get_close_button_keyboard, # Если будет использоваться явно
    TEXTS_CORE_KEYBOARDS_EN 
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider

core_navigation_router = Router(name="sdb_core_ui_navigation_handlers")

@core_navigation_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "main"))
async def cq_nav_to_main_menu(
    query: types.CallbackQuery, 
    services_provider: 'BotServicesProvider' 
):
    user_id = query.from_user.id
    user_full_name = query.from_user.full_name
    logger.debug(f"User {user_id} ({user_full_name}) navigating to main menu.")
    
    texts = TEXTS_CORE_KEYBOARDS_EN
    text = f"🏠 {hbold('Главное меню SwiftDevBot')}\nПривет, {hbold(user_full_name)}! Выберите действие:"
    
    keyboard = await get_main_menu_keyboard(services_provider=services_provider, user_telegram_id=user_id)
    
    try:
        if query.message:
            if query.message.text != text or query.message.reply_markup != keyboard:
                await query.message.edit_text(text, reply_markup=keyboard)
            else:
                logger.trace("Сообщение главного меню не было изменено (текст и клавиатура совпадают).")
        await query.answer()
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.trace("Сообщение главного меню не было изменено (поймано исключение).")
            await query.answer()
        else:
            logger.warning(f"Не удалось отредактировать сообщение для главного меню (user: {user_id}): {e}")
            await query.answer("Ошибка отображения меню.", show_alert=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при показе главного меню (user: {user_id}): {e}", exc_info=True)
        await query.answer("Произошла серьезная ошибка.", show_alert=True)


@core_navigation_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "modules_list"))
async def cq_nav_to_modules_list(
    query: types.CallbackQuery, 
    callback_data: CoreMenuNavigate, 
    services_provider: 'BotServicesProvider' 
):
    user_id = query.from_user.id
    page = callback_data.page if callback_data.page is not None else 1
    logger.debug(f"User {user_id} requested modules list, page: {page}")

    texts = TEXTS_CORE_KEYBOARDS_EN
    
    module_ui_entries = services_provider.ui_registry.get_all_module_entries()
    items_per_page = 5 
    total_pages = (len(module_ui_entries) + items_per_page - 1) // items_per_page
    total_pages = max(1, total_pages) 

    text = texts["modules_list_title_template"].format(current_page=page, total_pages=total_pages)
    
    keyboard = await get_modules_list_keyboard(
        services_provider=services_provider, 
        user_telegram_id=user_id, 
        current_page=page,
        items_per_page=items_per_page
    )
    
    try:
        if query.message:
            if query.message.text != text or query.message.reply_markup != keyboard:
                await query.message.edit_text(text, reply_markup=keyboard)
            else:
                logger.trace("Сообщение списка модулей не было изменено.")
        await query.answer()
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.trace("Сообщение списка модулей не было изменено (поймано исключение).")
            await query.answer()
        else:
            logger.warning(f"Не удалось отредактировать сообщение для списка модулей (user: {user_id}): {e}")
            await query.answer("Ошибка отображения списка.", show_alert=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при показе списка модулей (user: {user_id}): {e}", exc_info=True)
        await query.answer("Произошла серьезная ошибка.", show_alert=True)

@core_navigation_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "profile"))
async def cq_nav_to_profile(
    query: types.CallbackQuery, 
    services_provider: 'BotServicesProvider' 
):
    user_id = query.from_user.id
    logger.debug(f"User {user_id} requested profile menu (WIP).")
    text = "👤 Раздел 'Профиль' находится в разработке."
    keyboard = await get_main_menu_keyboard(services_provider=services_provider, user_telegram_id=user_id) 
    if query.message:
        
        try:
            if query.message.text != text or query.message.reply_markup != keyboard:
                await query.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning(f"Ошибка edit_text в cq_nav_to_profile: {e}")
    await query.answer("Раздел в разработке.")

@core_navigation_router.callback_query(CoreMenuNavigate.filter(F.target_menu == "feedback"))
async def cq_nav_to_feedback(
    query: types.CallbackQuery, 
    services_provider: 'BotServicesProvider' 
):
    user_id = query.from_user.id
    logger.debug(f"User {user_id} requested feedback menu (WIP).")
    text = "✍️ Раздел 'Обратная связь' находится в разработке."
    keyboard = await get_main_menu_keyboard(services_provider=services_provider, user_telegram_id=user_id) 
    if query.message:
        try:
            if query.message.text != text or query.message.reply_markup != keyboard:
                await query.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning(f"Ошибка edit_text в cq_nav_to_feedback: {e}")
    await query.answer("Раздел в разработке.")

# Удален обработчик cq_nav_to_admin_panel, так как он конфликтовал
# с рабочим обработчиком в core/admin/handlers_admin_entry.py

@core_navigation_router.callback_query(CoreServiceAction.filter(F.action == "delete_this_message"))
async def cq_service_action_delete_message(query: types.CallbackQuery, bot: Bot):
    user_id = query.from_user.id
    message_id = query.message.message_id if query.message else "N/A"
    logger.debug(f"User {user_id} requested to delete message_id: {message_id}")
    
    try:
        if query.message:
            await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await query.answer("Сообщение удалено.") 
        else:
            logger.warning(f"Не найдено сообщение для удаления по запросу от user {user_id}.")
            await query.answer("Не найдено сообщение для удаления.")
    except TelegramBadRequest as e:
        logger.warning(f"Не удалось удалить сообщение {message_id} для user {user_id}: {e}")
        await query.answer()
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения {message_id} для user {user_id}: {e}", exc_info=True)
        await query.answer("Ошибка при удалении сообщения.", show_alert=True)