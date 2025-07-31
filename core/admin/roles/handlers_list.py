# core/admin/roles/handlers_list.py
from aiogram import Router, types, F, Bot 
from aiogram.utils.markdown import hbold
from loguru import logger
from sqlalchemy import select, func as sql_func
from aiogram.exceptions import TelegramBadRequest # <--- ИСПРАВЛЕН ИМПОРТ

from core.ui.callback_data_factories import AdminRolesPanelNavigate
from .keyboards_roles import get_admin_roles_list_keyboard_local, ROLES_MGMT_TEXTS
from core.admin.filters_admin import can_view_admin_panel_filter 
from core.rbac.service import PERMISSION_CORE_ROLES_VIEW
from core.database.core_models import Role as DBRole

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession 

roles_list_router = Router(name="sdb_admin_roles_list_handlers")
MODULE_NAME_FOR_LOG = "AdminRoleMgmtList"

#roles_list_router.callback_query.filter(can_view_admin_panel_filter) 

@roles_list_router.callback_query(AdminRolesPanelNavigate.filter(F.action == "list"))
async def cq_admin_roles_list_entry( 
    query: types.CallbackQuery,
    callback_data: AdminRolesPanelNavigate, 
    services_provider: 'BotServicesProvider',
    bot: Bot 
):
    admin_user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Администратор {admin_user_id} запросил список ролей.")

    async with services_provider.db.get_session() as session: # type: AsyncSession
        has_perm_to_view_list = False
        is_owner_from_config = admin_user_id in services_provider.config.core.super_admins
        if is_owner_from_config:
            has_perm_to_view_list = True
        else:
            try:
                has_perm_to_view_list = await services_provider.rbac.user_has_permission(session, admin_user_id, PERMISSION_CORE_ROLES_VIEW)
            except Exception as e_perm_check_list:
                logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка проверки права PERMISSION_CORE_ROLES_VIEW для user {admin_user_id}: {e_perm_check_list}")
                await bot(query.answer("Ошибка проверки прав.", show_alert=True))
                return

        if not has_perm_to_view_list:
            await bot(query.answer("У вас нет прав для просмотра списка ролей.", show_alert=True)) 
            return
        
        all_roles: List[DBRole] = await services_provider.rbac.get_all_roles(session)
        
        text = f"{ROLES_MGMT_TEXTS['role_list_title']}\n{ROLES_MGMT_TEXTS['role_list_select_action']}"
        keyboard = await get_admin_roles_list_keyboard_local(all_roles, services_provider, admin_user_id, session)

        target_chat_id = query.message.chat.id if query.message else admin_user_id

        try:
            if query.message and text != query.message.text: 
                await bot(query.message.edit_text(text, reply_markup=keyboard))
                logger.debug(f"[{MODULE_NAME_FOR_LOG}] Сообщение со списком ролей отредактировано.")
            elif not query.message: 
                 await bot.send_message(target_chat_id, text, reply_markup=keyboard)
                 logger.debug(f"[{MODULE_NAME_FOR_LOG}] Сообщение со списком ролей отправлено (т.к. query.message был None).")
            else:
                logger.trace(f"[{MODULE_NAME_FOR_LOG}] Сообщение списка ролей не изменено.")
            
            # Попытка ответить на callback query
            try:
                await bot(query.answer())
            except Exception as e_answer:
                if "query is too old" in str(e_answer).lower() or "query id is invalid" in str(e_answer).lower():
                    logger.debug(f"[{MODULE_NAME_FOR_LOG}] Callback query устарел, пропускаем answer: {e_answer}")
                else:
                    logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка при ответе на callback query: {e_answer}")
        except TelegramBadRequest as e_tbr: # Используем импортированный TelegramBadRequest
            if query.message and "message to edit not found" in str(e_tbr).lower(): 
                logger.warning(f"[{MODULE_NAME_FOR_LOG}] Сообщение для редактирования не найдено, отправка нового: {e_tbr}")
                await bot.send_message(target_chat_id, text, reply_markup=keyboard)
                try:
                    await bot(query.answer())
                except Exception as e_answer:
                    if "query is too old" in str(e_answer).lower() or "query id is invalid" in str(e_answer).lower():
                        logger.debug(f"[{MODULE_NAME_FOR_LOG}] Callback query устарел при fallback: {e_answer}")
                    else:
                        logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка answer при fallback: {e_answer}")
            elif "message is not modified" in str(e_tbr).lower():
                logger.trace(f"[{MODULE_NAME_FOR_LOG}] Сообщение списка ролей не изменено (поймано исключение).")
                try:
                    await bot(query.answer())
                except Exception as e_answer:
                    if "query is too old" in str(e_answer).lower() or "query id is invalid" in str(e_answer).lower():
                        logger.debug(f"[{MODULE_NAME_FOR_LOG}] Callback query устарел: {e_answer}")
            else:
                logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка Telegram BadRequest при редактировании/отправке списка ролей: {e_tbr}")
                try:
                    await bot(query.answer("Ошибка отображения списка.", show_alert=True))
                except Exception as e_answer:
                    if "query is too old" in str(e_answer).lower() or "query id is invalid" in str(e_answer).lower():
                        logger.debug(f"[{MODULE_NAME_FOR_LOG}] Callback query устарел при ошибке: {e_answer}")
                    else:
                        logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка answer при ошибке: {e_answer}")
        except Exception as e_edit:
            logger.error(f"[{MODULE_NAME_FOR_LOG}] Непредвиденная ошибка в cq_admin_roles_list_entry: {e_edit}", exc_info=True)
            try:
                await bot(query.answer("Ошибка отображения списка ролей.", show_alert=True))
            except Exception as e_answer:
                if "query is too old" in str(e_answer).lower() or "query id is invalid" in str(e_answer).lower():
                    logger.debug(f"[{MODULE_NAME_FOR_LOG}] Callback query устарел при непредвиденной ошибке: {e_answer}")
                else:
                    logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка answer при непредвиденной ошибке: {e_answer}")