# core/admin/logs_viewer/handlers_logs.py
from aiogram import Router, types, F
from loguru import logger

from core.ui.callback_data_factories import AdminMainMenuNavigate 
from core.admin.filters_admin import can_view_admin_panel_filter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider

logs_viewer_router = Router(name="sdb_admin_logs_viewer_handlers")
MODULE_NAME_FOR_LOG = "AdminLogsViewer"

#logs_viewer_router.callback_query.filter(can_view_admin_panel_filter)

@logs_viewer_router.callback_query(AdminMainMenuNavigate.filter(F.target_section == "logs_view"))
async def cq_admin_logs_view_start(
    query: types.CallbackQuery,
    services_provider: 'BotServicesProvider'
):
    admin_user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Администратор {admin_user_id} запросил просмотр логов (раздел в разработке).")
    await query.answer("Раздел просмотра логов находится в разработке.", show_alert=True)