#!/usr/bin/env python3
"""
Утилита для сжатия видео файлов до размера подходящего для Telegram
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.youtube_downloader.utils import YouTubeDownloader
from loguru import logger

async def compress_video_file(input_path: str, max_size_mb: int = 45):
    """Сжимает видео файл до указанного размера"""
    
    # Создаем экземпляр downloader для использования метода сжатия
    downloader = YouTubeDownloader()
    
    input_file = Path(input_path)
    if not input_file.exists():
        logger.error(f"❌ Файл не найден: {input_path}")
        return False
    
    file_size_mb = input_file.stat().st_size / (1024*1024)
    logger.info(f"🎬 Исходный файл: {input_file.name}")
    logger.info(f"📦 Размер: {file_size_mb:.1f} МБ")
    
    if file_size_mb <= max_size_mb:
        logger.info(f"✅ Файл уже подходящего размера для Telegram ({file_size_mb:.1f} МБ <= {max_size_mb} МБ)")
        return True
    
    logger.info(f"🔧 Начинаем сжатие до {max_size_mb} МБ...")
    
    result = await downloader.compress_video_for_telegram(input_path, max_size_mb)
    
    if result["success"]:
        compressed_size_mb = result["file_size"] / (1024*1024)
        compression_ratio = result["compression_ratio"]
        
        logger.info(f"✅ Сжатие завершено!")
        logger.info(f"📁 Сжатый файл: {result['file_path']}")
        logger.info(f"📦 Новый размер: {compressed_size_mb:.1f} МБ")
        logger.info(f"📉 Сжато на: {compression_ratio:.1f}%")
        
        if compressed_size_mb <= 50:
            logger.info(f"🎯 Файл готов для отправки через Telegram!")
        else:
            logger.warning(f"⚠️ Файл все еще большой для Telegram: {compressed_size_mb:.1f} МБ")
        
        return True
    else:
        logger.error(f"❌ Ошибка сжатия: {result['error']}")
        return False

async def compress_all_videos_in_directory(directory: str, max_size_mb: int = 45):
    """Сжимает все видео файлы в указанной директории"""
    
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.error(f"❌ Директория не найдена: {directory}")
        return
    
    # Поддерживаемые видео форматы
    video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov']
    
    video_files = []
    for ext in video_extensions:
        video_files.extend(dir_path.glob(f"*{ext}"))
    
    if not video_files:
        logger.info(f"📁 В директории {directory} не найдено видео файлов")
        return
    
    logger.info(f"🎬 Найдено {len(video_files)} видео файлов")
    
    success_count = 0
    for video_file in video_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 Обрабатываем: {video_file.name}")
        
        if await compress_video_file(str(video_file), max_size_mb):
            success_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Обработано успешно: {success_count}/{len(video_files)} файлов")

def main():
    """Главная функция"""
    
    if len(sys.argv) < 2:
        print("📋 Использование:")
        print(f"  {sys.argv[0]} <путь_к_файлу_или_папке> [макс_размер_МБ]")
        print()
        print("🎯 Примеры:")
        print(f"  {sys.argv[0]} /path/to/video.mp4")
        print(f"  {sys.argv[0]} /path/to/video.mp4 40")
        print(f"  {sys.argv[0]} /path/to/directory/")
        print()
        print("📝 По умолчанию максимальный размер: 45 МБ")
        sys.exit(1)
    
    target_path = sys.argv[1]
    max_size_mb = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    
    logger.info(f"🚀 Запуск сжатия для: {target_path}")
    logger.info(f"🎯 Максимальный размер: {max_size_mb} МБ")
    
    # Проверяем, что ffmpeg доступен
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info(f"✅ FFmpeg найден")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(f"❌ FFmpeg не найден! Установите ffmpeg для сжатия видео")
        sys.exit(1)
    
    if Path(target_path).is_file():
        # Сжимаем один файл
        asyncio.run(compress_video_file(target_path, max_size_mb))
    elif Path(target_path).is_dir():
        # Сжимаем все файлы в директории
        asyncio.run(compress_all_videos_in_directory(target_path, max_size_mb))
    else:
        logger.error(f"❌ Путь не найден: {target_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
