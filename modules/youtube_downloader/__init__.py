# modules/youtube_downloader/__init__.py
"""
YouTube Downloader Module for SwiftDevBot

Модуль для скачивания видео и аудио с YouTube.
"""

from .handlers import youtube_router
from .permissions import (
    PERM_ACCESS_USER_FEATURES,
    PERM_DOWNLOAD_VIDEO,
    PERM_DOWNLOAD_AUDIO,
    PERM_VIEW_HISTORY,
    PERM_ADMIN_MANAGE
)
from .setup_module import setup_module

__all__ = [
    "youtube_router",
    "setup_module",
    "PERM_ACCESS_USER_FEATURES",
    "PERM_DOWNLOAD_VIDEO", 
    "PERM_DOWNLOAD_AUDIO",
    "PERM_VIEW_HISTORY",
    "PERM_ADMIN_MANAGE"
]
