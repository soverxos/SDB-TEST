#!/usr/bin/env python3
"""
Запуск Download Server
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.download_server import DownloadServer
from loguru import logger

async def main():
    """Запуск сервера"""
    
    server = DownloadServer(host="0.0.0.0", port=3000)
    
    logger.info("🚀 Запуск SwiftDevBot Download Server...")
    
    try:
        runner = await server.start_server()
        
        logger.info("✅ Сервер запущен и готов к работе!")
        logger.info("🌐 Доступ: http://localhost:8888")
        logger.info("📋 Для остановки нажмите Ctrl+C")
        
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки...")
    except Exception as e:
        logger.error(f"❌ Ошибка сервера: {e}")
    finally:
        try:
            await runner.cleanup()
            logger.info("✅ Сервер остановлен")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
