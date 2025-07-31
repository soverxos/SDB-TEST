# modules/youtube_downloader/callback_data.py
"""
Callback data factories для модуля YouTube Downloader
"""

from aiogram.filters.callback_data import CallbackData
from typing import Optional

class YouTubeAction(CallbackData, prefix="youtube"):
    """Callback для действий с YouTube"""
    action: str  # main_menu, url_input, view_history, download_file, clear_history, confirm_clear, delete_file, confirm_delete
    item_id: Optional[int] = None
    page: Optional[int] = None
    format_type: Optional[str] = None  # video, audio
    quality: Optional[str] = None  # 720p, 480p, best, worst
