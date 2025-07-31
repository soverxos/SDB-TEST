# core/admin/users/handlers_list.py
from aiogram import Router, types, F
from aiogram.utils.markdown import hbold
from loguru import logger
from sqlalchemy import select, func as sql_func # <--- ИСПРАВЛЕН ИМПОРТ func

from core.ui.callback_data_factories import AdminUsersPanelNavigate
from .keyboards_users import get_admin_users_list_keyboard_local, USERS_MGMT_TEXTS 
from core.admin.keyboards_admin_common import ADMIN_COMMON_TEXTS 
from core.admin.filters_admin import can_view_admin_panel_filter
from core.rbac.service import PERMISSION_CORE_USERS_VIEW_LIST
from core.database.core_models import User as DBUser

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider

users_list_router = Router(name="sdb_admin_users_list_handlers")
MODULE_NAME_FOR_LOG = "AdminUserList"

#users_list_router.callback_query.filter(can_view_admin_panel_filter)

USERS_PER_PAGE_ADMIN_LOCAL = 10 

@users_list_router.callback_query(AdminUsersPanelNavigate.filter(F.action == "list"))
async def cq_admin_users_list_entry( 
    query: types.CallbackQuery,
    callback_data: AdminUsersPanelNavigate, 
    services_provider: 'BotServicesProvider' 
):
    admin_user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Администратор {admin_user_id} запросил список пользователей, страница: {callback_data.page or 1}")

    async with services_provider.db.get_session() as session: 
        if not services_provider.config.core.super_admins or admin_user_id not in services_provider.config.core.super_admins: 
            if not await services_provider.rbac.user_has_permission(session, admin_user_id, PERMISSION_CORE_USERS_VIEW_LIST):
                await query.answer(ADMIN_COMMON_TEXTS["access_denied"], show_alert=True)
                return
        
        current_page = callback_data.page if callback_data.page is not None else 1
        
        total_users = 0
        try:
            count_stmt = select(sql_func.count(DBUser.id)) 
            total_users_res = await session.execute(count_stmt)
            total_users = total_users_res.scalar_one_or_none() or 0
        except Exception as e_count:
            logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка подсчета пользователей: {e_count}")
            await query.answer("Ошибка получения данных о пользователях.", show_alert=True)
            return
        
        total_pages = (total_users + USERS_PER_PAGE_ADMIN_LOCAL - 1) // USERS_PER_PAGE_ADMIN_LOCAL
        total_pages = max(1, total_pages) 
        current_page = max(1, min(current_page, total_pages))
        offset = (current_page - 1) * USERS_PER_PAGE_ADMIN_LOCAL

        stmt_users = (
            select(DBUser)
            .order_by(DBUser.id.desc()) 
            .limit(USERS_PER_PAGE_ADMIN_LOCAL)
            .offset(offset)
        )
        users_result = await session.execute(stmt_users)
        users_on_page: List[DBUser] = list(users_result.scalars().all())

        text = USERS_MGMT_TEXTS["user_list_title_template"].format(current_page=current_page, total_pages=total_pages)
        if total_users == 0 : 
             text = "👥 Пользователи\n\nВ базе данных нет зарегистрированных пользователей."

        keyboard = await get_admin_users_list_keyboard_local(users_on_page, total_pages, current_page)

        if query.message:
            try:
                if query.message.text != text or query.message.reply_markup != keyboard:
                    await query.message.edit_text(text, reply_markup=keyboard)
                else:
                    logger.trace(f"[{MODULE_NAME_FOR_LOG}] Сообщение списка пользователей не изменено.")
                await query.answer()
            except types.TelegramBadRequest as e_tbr:
                if "message is not modified" in str(e_tbr).lower():
                    logger.trace(f"[{MODULE_NAME_FOR_LOG}] Сообщение списка пользователей не изменено (поймано исключение).")
                    await query.answer()
                else:
                    logger.warning(f"[{MODULE_NAME_FOR_LOG}] Ошибка редактирования списка пользователей: {e_tbr}")
                    await query.answer() 
            except Exception as e_edit:
                logger.error(f"[{MODULE_NAME_FOR_LOG}] Непредвиденная ошибка в cq_admin_users_list_entry: {e_edit}", exc_info=True)
                await query.answer(ADMIN_COMMON_TEXTS["error_general"], show_alert=True)