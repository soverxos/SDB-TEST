# modules/youtube_downloader/web_server.py
"""
Простой веб-сервер для скачивания файлов через браузер
"""

import os
import asyncio
from pathlib import Path
from aiohttp import web, hdrs
from aiohttp.web_response import StreamResponse
import mimetypes
from loguru import logger
import time
import hashlib


class FileDownloadServer:
    """Простой веб-сервер для скачивания файлов"""
    
    def __init__(self, host="0.0.0.0", port=8080, external_host=None, external_port=None, use_https=True):
        self.host = host
        self.port = port
        self.external_host = external_host or "sdb.soverx.top"  # Внешний домен
        self.external_port = external_port or (443 if use_https else 80)  # HTTPS/HTTP порт
        self.use_https = use_https
        self.app = None
        self.runner = None
        self.site = None
        self.download_tokens = {}  # token -> {file_path, expires_at, filename}
        
    async def start(self):
        """Запускает веб-сервер"""
        try:
            self.app = web.Application()
            
            # Добавляем маршруты
            self.app.router.add_get('/download/{token}', self.handle_download)
            self.app.router.add_get('/info', self.handle_info)
            self.app.router.add_get('/', self.handle_root)
            
            # Запускаем сервер
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"📡 Веб-сервер для скачивания запущен: http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
            return False
    
    async def stop(self):
        """Останавливает веб-сервер"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("🔴 Веб-сервер остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка остановки веб-сервера: {e}")
    
    def get_external_url(self, token: str) -> str:
        """Генерирует внешний URL для скачивания"""
        protocol = "https" if self.use_https else "http"
        
        # Если используем стандартные порты (80/443), не указываем порт в URL
        if (self.use_https and self.external_port == 443) or (not self.use_https and self.external_port == 80):
            return f"{protocol}://{self.external_host}/download/{token}"
        else:
            return f"{protocol}://{self.external_host}:{self.external_port}/download/{token}"
    
    def generate_download_token(self, file_path: str, filename: str = None, expire_hours: int = 24) -> str:
        """Генерирует токен для скачивания файла"""
        try:
            # Создаем уникальный токен
            token_data = f"{file_path}_{int(time.time())}_{os.urandom(8).hex()}"
            token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
            
            # Время истечения токена
            expires_at = time.time() + (expire_hours * 3600)
            
            # Определяем имя файла
            if not filename:
                filename = os.path.basename(file_path)
            
            # Сохраняем токен
            self.download_tokens[token] = {
                'file_path': file_path,
                'expires_at': expires_at,
                'filename': filename
            }
            
            # Очищаем старые токены
            self._cleanup_expired_tokens()
            
            logger.info(f"🔗 Создан токен для скачивания: {filename} (действует {expire_hours}ч)")
            
            return token
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания токена: {e}")
            return None
    
    def _cleanup_expired_tokens(self):
        """Удаляет истекшие токены"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.download_tokens.items()
            if data['expires_at'] < current_time
        ]
        
        for token in expired_tokens:
            del self.download_tokens[token]
        
        if expired_tokens:
            logger.info(f"🧹 Удалено {len(expired_tokens)} истекших токенов")
    
    async def handle_root(self, request):
        """Главная страница"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SwiftDevBot - Скачивание файлов</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .header { text-align: center; color: #333; }
                .info { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .code { background: #000; color: #0f0; padding: 10px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 SwiftDevBot</h1>
                <h2>📥 Сервер скачивания файлов</h2>
            </div>
            
            <div class="info">
                <h3>ℹ️ Информация</h3>
                <p>Этот сервер предназначен для скачивания больших видео файлов из YouTube через Telegram бота.</p>
                <p>Для скачивания файла используйте ссылку из бота с токеном доступа.</p>
            </div>
            
            <div class="info">
                <h3>🔗 Формат ссылки</h3>
                <div class="code">http://sdb.soverx.top:8080/download/TOKEN</div>
                <p><small>Токены действительны 24 часа</small></p>
                <p><small>⚠️ Требуется доступ к Tailscale сети</small></p>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html', charset='utf-8')
    
    async def handle_info(self, request):
        """Информация о сервере"""
        info = {
            'status': 'running',
            'active_tokens': len(self.download_tokens),
            'server': 'SwiftDevBot Download Server',
            'version': '1.0'
        }
        return web.json_response(info)
    
    async def handle_download(self, request):
        """Обработка скачивания файла"""
        try:
            token = request.match_info['token']
            
            # Очищаем истекшие токены
            self._cleanup_expired_tokens()
            
            # Проверяем токен
            if token not in self.download_tokens:
                return web.Response(
                    text="❌ Неверный или истекший токен доступа",
                    status=404,
                    content_type='text/plain', charset='utf-8'
                )
            
            token_data = self.download_tokens[token]
            file_path = token_data['file_path']
            filename = token_data['filename']
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return web.Response(
                    text="❌ Файл не найден на сервере",
                    status=404,
                    content_type='text/plain', charset='utf-8'
                )
            
            # Получаем информацию о файле
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024*1024)
            
            # Определяем MIME-тип
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            logger.info(f"📥 Начинается скачивание: {filename} ({file_size_mb:.1f} МБ)")
            
            # Обработка Range запросов для больших файлов
            range_header = request.headers.get('Range')
            start = 0
            end = file_size - 1
            
            if range_header:
                # Парсим Range: bytes=start-end
                range_match = range_header.replace('bytes=', '').split('-')
                if len(range_match) == 2:
                    if range_match[0]:
                        start = int(range_match[0])
                    if range_match[1]:
                        end = int(range_match[1])
                    
                    logger.info(f"📊 Range запрос: байты {start}-{end} из {file_size}")
            
            content_length = end - start + 1
            
            # Создаем потоковый ответ
            status = 206 if range_header else 200
            headers = {
                hdrs.CONTENT_TYPE: mime_type,
                hdrs.CONTENT_DISPOSITION: f'attachment; filename="{filename}"',
                hdrs.CONTENT_LENGTH: str(content_length),
                hdrs.ACCEPT_RANGES: 'bytes'
            }
            
            if range_header:
                headers[hdrs.CONTENT_RANGE] = f'bytes {start}-{end}/{file_size}'
            
            response = StreamResponse(status=status, headers=headers)
            
            await response.prepare(request)
            
            # Отправляем файл по частям (увеличенный размер для больших файлов)
            chunk_size = 1024 * 1024  # 1MB chunks для стабильной передачи больших файлов
            bytes_sent = 0
            
            with open(file_path, 'rb') as f:
                f.seek(start)
                bytes_to_read = content_length
                bytes_sent = 0
                
                while bytes_to_read > 0:
                    try:
                        # Читаем либо размер чанка, либо оставшиеся байты
                        current_chunk_size = min(chunk_size, bytes_to_read)
                        chunk = f.read(current_chunk_size)
                        
                        if not chunk:
                            break
                            
                        await response.write(chunk)
                        bytes_sent += len(chunk)
                        bytes_to_read -= len(chunk)
                        
                        # Логируем прогресс для больших файлов (>10MB)
                        if file_size_mb > 10 and bytes_sent % (5 * 1024 * 1024) == 0:
                            progress = (bytes_sent / content_length) * 100
                            logger.info(f"📊 Прогресс передачи: {progress:.1f}% ({bytes_sent / (1024*1024):.1f} МБ из {content_length / (1024*1024):.1f} МБ)")
                            
                    except ConnectionResetError:
                        logger.warning(f"⚠️ Соединение сброшено клиентом на {bytes_sent / (1024*1024):.1f} МБ из {content_length / (1024*1024):.1f} МБ")
                        return response
                    except Exception as chunk_error:
                        logger.error(f"❌ Ошибка при отправке чанка: {chunk_error}")
                        return response
            
            await response.write_eof()
            
            logger.info(f"✅ Скачивание завершено: {filename}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании: {e}")
            return web.Response(
                text=f"❌ Ошибка сервера: {str(e)}",
                status=500,
                content_type='text/plain', charset='utf-8'
            )


# Глобальный экземпляр сервера
_download_server = None


async def get_download_server():
    """Получает экземпляр сервера скачивания"""
    global _download_server
    if _download_server is None:
        _download_server = FileDownloadServer(
            host="0.0.0.0", 
            port=8080,
            external_host="sdb.soverx.top",
            external_port=8080,    # Используем тот же порт 8080
            use_https=False        # HTTP для прямого соединения
        )
    return _download_server


async def start_download_server_if_needed():
    """Запускает сервер если он еще не запущен"""
    try:
        server = await get_download_server()
        
        # Проверяем, запущен ли уже сервер
        if server.runner is None:
            success = await server.start()
            if success:
                logger.info("✅ Веб-сервер для скачивания готов к работе")
                return server
            else:
                logger.error("❌ Не удалось запустить веб-сервер")
                return None
        else:
            logger.info("ℹ️ Веб-сервер уже запущен")
            return server
            
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске веб-сервера: {e}")
        return None


async def stop_download_server():
    """Останавливает сервер скачивания"""
    global _download_server
    if _download_server:
        await _download_server.stop()
        _download_server = None
