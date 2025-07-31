# modules/youtube_downloader/keyboards.py
"""
Клавиатуры для модуля YouTube Downloader
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import TYPE_CHECKING, Optional, Dict, Any

from .callback_data import YouTubeAction
from core.ui.callback_data_factories import CoreMenuNavigate
from .permissions import (
    PERM_DOWNLOAD_VIDEO,
    PERM_DOWNLOAD_AUDIO,
    PERM_VIEW_HISTORY
)

if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession

async def get_youtube_main_menu_keyboard(
    services_provider: 'BotServicesProvider',
    user_id: int,
    session: 'AsyncSession'
) -> InlineKeyboardMarkup:
    """Главное меню модуля YouTube Downloader"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка загрузки видео
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_DOWNLOAD_VIDEO):
        builder.button(
            text="📺 Скачать видео",
            callback_data=YouTubeAction(action="start_video_download").pack()
        )
    
    # Кнопка загрузки аудио
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_DOWNLOAD_AUDIO):
        builder.button(
            text="🎵 Скачать аудио",
            callback_data=YouTubeAction(action="start_audio_download").pack()
        )
    
    # История загрузок
    if await services_provider.rbac.user_has_permission(session, user_id, PERM_VIEW_HISTORY):
        builder.button(
            text="📋 История загрузок",
            callback_data=YouTubeAction(action="view_history", page=1).pack()
        )
    
    # Если нет доступных действий
    if not builder.export():
        builder.button(
            text="🤷‍♂️ Для вас нет доступных действий",
            callback_data=YouTubeAction(action="no_actions").pack()
        )
    
    # Кнопка "Назад к модулям"
    builder.button(
        text="⬅️ Назад к модулям",
        callback_data=CoreMenuNavigate(target_menu="modules_list").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_url_input_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для этапа ввода URL"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="⬅️ Назад в меню",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_video_quality_keyboard(video_info: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Клавиатура выбора качества видео"""
    builder = InlineKeyboardBuilder()
    
    # Предустановленные качества
    qualities = ["720p", "480p", "360p", "best", "worst"]
    
    for quality in qualities:
        builder.button(
            text=f"📹 {quality}",
            callback_data=YouTubeAction(
                action="download_video_quality",
                quality=quality
            ).pack()
        )
    
    # Кнопка "Назад в главное меню"
    builder.button(
        text="⬅️ Назад",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_audio_quality_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора качества аудио"""
    builder = InlineKeyboardBuilder()
    
    # Качества аудио
    qualities = [
        ("🎵 Высокое (320kbps)", "320"),
        ("🎵 Среднее (192kbps)", "192"),
        ("🎵 Низкое (128kbps)", "128"),
        ("🎵 Лучшее доступное", "best")
    ]
    
    for text, quality in qualities:
        builder.button(
            text=text,
            callback_data=YouTubeAction(
                action="download_audio_quality",
                quality=quality
            ).pack()
        )
    
    # Кнопка "Назад в главное меню"
    builder.button(
        text="⬅️ Назад",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_download_confirmation_keyboard(download_type: str, quality: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения загрузки"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="✅ Подтвердить загрузку",
        callback_data=YouTubeAction(
            action="confirm_download",
            format_type=download_type,
            quality=quality
        ).pack()
    )
    
    builder.button(
        text="🔄 Выбрать другое качество",
        callback_data=YouTubeAction(
            action=f"start_{download_type}_download"
        ).pack()
    )
    
    builder.button(
        text="⬅️ Назад в меню",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_download_complete_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру после завершения загрузки"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📋 Перейти к истории загрузок",
        callback_data=YouTubeAction(action="view_history", page=1).pack()
    )
    
    builder.button(
        text="🏠 Главное меню модуля",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_history_keyboard(page: int = 1, has_next: bool = False, has_prev: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для истории загрузок"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_buttons = []
    if has_prev:
        nav_buttons.append(("⬅️ Назад", YouTubeAction(action="view_history", page=page-1).pack()))
    
    if has_next:
        nav_buttons.append(("Вперед ➡️", YouTubeAction(action="view_history", page=page+1).pack()))
    
    for text, callback_data in nav_buttons:
        builder.button(text=text, callback_data=callback_data)
    
    # Кнопка обновления
    builder.button(
        text="🔄 Обновить",
        callback_data=YouTubeAction(action="view_history", page=page).pack()
    )
    
    # Кнопка "Назад к главному меню"
    builder.button(
        text="⬅️ Главное меню",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    if nav_buttons:
        builder.adjust(len(nav_buttons), 1, 1)
    else:
        builder.adjust(1)
    
    return builder.as_markup()

def get_history_with_download_keyboard(download_id: int, page: int = 1, has_next: bool = False, has_prev: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для истории загрузок с кнопкой отправки файла"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка отправки файла
    builder.button(
        text="📤 Отправить файл",
        callback_data=YouTubeAction(action="send_file", item_id=download_id).pack()
    )
    
    # Кнопки навигации
    nav_buttons = []
    if has_prev:
        nav_buttons.append(("⬅️ Назад", YouTubeAction(action="view_history", page=page-1).pack()))
    
    if has_next:
        nav_buttons.append(("Вперед ➡️", YouTubeAction(action="view_history", page=page+1).pack()))
    
    for text, callback_data in nav_buttons:
        builder.button(text=text, callback_data=callback_data)
    
    # Кнопка обновления
    builder.button(
        text="🔄 Обновить",
        callback_data=YouTubeAction(action="view_history", page=page).pack()
    )
    
    # Кнопка "Назад к главному меню"
    builder.button(
        text="⬅️ Главное меню",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    if nav_buttons:
        builder.adjust(1, len(nav_buttons), 1, 1)
    else:
        builder.adjust(1, 1, 1)
    
    return builder.as_markup()

def get_download_item_keyboard(download_id: int, status: str) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного элемента загрузки"""
    builder = InlineKeyboardBuilder()
    
    if status == "completed":
        builder.button(
            text="📱 Отправить файл",
            callback_data=YouTubeAction(action="send_file", item_id=download_id).pack()
        )
    
    if status in ["failed", "completed"]:
        builder.button(
            text="🗑️ Удалить",
            callback_data=YouTubeAction(action="delete_download", item_id=download_id).pack()
        )
    
    builder.button(
        text="⬅️ К истории",
        callback_data=YouTubeAction(action="view_history", page=1).pack()
    )
    
    builder.adjust(1)
    return builder.as_markup()
