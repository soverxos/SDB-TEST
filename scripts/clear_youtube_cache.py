#!/usr/bin/env python3
"""
Скрипт для очистки кэша YouTube загрузчика от низкокачественных файлов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent.parent))

from modules.youtube_downloader.utils import YouTubeDownloader
from loguru import logger

def main():
    """Основная функция для очистки кэша"""
    
    print("🧹 Очистка YouTube кэша от низкокачественных файлов...")
    
    # Создаем экземпляр загрузчика
    downloader = YouTubeDownloader()
    
    print(f"📁 Папка кэша: {downloader.shared_video_cache_dir}")
    
    # Показываем текущее содержимое кэша
    if downloader.shared_video_cache_dir.exists():
        video_files = list(downloader.shared_video_cache_dir.glob("*.mp4"))
        print(f"📊 Найдено видеофайлов в кэше: {len(video_files)}")
        
        for file_path in video_files:
            file_size_mb = file_path.stat().st_size / (1024*1024)
            print(f"  - {file_path.name}: {file_size_mb:.1f} МБ")
    else:
        print("⚠️ Папка кэша не существует")
        return
    
    # Спрашиваем подтверждение
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        confirm = "y"
    else:
        confirm = input("\n🤔 Удалить все файлы размером меньше 10 МБ? (y/N): ")
    
    if confirm.lower() in ['y', 'yes', 'да']:
        deleted_count = downloader.clean_low_quality_cache()
        print(f"✅ Удалено файлов: {deleted_count}")
    else:
        print("❌ Операция отменена")

if __name__ == "__main__":
    main()
