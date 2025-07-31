# modules/youtube_downloader/utils.py
"""
Утилиты для работы с YouTube
"""

import re
import os
import asyncio
import subprocess
from typing import Optional, Dict, Any, List
from pathlib import Path
import yt_dlp
from loguru import logger

class YouTubeDownloader:
    """Класс для работы с YouTube через yt-dlp"""
    
    # Семафор для ограничения одновременных операций сжатия
    _compression_semaphore = asyncio.Semaphore(1)  # Только одно сжатие одновременно
    
    def __init__(self, download_dir: str = "project_data/downloads/youtube_downloader", user_id: Optional[int] = None):
        self.base_download_dir = Path(download_dir)
        self.user_id = user_id
        
        # Общие папки для кэширования файлов по типам
        self.shared_video_cache_dir = self.base_download_dir / "shared_cache" / "video"
        self.shared_audio_cache_dir = self.base_download_dir / "shared_cache" / "audio"
        self.shared_video_cache_dir.mkdir(parents=True, exist_ok=True)
        self.shared_audio_cache_dir.mkdir(parents=True, exist_ok=True)
        
        if user_id:
            # Создаем персональные папки для пользователя
            self.video_download_dir = self.base_download_dir / f"user_{user_id}" / "video"
            self.audio_download_dir = self.base_download_dir / f"user_{user_id}" / "audio"
        else:
            # Общие папки для случаев без указания пользователя
            self.video_download_dir = self.base_download_dir / "general" / "video"
            self.audio_download_dir = self.base_download_dir / "general" / "audio"
            
        self.video_download_dir.mkdir(parents=True, exist_ok=True)
        self.audio_download_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_user_symlink(self, shared_file_path: Path, video_id: str, file_type: str = "video") -> Path:
        """Создает симлинк в папке пользователя на файл в общем кэше"""
        try:
            # Выбираем правильную папку в зависимости от типа файла
            if file_type == "video":
                user_file_path = self.video_download_dir / shared_file_path.name
            else:  # audio
                user_file_path = self.audio_download_dir / shared_file_path.name
            
            # Если симлинк уже существует, удаляем его
            if user_file_path.exists() or user_file_path.is_symlink():
                user_file_path.unlink()
            
            # Создаем симлинк
            user_file_path.symlink_to(shared_file_path.resolve())
            logger.info(f"📎 Создан симлинк для пользователя {self.user_id}: {user_file_path.name} -> {shared_file_path}")
            
            return user_file_path
            
        except Exception as e:
            logger.error(f"Ошибка создания симлинка: {e}")
            # В случае ошибки, копируем файл
            import shutil
            if file_type == "video":
                user_file_path = self.video_download_dir / shared_file_path.name
            else:  # audio
                user_file_path = self.audio_download_dir / shared_file_path.name
            shutil.copy2(shared_file_path, user_file_path)
            logger.info(f"📋 Скопирован файл для пользователя {self.user_id}: {user_file_path.name}")
            return user_file_path
    
    def _check_shared_cache(self, video_id: str, quality: str, file_type: str = "video") -> Optional[Path]:
        """Проверяет наличие файла в общем кэше с учетом качества"""
        try:
            # Выбираем правильную папку кэша в зависимости от типа файла
            if file_type == "video":
                cache_dir = self.shared_video_cache_dir
                extensions = ['mp4', 'mkv', 'webm']
            else:  # audio
                cache_dir = self.shared_audio_cache_dir
                extensions = ['mp3', 'm4a', 'ogg']
            
            # Ищем файлы с этим video_id - улучшенный поиск с учетом качества
            for ext in extensions:
                # Сначала ищем точное совпадение качества в имени файла
                if quality != "best" and quality != "worst":
                    quality_patterns = [
                        f"*[{video_id}]*{quality}*.{ext}",  # качество в любом месте
                        f"*{quality}*[{video_id}].{ext}",   # качество перед ID
                    ]
                    
                    for pattern in quality_patterns:
                        cached_files = list(cache_dir.glob(pattern))
                        if cached_files:
                            logger.info(f"💾 Найден в кэше с нужным качеством {quality}: {cached_files[0].name}")
                            return cached_files[0]
                
                # Если точное качество не найдено, ищем любые файлы с этим ID
                general_patterns = [
                    f"*[{video_id}].{ext}",     # основной паттерн
                    f"*[{video_id}]*.{ext}",   # с дополнительными символами
                    f"*{video_id}*.{ext}"      # ID в любом месте
                ]
                
                for pattern in general_patterns:
                    cached_files = list(cache_dir.glob(pattern))
                    if cached_files:
                        # Если пользователь запрашивает конкретное качество, а в кэше другое - НЕ используем кэш
                        cached_file = cached_files[0]
                        if quality not in ["best", "worst"] and quality not in cached_file.name.lower():
                            logger.info(f"💾 В кэше найден файл {cached_file.name}, но качество не совпадает с запрошенным {quality}")
                            continue
                        
                        logger.info(f"💾 Найден в кэше: {cached_file.name}")
                        return cached_file
                        
            return None
            
        except Exception as e:
            logger.error(f"Ошибка проверки кэша: {e}")
            return None
    
    def _find_files_in_cache(self, title: str, video_id: str, extensions: List[str], file_type: str = "video") -> List[Path]:
        """Ищет файлы в общем кэше по названию и ID видео"""
        files = []
        
        # Выбираем правильную папку кэша в зависимости от типа файла
        if file_type == "video":
            cache_dir = self.shared_video_cache_dir
        else:  # audio
            cache_dir = self.shared_audio_cache_dir
        
        logger.info(f"🔍 Ищем файлы в кэше: video_id={video_id}, type={file_type}")
        
        if not cache_dir.exists():
            logger.warning(f"⚠️ Папка кэша не существует: {cache_dir}")
            return files
        
        # Ищем по ID видео (более надежно) - исправляем паттерн
        if video_id:
            for ext in extensions:
                # Паттерн для поиска файлов с ID в квадратных скобках
                pattern = f"*[{video_id}].{ext}"
                found_files = list(cache_dir.glob(pattern))
                files.extend(found_files)
                
                # Также пробуем искать без точки перед расширением (для случаев слияния)
                pattern_alt = f"*[{video_id}]{ext}"
                found_files_alt = list(cache_dir.glob(pattern_alt))
                files.extend(found_files_alt)
                
                # Дополнительный паттерн для поиска
                pattern_wide = f"*{video_id}*.{ext}"
                found_files_wide = list(cache_dir.glob(pattern_wide))
                files.extend(found_files_wide)
        
        # Если не найдено по ID, ищем по названию
        if not files and title:
            clean_title = self._clean_filename(title)
            logger.info(f"🔍 Поиск по названию: {clean_title}")
            for ext in extensions:
                pattern = f"*{clean_title}*.{ext}"
                found_files = list(cache_dir.glob(pattern))
                files.extend(found_files)
        
        # Убираем дубликаты и сортируем по времени создания (новые первыми)
        files = list(set(files))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        logger.info(f"🔍 Найдено файлов в кэше: {len(files)}")
        
        return files
    
    def _clean_filename(self, title: str) -> str:
        """Очищает название файла от недопустимых символов"""
        import string
        import unicodedata
        
        # Убираем управляющие символы и нормализуем Unicode
        title = unicodedata.normalize('NFKD', title)
        
        # Заменяем недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        # Убираем лишние пробелы и точки в конце
        title = title.strip(' .')
        
        # Ограничиваем длину (оставляем место для ID видео и расширения)
        if len(title) > 100:
            title = title[:100]
        
        return title
    
    def clean_cache_for_video(self, video_id: str, file_type: str = "video") -> bool:
        """Удаляет все файлы конкретного видео из кэша"""
        try:
            # Выбираем правильную папку кэша
            if file_type == "video":
                cache_dir = self.shared_video_cache_dir
                extensions = ['mp4', 'mkv', 'webm']
            else:  # audio
                cache_dir = self.shared_audio_cache_dir
                extensions = ['mp3', 'm4a', 'ogg']
            
            files_deleted = 0
            
            # Ищем и удаляем все файлы с этим video_id
            for ext in extensions:
                patterns = [
                    f"*[{video_id}].{ext}",     # основной паттерн
                    f"*[{video_id}]*.{ext}",   # с дополнительными символами
                    f"*{video_id}*.{ext}"      # ID в любом месте
                ]
                
                for pattern in patterns:
                    cached_files = list(cache_dir.glob(pattern))
                    for file_path in cached_files:
                        try:
                            file_path.unlink()
                            logger.info(f"🗑️ Удален из кэша: {file_path.name}")
                            files_deleted += 1
                        except Exception as e:
                            logger.warning(f"Не удалось удалить файл из кэша {file_path}: {e}")
            
            logger.info(f"🧹 Очищен кэш для video_id {video_id}: удалено {files_deleted} файлов")
            return files_deleted > 0
            
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша для {video_id}: {e}")
            return False
    
    def clean_low_quality_cache(self) -> int:
        """Удаляет все подозрительно маленькие видео файлы из кэша"""
        try:
            files_deleted = 0
            cache_dir = self.shared_video_cache_dir
            
            if not cache_dir.exists():
                return 0
            
            for file_path in cache_dir.glob("*.mp4"):
                try:
                    file_size_mb = file_path.stat().st_size / (1024*1024)
                    
                    # Подозрительно маленькие файлы для видео (меньше 1 МБ на минуту)
                    if file_size_mb < 10:  # Для видео меньше 10 МБ
                        logger.info(f"🗑️ Удаляем подозрительно маленький файл: {file_path.name} ({file_size_mb:.1f} МБ)")
                        file_path.unlink()
                        files_deleted += 1
                except Exception as e:
                    logger.warning(f"Ошибка при обработке файла {file_path}: {e}")
            
            logger.info(f"🧹 Очищен кэш от низкокачественных файлов: удалено {files_deleted} файлов")
            return files_deleted
            
        except Exception as e:
            logger.error(f"Ошибка при очистке низкокачественного кэша: {e}")
            return 0
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Извлекает ID видео из YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'youtube\.com\/embed\/([0-9A-Za-z_-]{11})',
            r'youtube\.com\/watch\?v=([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """Проверяет, является ли URL валидным YouTube URL"""
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be', 'www.youtu.be'
        ]
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower() in youtube_domains
        except:
            return False
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Получает расширенную информацию о видео без загрузки"""
        try:
            def _extract_info():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    return ydl.extract_info(url, download=False)
            
            # Запускаем в executor чтобы не блокировать event loop
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract_info)
            
            if info:
                # Получаем дату публикации
                upload_date = info.get('upload_date')
                formatted_date = None
                if upload_date:
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(upload_date, '%Y%m%d')
                        formatted_date = date_obj.strftime('%d.%m.%Y')
                    except:
                        formatted_date = upload_date
                
                # Получаем категорию
                categories = info.get('categories', [])
                category = categories[0] if categories else 'Неизвестно'
                
                # Получаем теги
                tags = info.get('tags', [])
                limited_tags = tags[:5] if tags else []  # Ограничиваем до 5 тегов
                
                # Получаем информацию о канале
                channel_url = info.get('channel_url', '')
                channel_subscriber_count = info.get('channel_follower_count', 0)
                
                # Получаем рейтинг
                like_count = info.get('like_count', 0)
                dislike_count = info.get('dislike_count', 0)
                
                # Получаем описание (ограниченное)
                description = info.get('description', '')
                if description and len(description) > 200:
                    description = description[:200] + '...'
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'upload_date': formatted_date,
                    'category': category,
                    'tags': limited_tags,
                    'channel_url': channel_url,
                    'channel_subscriber_count': channel_subscriber_count,
                    'like_count': like_count,
                    'dislike_count': dislike_count,
                    'description': description,
                    'formats': self._extract_formats(info.get('formats', []))
                }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о видео {url}: {e}")
        
        return None
    
    def _extract_formats(self, formats: List[Dict]) -> Dict[str, List[Dict]]:
        """Извлекает доступные форматы видео и аудио"""
        video_formats = []
        audio_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                # Видео с аудио
                video_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': fmt.get('height', 'unknown'),
                    'filesize': fmt.get('filesize'),
                    'format_note': fmt.get('format_note', '')
                })
            elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                # Только аудио
                audio_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': fmt.get('abr', 'unknown'),
                    'filesize': fmt.get('filesize'),
                    'format_note': fmt.get('format_note', '')
                })
        
        return {
            'video': video_formats[:10],  # Ограничиваем количество
            'audio': audio_formats[:5]
        }
    
    async def download_video(self, url: str, quality: str = "best", 
                           progress_callback: Optional[callable] = None, force_download: bool = False) -> Dict[str, Any]:
        """Скачивает видео с YouTube с поддержкой общего кэша"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return {"success": False, "error": "Неверный URL YouTube"}
            
            # Сначала получаем информацию о видео
            def _get_info():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    return ydl.extract_info(url, download=False)
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _get_info)
            
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            view_count = info.get('view_count', 0)
            
            # Проверяем кэш (если не принудительная загрузка)
            if not force_download:
                cached_file = self._check_shared_cache(video_id, quality, "video")
                if cached_file and cached_file.exists():
                    file_size_mb = cached_file.stat().st_size / (1024*1024)
                    logger.info(f"💾 Найден в кэше: {cached_file.name} ({file_size_mb:.1f} МБ)")
                    
                    # Проверяем, подозрительно ли маленький файл для запрошенного качества
                    if duration > 0:
                        expected_min_size = duration * 0.3  # Минимум ~2.4 Мбит/с для 720p
                        if quality == '720p' and file_size_mb < expected_min_size:
                            logger.warning(f"⚠️ Файл в кэше подозрительно маленький для {quality}: {file_size_mb:.1f} МБ")
                            logger.info(f"🔄 Принудительно перезагружаем с новыми настройками качества...")
                            # Удаляем старый файл из кэша
                            self.clean_cache_for_video(video_id, "video")
                        else:
                            # Создаем симлинк в папке пользователя
                            user_file = self._create_user_symlink(cached_file, video_id, "video")
                            
                            return {
                                'success': True,
                                'file_path': str(user_file),
                                'file_size': cached_file.stat().st_size,
                                'title': title,
                                'duration': duration,
                                'uploader': uploader,
                                'view_count': view_count,
                                'quality': quality,
                                'from_cache': True
                            }
            
            # Если принудительная загрузка или файл не найден/не подходит в кэше - загружаем заново
            # Если в кэше нет, загружаем в общий кэш
            format_selector = self._get_format_selector(quality, 'video')
            logger.info(f"📱 Селектор формата для {quality}: {format_selector}")
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': str(self.shared_video_cache_dir / f"%(title)s [{quality}] [%(id)s].%(ext)s"),
                'quiet': False,
                'no_warnings': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'merge_output_format': 'mp4',
                # Упрощенные параметры для стабильной работы
                'writesubtitles': False,
                'writeautomaticsub': False,
                'prefer_free_formats': False,  # Предпочитаем качественные форматы
                'extract_flat': False,
                'force_generic_extractor': False,
                # Параметры для FFmpeg - упрощенные для стабильности
                'postprocessor_args': {
                    'ffmpeg': ['-c', 'copy']  # Просто копируем потоки без перекодирования
                },
                # Добавляем таймауты для предотвращения зависаний
                'socket_timeout': 30,
                'fragment_retries': 3,
                'retries': 3
            }
            
            if progress_callback:
                ydl_opts['progress_hooks'] = [progress_callback]
            
            # Добавляем логирование для отслеживания выбранного формата
            logger.info(f"🎯 Селектор формата для {quality}: {format_selector}")
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Получаем информацию о форматах перед загрузкой
                    try:
                        info = ydl.extract_info(url, download=False)
                        formats = info.get('formats', [])
                        
                        # Логируем доступные форматы для отладки
                        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                        if video_formats:
                            logger.info(f"📊 Доступные видео форматы: {len(video_formats)} шт.")
                            for fmt in video_formats[:5]:  # Показываем первые 5
                                logger.info(f"   - ID: {fmt.get('format_id')}, "
                                          f"{fmt.get('height')}p, "
                                          f"TBR: {fmt.get('tbr', 'unknown')} kbps, "
                                          f"EXT: {fmt.get('ext')}")
                    except Exception as e:
                        logger.warning(f"Не удалось получить информацию о форматах: {e}")
                    
                    return ydl.download([url])
            
            # Добавляем timeout для загрузки (максимум 10 минут)
            try:
                await asyncio.wait_for(
                    loop.run_in_executor(None, _download), 
                    timeout=600  # 10 минут
                )
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout при загрузке видео {url} (более 10 минут)")
                return {"success": False, "error": "Загрузка превысила лимит времени (10 минут)"}
            
            # Поиск загруженного файла в кэше
            cached_files = self._find_files_in_cache(title, video_id, ['mp4', 'mkv', 'webm'], "video")
            
            if not cached_files:
                return {"success": False, "error": "Не удалось найти загруженный файл в кэше"}
            
            cached_file = cached_files[0]
            file_size_mb = cached_file.stat().st_size / (1024*1024)
            
            # Логирование с анализом качества
            logger.info(f"📁 Сохранен в кэш: {cached_file.name}")
            logger.info(f"📦 Размер файла: {file_size_mb:.1f} МБ")
            logger.info(f"📊 Анализ качества: {duration} сек → {file_size_mb:.1f} МБ = {file_size_mb*8/duration:.1f} Мбит/с битрейт" if duration > 0 else f"📊 Размер: {file_size_mb:.1f} МБ")
            
            # Предупреждение о подозрительно маленьком размере
            if duration > 0:
                expected_min_size = duration * 0.3  # Минимум ~2.4 Мбит/с для 720p
                if quality == '720p' and file_size_mb < expected_min_size:
                    logger.warning(f"⚠️ Подозрительно маленький размер для {quality}: {file_size_mb:.1f} МБ (ожидалось >{expected_min_size:.1f} МБ)")
            
            # Создаем симлинк в папке пользователя
            user_file = self._create_user_symlink(cached_file, video_id, "video")
            
            return {
                "success": True,
                "file_path": str(user_file),
                "file_size": cached_file.stat().st_size,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'view_count': view_count,
                'quality': quality,
                'from_cache': False
            }
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке видео {url}: {e}")
            return {"success": False, "error": str(e)}
    
    async def download_audio(self, url: str, quality: str = "best",
                           progress_callback: Optional[callable] = None, force_download: bool = False) -> Dict[str, Any]:
        """Скачивает аудио с YouTube с поддержкой общего кэша"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return {"success": False, "error": "Неверный URL YouTube"}
            
            # Сначала получаем информацию о видео
            def _get_info():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    return ydl.extract_info(url, download=False)
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _get_info)
            
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            # Проверяем кэш
            cached_file = self._check_shared_cache(video_id, quality, "audio")
            if cached_file and cached_file.exists():
                logger.info(f"🎵 Найдено аудио в кэше: {cached_file.name}")
                # Создаем симлинк в папке пользователя
                user_file = self._create_user_symlink(cached_file, video_id, "audio")
                
                return {
                    'success': True,
                    'file_path': str(user_file),
                    'file_size': cached_file.stat().st_size,
                    'title': title,
                    'duration': duration,
                    'uploader': uploader,
                    'quality': quality,
                    'from_cache': True
                }
            
            # Если в кэше нет, загружаем в общий кэш
            # Определяем качество аудио в зависимости от запрошенного
            audio_quality = '320' if quality in ['best', '720p', '1080p'] else '192'
            if quality.isdigit():
                audio_quality = quality
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',  # Предпочитаем качественные форматы
                'outtmpl': str(self.shared_audio_cache_dir / f"%(title)s [{quality}] [%(id)s].%(ext)s"),
                'quiet': True,
                'no_warnings': True,
                'prefer_free_formats': False,  # Предпочитаем качественные форматы
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality,  # Используем высокое качество
                }],
            }
            
            if progress_callback:
                ydl_opts['progress_hooks'] = [progress_callback]
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.download([url])
            
            await loop.run_in_executor(None, _download)
            
            # Поиск загруженного файла в кэше
            cached_files = self._find_files_in_cache(title, video_id, ['mp3', 'm4a', 'ogg'], "audio")
            
            if not cached_files:
                return {"success": False, "error": "Не удалось найти загруженный аудио файл в кэше"}
            
            cached_file = cached_files[0]
            logger.info(f"🎵 Сохранено аудио в кэш: {cached_file.name}")
            
            # Создаем симлинк в папке пользователя
            user_file = self._create_user_symlink(cached_file, video_id, "audio")
            
            return {
                "success": True,
                "file_path": str(user_file),
                "file_size": cached_file.stat().st_size,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'quality': quality,
                'from_cache': False
            }
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке аудио {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_format_selector(self, quality: str, download_type: str) -> str:
        """Возвращает селектор формата для yt-dlp"""
        if download_type == 'video':
            if quality == 'best':
                return 'best[acodec!=none][vcodec!=none]/18'  # Только готовые форматы с аудио+видео
            elif quality == 'worst':
                return 'worst[acodec!=none][vcodec!=none]/18'  # Только готовые форматы с аудио+видео
            elif quality.endswith('p'):
                height = quality[:-1]
                # ИСПРАВЛЕНО: приоритет готовым объединенным форматам для избежания зависаний при слиянии
                if height == '720':
                    # ИСПРАВЛЕНО: Приоритет раздельным высококачественным форматам
                    return (f'232+251/'                                              # Лучший H.264 720p + Opus аудио (по анализу)
                           f'232+140/'                                              # Лучший H.264 720p + AAC аудио  
                           f'136+251/'                                              # H.264 720p (запасной) + Opus аудио
                           f'136+140/'                                              # H.264 720p (запасной) + AAC аудио
                           f'bestvideo[height=720][vbr>=2500]+bestaudio[abr>=128]/' # Высокий битрейт видео + качественное аудио
                           f'bestvideo[height=720]+bestaudio[ext=m4a]/'             # Любой 720p видео + m4a аудио
                           f'best[height=720]')                                     # Готовый формат (last resort)
                elif height == '1080':
                    # ИСПРАВЛЕНО: Приоритет раздельным высококачественным форматам для 1080p
                    return (f'270+251/'                                              # Лучший H.264 1080p + Opus аудио
                           f'270+140/'                                              # Лучший H.264 1080p + AAC аудио
                           f'137+251/'                                              # H.264 1080p (запасной) + Opus аудио
                           f'137+140/'                                              # H.264 1080p (запасной) + AAC аудио
                           f'bestvideo[height=1080][vbr>=3500]+bestaudio[abr>=128]/'# Высокий битрейт видео + качественное аудио
                           f'bestvideo[height=1080]+bestaudio[ext=m4a]/'            # Любой 1080p видео + m4a аудио
                           f'best[height=1080]')                                    # Готовый формат (last resort)
                elif height == '480':
                    # ИСПРАВЛЕНО: Приоритет раздельным форматам для 480p  
                    return (f'231+251/'                                              # Лучший H.264 480p + Opus аудио
                           f'231+140/'                                              # Лучший H.264 480p + AAC аудио
                           f'135+251/'                                              # H.264 480p (запасной) + Opus аудио
                           f'135+140/'                                              # H.264 480p (запасной) + AAC аудио
                           f'bestvideo[height=480][vbr>=1200]+bestaudio[abr>=128]/' # Высокий битрейт видео + качественное аудио
                           f'bestvideo[height=480]+bestaudio[ext=m4a]/'             # Любой 480p видео + m4a аудио
                           f'best[height=480]')                                     # Готовый формат (last resort)
                elif height == '360':
                    return (f'best[height=360][tbr>=800]/'                           # Готовый 360p с высоким битрейтом
                           f'best[height=360]/'                                     # Любой готовый 360p
                           f'bestvideo[height=360]+bestaudio[ext=m4a]')              # 360p + аудио (fallback)
                else:
                    # Для других разрешений
                    return (f'bestvideo[height={height}]+bestaudio[ext=m4a]/'
                           f'best[height={height}]')
            else:
                return 'best[acodec!=none][vcodec!=none]/18'  # Только готовые форматы с аудио+видео
        else:  # audio
            return 'bestaudio[ext=m4a]/bestaudio/best'

    async def compress_video_for_telegram(self, input_path: str, max_size_mb: int = 45) -> Dict[str, Any]:
        """Сжимает видео для отправки через Telegram с размером до max_size_mb МБ"""
        
        # Используем семафор для предотвращения одновременного сжатия
        async with self._compression_semaphore:
            try:
                input_file = Path(input_path)
                if not input_file.exists():
                    return {"success": False, "error": "Исходный файл не найден"}
                
                # Создаем имя для сжатого файла
                compressed_name = f"{input_file.stem}_tg_compressed{input_file.suffix}"
                compressed_path = input_file.parent / compressed_name
                
                # Если сжатый файл уже существует, используем его
                if compressed_path.exists():
                    compressed_size_mb = compressed_path.stat().st_size / (1024*1024)
                    if compressed_size_mb <= max_size_mb + 5:  # небольшой запас
                        logger.info(f"✅ Найден готовый сжатый файл: {compressed_path.name} ({compressed_size_mb:.1f} МБ)")
                        return {
                            "success": True,
                            "file_path": str(compressed_path),
                            "file_size": compressed_path.stat().st_size,
                            "original_size": input_file.stat().st_size,
                            "compression_ratio": (1 - compressed_size_mb / (input_file.stat().st_size / (1024*1024))) * 100
                        }
                
                # Получаем информацию о файле
                file_size_mb = input_file.stat().st_size / (1024*1024)
                
                logger.info(f"🔧 Начинаем сжатие видео: {input_file.name}")
                logger.info(f"📊 Исходный размер: {file_size_mb:.1f} МБ → Целевой: {max_size_mb} МБ")
                logger.info(f"⚠️ Процесс может занять до 10-15 минут...")
                
                # Получаем длительность видео
                def get_video_info():
                    cmd = [
                        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(input_file)
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        import json
                        info = json.loads(result.stdout)
                        duration = float(info.get('format', {}).get('duration', 0))
                        return duration
                    return 600  # fallback 10 минут
                
                duration = await asyncio.get_event_loop().run_in_executor(None, get_video_info)
                
                if duration <= 0:
                    duration = 600  # fallback
                
                # Рассчитываем агрессивный битрейт для достижения цели
                target_size_bits = max_size_mb * 1024 * 1024 * 8
                audio_bitrate_kbps = 96  # уменьшаем аудио битрейт
                video_bitrate_kbps = int((target_size_bits / duration) / 1000) - audio_bitrate_kbps
                
                # Ограничиваем битрейт разумными пределами
                video_bitrate_kbps = max(150, min(video_bitrate_kbps, 1500))
                
                logger.info(f"🎯 Расчетный битрейт видео: {video_bitrate_kbps} kbps (аудио: {audio_bitrate_kbps} kbps)")
                
                # Оптимизированная команда FFmpeg для быстрого и эффективного сжатия
                cmd = [
                    'ffmpeg', '-i', str(input_file),
                    '-c:v', 'libx264',                   # Видео кодек
                    '-preset', 'ultrafast',              # Максимально быстрое сжатие
                    '-crf', '32',                        # Агрессивное сжатие
                    '-b:v', f'{video_bitrate_kbps}k',    # Битрейт видео
                    '-maxrate', f'{video_bitrate_kbps}k', # Строгий лимит битрейта
                    '-bufsize', f'{video_bitrate_kbps//2}k', # Меньший буфер
                    '-c:a', 'aac',                       # Аудио кодек
                    '-b:a', f'{audio_bitrate_kbps}k',    # Битрейт аудио
                    '-ac', '2',                          # Стерео аудио
                    '-ar', '44100',                      # Частота дискретизации
                    '-movflags', '+faststart',           # Быстрый старт
                    '-threads', '4',                     # Ограничиваем количество потоков
                    '-y',                                # Перезаписать файл
                    str(compressed_path)
                ]
                
                def run_compression():
                    return subprocess.run(cmd, capture_output=True, text=True)
                
                logger.info(f"⚙️ Запускаем сжатие (макс. 10 минут)...")
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, run_compression),
                    timeout=600  # 10 минут максимум (уменьшили с 15)
                )
                
                if result.returncode != 0:
                    logger.error(f"❌ Ошибка сжатия: {result.stderr}")
                    return {"success": False, "error": f"Ошибка FFmpeg: {result.stderr[:200]}..."}
                
                # Проверяем результат
                if not compressed_path.exists():
                    return {"success": False, "error": "Сжатый файл не создан"}
                
                compressed_size_mb = compressed_path.stat().st_size / (1024*1024)
                compression_ratio = (file_size_mb - compressed_size_mb) / file_size_mb * 100
                
                logger.info(f"✅ Сжатие завершено!")
                logger.info(f"📦 Новый размер: {compressed_size_mb:.1f} МБ")
                logger.info(f"📉 Сжато на: {compression_ratio:.1f}%")
                
                return {
                    "success": True,
                    "file_path": str(compressed_path),
                    "file_size": compressed_path.stat().st_size,
                    "original_size": input_file.stat().st_size,
                    "compression_ratio": compression_ratio
                }
                
            except asyncio.TimeoutError:
                logger.error("⏰ Timeout при сжатии видео (более 10 минут)")
                return {"success": False, "error": "Сжатие превысило лимит времени (10 минут)"}
            except Exception as e:
                logger.error(f"❌ Ошибка при сжатии видео: {e}")
                return {"success": False, "error": str(e)}

def format_duration(seconds: int) -> str:
    """Форматирует длительность в читаемый вид"""
    if not seconds:
        return "Неизвестно"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    if not size_bytes:
        return "Неизвестно"
    
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ТБ"

def format_count(count: int) -> str:
    """Форматирует большие числа в читаемый вид"""
    if not count:
        return "0"
    
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}млрд"
    elif count >= 1_000_000:
        return f"{count / 1_000_000:.1f}млн"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}тыс"
    else:
        return f"{count:,}"

# Импортируем новую функцию отправки файлов
from .file_sender import send_file_to_user
