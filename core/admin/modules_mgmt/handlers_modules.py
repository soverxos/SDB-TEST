# core/admin/modules_mgmt/handlers_modules.py
from aiogram import Router, types, F
from loguru import logger

from core.ui.callback_data_factories import AdminModulesPanelNavigate # Пример
from core.admin.filters_admin import can_view_admin_panel_filter
# from .keyboards_modules import ...

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider

modules_mgmt_router = Router(name="sdb_admin_modules_mgmt_handlers")
MODULE_NAME_FOR_LOG = "AdminModulesMgmt"

#modules_mgmt_router.callback_query.filter(can_view_admin_panel_filter)

@modules_mgmt_router.callback_query(AdminModulesPanelNavigate.filter(F.action == "list"))
async def cq_admin_modules_list_stub(
    query: types.CallbackQuery,
    callback_data: AdminModulesPanelNavigate, 
    services_provider: 'BotServicesProvider'
):
    logger.info(f"[{MODULE_NAME_FOR_LOG}] Заглушка для списка модулей вызвана.")
    await query.answer("Раздел управления модулями в разработке.", show_alert=True)