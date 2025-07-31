# modules/youtube_downloader/permissions.py
"""
Разрешения для модуля YouTube Downloader
"""

# Базовые разрешения
PERM_ACCESS_USER_FEATURES = "youtube_downloader.access_user_features"
PERM_DOWNLOAD_VIDEO = "youtube_downloader.download_video"  
PERM_DOWNLOAD_AUDIO = "youtube_downloader.download_audio"
PERM_VIEW_HISTORY = "youtube_downloader.view_history"
PERM_ADMIN_MANAGE = "youtube_downloader.admin_manage"

# Список всех разрешений для экспорта
ALL_PERMISSIONS = [
    PERM_ACCESS_USER_FEATURES,
    PERM_DOWNLOAD_VIDEO,
    PERM_DOWNLOAD_AUDIO, 
    PERM_VIEW_HISTORY,
    PERM_ADMIN_MANAGE
]
