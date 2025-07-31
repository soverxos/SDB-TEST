# SwiftDevBot/core/ui/keyboards_core.py

from typing import List, Dict, Optional, TYPE_CHECKING
# Используем нужные типы для Reply клавиатур
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder # Добавляем ReplyKeyboardBuilder
from loguru import logger 

from .callback_data_factories import CoreMenuNavigate, ModuleMenuEntry, CoreServiceAction
from core.rbac.service import PERMISSION_CORE_VIEW_ADMIN_PANEL 
from core.database.core_models import User as DBUser

if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from core.ui.registry_ui import ModuleUIEntry
    from sqlalchemy.ext.asyncio import AsyncSession 

# Обновляем тексты для кнопок, чтобы они были командами или уникальными фразами
TEXTS_CORE_KEYBOARDS_EN = {
    # Для Reply Keyboard (главное меню)
    "main_menu_reply_modules": "🗂 Модули", # Текст, который будет отправлен как сообщение
    "main_menu_reply_profile": "👤 Профиль",
    "main_menu_reply_feedback": "✍️ Обратная связь",
    "main_menu_reply_admin_panel": "🛠 Админ-панель",

    # Для Inline Keyboard (остальные меню)
    "main_menu_inline_modules": "🗂 Modules", # Оставим старые для инлайн, если понадобятся
    "main_menu_inline_profile": "👤 Profile",
    "main_menu_inline_feedback": "✍️ Feedback",
    "main_menu_inline_admin_panel": "🛠 Admin Panel",

    "modules_list_no_modules": "🤷 No modules available",
    "modules_list_title_template": "Available Modules (Page {current_page}/{total_pages}):",
    "pagination_prev": "⬅️ Prev",
    "pagination_next": "Next ➡️",
    "navigation_back_to_main": "🏠 Main Menu", # Может быть и для инлайн, и для reply (как /start)
    "service_delete_message": "❌ Close this menu",
    "confirm_yes": "✅ Yes",
    "confirm_no": "❌ No",
    "welcome_message_title": "🎉 Добро пожаловать в SwiftDevBot!",
    "welcome_message_body": (
        "Я — ваш модульный Telegram-помощник, созданный для расширения функциональности и автоматизации задач.\n\n"
        "🔍 **Что я могу?**\n"
        "Мои возможности зависят от подключенных модулей. Это могут быть инструменты для разработки, утилиты, информационные сервисы и многое другое.\n\n"
        "🔒 **Конфиденциальность:**\n"
        "Я обрабатываю только те данные, которые необходимы для моей работы и работы активных модулей. "
        "Мы ценим вашу приватность. Для получения более подробной информации вы всегда можете обратиться к администратору бота.\n\n"
        "Нажимая «Продолжить», вы соглашаетесь с тем, что бот будет обрабатывать ваши сообщения для предоставления своих функций."
    ),
    "welcome_button_continue": "✅ Продолжить",
    "welcome_button_cancel": "❌ Отмена",
    "registration_cancelled_message": "Очень жаль, что вы передумали. Если надумаете снова, просто напишите /start.",
    "user_middleware_please_register": (
        "👋 Похоже, вы еще не знакомы со мной! "
        "Чтобы начать, пожалуйста, нажмите /start или введите команду /start."
    ),
    "account_deactivated_message": "🚫 Ваш аккаунт был деактивирован. Для получения дополнительной информации, пожалуйста, свяжитесь с администратором.",
    "account_blocked_message": "🚫 Ваш доступ к боту ограничен администратором. Пожалуйста, свяжитесь с поддержкой для уточнения деталей.",
    "profile_title": "👤 Ваш профиль",
    "profile_info_template": (
        "🆔 Ваш Telegram ID: {user_id}\n"
        "📝 Имя: {full_name}\n"
        "👤 Username: @{username}\n"
        "📅 Дата регистрации: {registration_date}\n"
        "🗣 Язык интерфейса: {current_language}"
    ),
    "profile_no_username": "не указан",
    "profile_no_reg_date": "неизвестно",
    "profile_button_change_language": "🌐 Сменить язык", # Это будет инлайн кнопка в профиле
    "profile_select_language_title": "Выберите язык интерфейса:",
}

async def get_main_menu_reply_keyboard( 
    services_provider: 'BotServicesProvider', 
    user_telegram_id: int
) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN 
    
    builder.button(text=texts["main_menu_reply_modules"])
    builder.button(text=texts["main_menu_reply_profile"])
    
    show_admin_button = False
    if user_telegram_id in services_provider.config.core.super_admins:
        show_admin_button = True
    else:
        try:
            async with services_provider.db.get_session() as session: 
                if await services_provider.rbac.user_has_permission(session, user_telegram_id, PERMISSION_CORE_VIEW_ADMIN_PANEL):
                    show_admin_button = True
        except Exception as e: 
            logger.error(f"[MainMenuReplyKeyboard] Ошибка проверки разрешения '{PERMISSION_CORE_VIEW_ADMIN_PANEL}' для {user_telegram_id}: {e}")
            
    if show_admin_button:
        builder.button(text=texts["main_menu_reply_admin_panel"])
        
    builder.button(text=texts["main_menu_reply_feedback"])
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True, 
        input_field_placeholder="Выберите действие из меню..."
    )

async def get_main_menu_inline_keyboard(
    services_provider: 'BotServicesProvider', 
    user_telegram_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN 
    
    builder.button(
        text=texts["main_menu_inline_modules"],
        callback_data=CoreMenuNavigate(target_menu="modules_list", page=1).pack()
    )
    builder.button(
        text=texts["main_menu_inline_profile"],
        callback_data=CoreMenuNavigate(target_menu="profile").pack()
    )
    show_admin_button = False
    if user_telegram_id in services_provider.config.core.super_admins:
        show_admin_button = True
    else:
        try:
            async with services_provider.db.get_session() as session: 
                if await services_provider.rbac.user_has_permission(session, user_telegram_id, PERMISSION_CORE_VIEW_ADMIN_PANEL):
                    show_admin_button = True
        except Exception: pass
            
    if show_admin_button:
        builder.button(
            text=texts["main_menu_inline_admin_panel"],
            callback_data=CoreMenuNavigate(target_menu="admin_panel_main").pack()
        )
    builder.button(
        text=texts["main_menu_inline_feedback"],
        callback_data=CoreMenuNavigate(target_menu="feedback").pack()
    )
    builder.adjust(2) 
    return builder.as_markup()


async def get_modules_list_keyboard(
    services_provider: 'BotServicesProvider',
    user_telegram_id: int, 
    current_page: int = 1,
    items_per_page: int = 5
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN
    
    all_module_ui_entries: List['ModuleUIEntry'] = services_provider.ui_registry.get_all_module_entries()
    
    accessible_module_entries: List['ModuleUIEntry'] = []
    if all_module_ui_entries:
        async with services_provider.db.get_session() as session: 
            for entry in all_module_ui_entries:
                if entry.required_permission_to_view:
                    if await services_provider.rbac.user_has_permission(session, user_telegram_id, entry.required_permission_to_view):
                        accessible_module_entries.append(entry)
                else:
                    accessible_module_entries.append(entry)

    if not accessible_module_entries:
        builder.button(
            text=texts["modules_list_no_modules"],
            callback_data="core:dummy_no_modules"
        )
    else:
        total_items = len(accessible_module_entries)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        total_pages = max(1, total_pages if total_pages > 0 else 1)

        start_index = (current_page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_entries = accessible_module_entries[start_index:end_index]

        for entry in paginated_entries:
            button_text = f"{entry.icon} {entry.display_name}" if entry.icon else entry.display_name
            builder.button(
                text=button_text,
                callback_data=entry.entry_callback_data
            )
        builder.adjust(1)

        if total_pages > 1:
            pagination_buttons_row: List[InlineKeyboardButton] = []
            if current_page > 1:
                pagination_buttons_row.append(InlineKeyboardButton(text=texts["pagination_prev"], callback_data=CoreMenuNavigate(target_menu="modules_list", page=current_page - 1).pack()))
            pagination_buttons_row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="core:dummy_page_indicator"))
            if current_page < total_pages:
                pagination_buttons_row.append(InlineKeyboardButton(text=texts["pagination_next"], callback_data=CoreMenuNavigate(target_menu="modules_list", page=current_page + 1).pack()))
            if pagination_buttons_row:
                 builder.row(*pagination_buttons_row)
    builder.row(
        InlineKeyboardButton(
            text=texts["navigation_back_to_main"], 
            callback_data=CoreMenuNavigate(target_menu="main_reply").pack()
        )
    )
    return builder.as_markup()


def get_welcome_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN
    builder.button(
        text=texts["welcome_button_continue"],
        callback_data=CoreServiceAction(action="confirm_registration").pack()
    )
    builder.button(
        text=texts["welcome_button_cancel"],
        callback_data=CoreServiceAction(action="cancel_registration").pack()
    )
    builder.adjust(2)
    return builder.as_markup()

async def get_profile_menu_keyboard(
    db_user: DBUser, 
    services_provider: 'BotServicesProvider'
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN
    available_langs = services_provider.config.core.i18n.available_locales
    if len(available_langs) > 1:
        builder.button(
            text=texts["profile_button_change_language"],
            callback_data=CoreMenuNavigate(target_menu="profile_change_lang_list").pack()
        )
    if not builder.export():
        builder.button(text="Нет доступных действий в профиле", callback_data="core_profile:dummy_no_actions")
    builder.row(
        InlineKeyboardButton(
            text=texts["navigation_back_to_main"],
            callback_data=CoreMenuNavigate(target_menu="main_reply").pack()
        )
    )
    builder.adjust(1)
    return builder.as_markup()

async def get_language_selection_keyboard(
    current_lang_code: Optional[str],
    available_locales: List[str], 
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lang_code in available_locales:
        prefix = "✅ " if lang_code == current_lang_code else "▫️ "
        display_name = lang_code.upper() 
        builder.button(
            text=f"{prefix}{display_name}",
            callback_data=CoreMenuNavigate(target_menu="profile_set_lang", payload=lang_code).pack()
        )
    builder.adjust(1) 
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад в профиль", 
            callback_data=CoreMenuNavigate(target_menu="profile").pack()
        )
    )
    return builder.as_markup()

def get_confirm_action_keyboard(
    confirm_callback_data: str,
    cancel_callback_data: str,
    confirm_text_key: str = "confirm_yes",
    cancel_text_key: str = "confirm_no"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN
    
    builder.button(text=texts[confirm_text_key], callback_data=confirm_callback_data)
    builder.button(text=texts[cancel_text_key], callback_data=cancel_callback_data)
    builder.adjust(2)
    return builder.as_markup()

def get_close_button_keyboard(
    close_text_key: str = "service_delete_message"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = TEXTS_CORE_KEYBOARDS_EN
    builder.button(
        text=texts[close_text_key],
        callback_data=CoreServiceAction(action="delete_this_message").pack()
    )
    return builder.as_markup()