# modules/youtube_downloader/models.py
"""
Модели базы данных для модуля YouTube Downloader
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database.base import Base
import enum

class DownloadType(enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"

class DownloadStatus(enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

class YouTubeDownload(Base):
    """Модель для истории загрузок YouTube"""
    __tablename__ = "youtube_downloads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # Информация о видео
    url = Column(String(500), nullable=False)
    video_id = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=True)  # в секундах
    
    # Параметры загрузки
    format_type = Column(String(10), nullable=False)
    quality = Column(String(20), nullable=False)
    
    # Статус и результат
    status = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)  # в байтах
    error_message = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(), nullable=False)
    completed_at = Column(DateTime(), nullable=True)
    
    # Дополнительное поле для совместимости с обработчиками
    started_at = None  # Динамическое поле, не сохраняется в БД
    
    def __repr__(self):
        return f"<YouTubeDownload(id={self.id}, user={self.user_id}, title='{self.title}', status={self.status})>"
