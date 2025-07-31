#!/usr/bin/env python3
"""
Простой HTTP сервер для скачивания файлов YouTube
"""

import os
import uuid
import mimetypes
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio
from aiohttp import web, web_response
from loguru import logger
import urllib.parse

class DownloadServer:
    """Сервер для скачивания файлов"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3000, base_path: str = "/root/SwiftDevBot"):
        self.host = host
        self.port = port
        self.base_path = Path(base_path)
        self.download_tokens: Dict[str, Dict] = {}  # token -> {file_path, expires, filename}
        
    def generate_download_link(self, file_path: str, filename: str = None, expire_hours: int = 24) -> str:
        """Генерирует временную ссылку для скачивания файла"""
        
        # Создаем уникальный токен
        token = str(uuid.uuid4().hex)
        
        # Время истечения
        expires = datetime.now() + timedelta(hours=expire_hours)
        
        # Определяем имя файла
        if not filename:
            filename = Path(file_path).name
        
        # Сохраняем информацию о токене
        self.download_tokens[token] = {
            'file_path': str(file_path),
            'filename': filename,
            'expires': expires,
            'created': datetime.now()
        }
        
        # Генерируем ссылку - используем 100.113.229.67 для Tailscale
        download_url = f"http://100.113.229.67:{self.port}/download/{token}"
        
        logger.info(f"🔗 Создана ссылка для скачивания: {filename}")
        logger.info(f"📅 Срок действия: {expires.strftime('%d.%m.%Y %H:%M')}")
        logger.info(f"🌐 Ссылка: {download_url}")
        
        return download_url
    
    async def handle_download(self, request: web.Request) -> web_response.Response:
        """Обработчик скачивания файла"""
        
        token = request.match_info.get('token')
        
        if not token or token not in self.download_tokens:
            logger.warning(f"❌ Неверный токен: {token}")
            return web.Response(text="Ссылка недействительна или истекла", status=404)
        
        token_info = self.download_tokens[token]
        
        # Проверяем срок действия
        if datetime.now() > token_info['expires']:
            logger.warning(f"⏰ Истек срок действия токена: {token}")
            del self.download_tokens[token]
            return web.Response(text="Ссылка истекла", status=410)
        
        file_path = Path(token_info['file_path'])
        filename = token_info['filename']
        
        # Проверяем существование файла
        if not file_path.exists():
            logger.error(f"📁 Файл не найден: {file_path}")
            return web.Response(text="Файл не найден", status=404)
        
        # Определяем MIME тип
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Кодируем имя файла для заголовка
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        
        file_size = file_path.stat().st_size
        
        logger.info(f"📥 Начинаем скачивание: {filename} ({file_size / (1024*1024):.1f} МБ)")
        
        # Создаем response для скачивания
        response = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': mime_type,
                'Content-Length': str(file_size),
                'Content-Disposition': f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        )
        
        await response.prepare(request)
        
        # Отправляем файл чанками
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB чанки
                    if not chunk:
                        break
                    await response.write(chunk)
            
            logger.info(f"✅ Скачивание завершено: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке файла: {e}")
        
        await response.write_eof()
        return response
    
    async def handle_info(self, request: web.Request) -> web.Response:
        """Информация о сервере"""
        
        active_links = len(self.download_tokens)
        
        info_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SwiftDevBot Download Server</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .stat {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 SwiftDevBot Download Server</h1>
                <p>Сервер для скачивания файлов YouTube</p>
                
                <div class="stat">
                    <strong>📊 Статистика:</strong><br>
                    Активных ссылок: {active_links}<br>
                    Время работы: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
                </div>
                
                <div class="stat">
                    <strong>ℹ️ Информация:</strong><br>
                    • Ссылки действительны 24 часа<br>
                    • Максимальный размер файла: без ограничений<br>
                    • Поддерживаемые форматы: все
                </div>
            </div>
        </body>
        </html>
        """
        
        return web.Response(text=info_html, content_type='text/html')
    
    async def cleanup_expired_tokens(self):
        """Очистка истекших токенов"""
        while True:
            try:
                now = datetime.now()
                expired_tokens = [
                    token for token, info in self.download_tokens.items()
                    if now > info['expires']
                ]
                
                for token in expired_tokens:
                    del self.download_tokens[token]
                
                if expired_tokens:
                    logger.info(f"🧹 Удалено истекших токенов: {len(expired_tokens)}")
                
                # Проверяем каждый час
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Ошибка при очистке токенов: {e}")
                await asyncio.sleep(60)
    
    async def start_server(self):
        """Запускает сервер"""
        
        app = web.Application()
        
        # Маршруты
        app.router.add_get('/download/{token}', self.handle_download)
        app.router.add_get('/', self.handle_info)
        app.router.add_get('/info', self.handle_info)
        
        # Запускаем очистку токенов в фоне
        asyncio.create_task(self.cleanup_expired_tokens())
        
        logger.info(f"🚀 Запуск Download Server на {self.host}:{self.port}")
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"✅ Download Server запущен: http://{self.host}:{self.port}")
        
        return runner

# Глобальный экземпляр сервера
_download_server: Optional[DownloadServer] = None

def get_download_server() -> DownloadServer:
    """Получает глобальный экземпляр сервера"""
    global _download_server
    if _download_server is None:
        _download_server = DownloadServer()
    return _download_server

async def start_download_server_if_needed():
    """Запускает сервер если он еще не запущен"""
    server = get_download_server()
    
    # Проверяем, запущен ли уже сервер
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{server.host}:{server.port}/info', timeout=2) as resp:
                if resp.status == 200:
                    logger.info(f"✅ Download Server уже запущен")
                    return server
    except:
        pass
    
    # Запускаем сервер
    try:
        await server.start_server()
        return server
    except Exception as e:
        logger.error(f"❌ Ошибка запуска Download Server: {e}")
        return None

if __name__ == "__main__":
    async def main():
        server = DownloadServer()
        runner = await server.start_server()
        
        try:
            # Держим сервер запущенным
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Остановка сервера...")
        finally:
            await runner.cleanup()
    
    asyncio.run(main())
