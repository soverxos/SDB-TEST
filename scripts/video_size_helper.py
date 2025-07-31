#!/usr/bin/env python3
"""
Быстрая утилита для решения проблемы больших видео файлов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.youtube_downloader.utils import YouTubeDownloader
from loguru import logger

def main():
    """Предлагает альтернативы для большого видео файла"""
    
    logger.info("🎬 Анализ проблемы с размером файла...")
    
    # Находим большой файл
    downloader = YouTubeDownloader()
    video_cache_dir = downloader.shared_video_cache_dir
    
    large_files = []
    for file_path in video_cache_dir.glob("*.mp4"):
        file_size_mb = file_path.stat().st_size / (1024*1024)
        if file_size_mb > 50:
            large_files.append((file_path, file_size_mb))
    
    if not large_files:
        logger.info("✅ Файлов больше 50 МБ не найдено")
        return
    
    # Сортируем по размеру (большие первыми)
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"🔍 Найдено {len(large_files)} больших файлов:")
    
    for i, (file_path, file_size_mb) in enumerate(large_files, 1):
        logger.info(f"\n📁 {i}. {file_path.name}")
        logger.info(f"📦 Размер: {file_size_mb:.1f} МБ")
        
        print(f"\n🎯 Рекомендации для файла '{file_path.name}':")
        print(f"📊 Текущий размер: {file_size_mb:.1f} МБ (лимит Telegram: 50 МБ)")
        print()
        print("💡 Варианты решения:")
        print("1. 🎵 Скачать только аудио (обычно 3-10 МБ)")
        print("2. 📱 Скачать в более низком качестве (360p или 480p)")  
        print("3. 🔧 Сжать видео (может занять 10-15 минут)")
        print("4. 💾 Сохранить как есть (доступно в истории загрузок)")
        print("5. 🗑️ Удалить файл из кэша")
        print()
        
        # Показываем команды для каждого варианта
        video_id = None
        for part in file_path.name.split('['):
            if len(part) == 12 and part.endswith(']'):
                video_id = part[:-1]
                break
        
        if video_id:
            print("📋 Команды для выполнения:")
            print(f"   Аудио:      python3 -c \"from modules.youtube_downloader.utils import *; import asyncio; d=YouTubeDownloader(); asyncio.run(d.download_audio('https://youtu.be/{video_id}'))\"")
            print(f"   360p:       python3 -c \"from modules.youtube_downloader.utils import *; import asyncio; d=YouTubeDownloader(); asyncio.run(d.download_video('https://youtu.be/{video_id}', '360p'))\"")
            print(f"   Сжатие:     python3 scripts/compress_video_for_telegram.py \"{file_path}\"")
            print(f"   Удаление:   rm \"{file_path}\"")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    main()
