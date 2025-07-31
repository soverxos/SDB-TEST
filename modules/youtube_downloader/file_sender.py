# modules/youtube_downloader/file_sender.py
"""
Модуль для отправки файлов пользователям
"""

import os
from typing import Dict, Any
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loguru import logger


async def handle_download_help_callback(callback_query: CallbackQuery) -> None:
    """Обработчик кнопки помощи по скачиванию"""
    help_text = (
        "📋 **Инструкция по скачиванию больших файлов**\n\n"
        "🌐 **Через браузер (рекомендуется):**\n"
        "• Просто нажмите на ссылку для скачивания\n"
        "• Работает на компьютере, телефоне, планшете\n"
        "• Файл загрузится автоматически\n\n"
        "📱 **На мобильном устройстве:**\n"
        "• Нажмите на ссылку или кнопку\n"
        "• Выберите папку для сохранения\n"
        "• Дождитесь завершения загрузки\n\n"
        "💻 **На компьютере:**\n"
        "• Кликните правой кнопкой → 'Сохранить как...'\n"
        "• Или просто нажмите на ссылку\n\n"
        "⏰ **Важно:**\n"
        "• Ссылка действительна 24 часа\n"
        "• Файл в оригинальном качестве (без сжатия)\n"
        "• Если ссылка не работает, запросите файл заново"
    )
    
    await callback_query.message.edit_text(
        text=help_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="↩️ Назад", 
                callback_data="back_to_download"
            )]
        ])
    )
    
    await callback_query.answer()


async def send_file_to_user(bot, user_id: int, file_path: str, title: str, file_size: int) -> Dict[str, Any]:
    """
    Отправляет файл пользователю через Telegram или создает ссылку для скачивания
    
    Args:
        bot: Экземпляр aiogram Bot
        user_id: ID пользователя Telegram
        file_path: Путь к файлу
        title: Название файла
        file_size: Размер файла в байтах
        
    Returns:
        dict: Результат отправки с информацией о методе доставки
    """
    # Ограничение Telegram на размер файла (50 МБ)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    file_size_mb = file_size / (1024*1024)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # Если файл маленький - отправляем через Telegram
        if file_size <= MAX_FILE_SIZE:
            logger.info(f"📤 Отправляем файл через Telegram: {file_size_mb:.1f} МБ")
            
            # Создаем объект файла для отправки
            input_file = FSInputFile(file_path, filename=os.path.basename(file_path))
            
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                # Отправляем как видео
                await bot.send_video(
                    chat_id=user_id,
                    video=input_file,
                    caption=f"✅ {title}\n📦 Размер: {file_size_mb:.1f} МБ"[:1024]
                )
            elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                # Отправляем как аудио
                await bot.send_audio(
                    chat_id=user_id,
                    audio=input_file,
                    caption=f"✅ {title}\n📦 Размер: {file_size_mb:.1f} МБ"[:1024]
                )
            else:
                # Отправляем как документ
                await bot.send_document(
                    chat_id=user_id,
                    document=input_file,
                    caption=f"✅ {title}\n📦 Размер: {file_size_mb:.1f} МБ"[:1024]
                )
            
            return {
                "success": True,
                "method": "telegram",
                "file_size": file_size,
                "message": f"Файл отправлен через Telegram ({file_size_mb:.1f} МБ)"
            }
        
        else:
            # Файл большой - создаем простую ссылку для скачивания через браузер
            logger.info(f"📦 Файл большой ({file_size_mb:.1f} МБ), создаем ссылку для скачивания...")
            
            # Запускаем веб-сервер если нужно
            from .web_server import start_download_server_if_needed
            
            server = await start_download_server_if_needed()
            if not server:
                # Если сервер не запустился, показываем инструкцию по SSH
                relative_path = os.path.relpath(file_path, '/root/SwiftDevBot')
                
                message_text = (
                    f"📁 **Файл готов, но сервер недоступен**\n\n"
                    f"🎬 **{title}**\n"
                    f"📦 **Размер:** {file_size_mb:.1f} МБ\n"
                    f"🎯 **Оригинальное качество** (без сжатия)\n\n"
                    f"📂 **Путь к файлу:** `{file_path}`\n\n"
                    f"💡 **Скачайте через SSH:**\n"
                    f"`scp -P 31201 user@sdb.soverx.top:'{file_path}' ./`"
                )
                
                await bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode="Markdown"
                )
                
                return {
                    "success": True,
                    "method": "ssh_fallback",
                    "file_path": file_path,
                    "file_size": file_size,
                    "message": f"SSH инструкция для файла ({file_size_mb:.1f} МБ)"
                }
            
            # Генерируем токен для скачивания
            safe_filename = os.path.basename(file_path)
            token = server.generate_download_token(
                file_path=file_path,
                filename=safe_filename,
                expire_hours=24
            )
            
            if not token:
                raise Exception("Не удалось создать токен для скачивания")
            
            # Создаем ссылку для скачивания через новый метод
            download_url = server.get_external_url(token)
            
            # Отправляем красивое сообщение со ссылкой
            message_text = (
                f"📁 **Файл готов для скачивания!**\n\n"
                f"🎬 **{title}**\n"
                f"📦 **Размер:** {file_size_mb:.1f} МБ\n"
                f"🎯 **Оригинальное качество** (без сжатия)\n\n"
                f"� **Ссылка для скачивания:**\n"
                f"{download_url}\n\n"
                f"� **Как скачать:**\n"
                f"1. Откройте ссылку в браузере\n"
                f"2. Файл автоматически начнет скачиваться\n"
                f"3. Ссылка действительна 24 часа\n\n"
                f"📱 **Работает на любом устройстве с браузером!**"
            )
            
            # Создаем кнопку для удобства
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"� Скачать файл ({file_size_mb:.1f} МБ)", 
                    url=download_url
                )],
                [InlineKeyboardButton(
                    text="ℹ️ Помощь", 
                    callback_data="download_help"
                )]
            ])
            
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return {
                "success": True,
                "method": "web_download",
                "download_url": download_url,
                "file_path": file_path,
                "file_size": file_size,
                "message": f"Создана веб-ссылка для скачивания ({file_size_mb:.1f} МБ) - оригинальное качество"
            }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        
        # В случае ошибки отправляем информацию о файле
        await bot.send_message(
            chat_id=user_id,
            text=f"❌ **Ошибка при обработке файла**\n\n"
                 f"🎬 **{title}**\n"
                 f"📦 **Размер:** {file_size_mb:.1f} МБ\n"
                 f"📂 **Путь:** `{file_path}`\n\n"
                 f"⚠️ **Ошибка:** {str(e)[:200]}...\n\n"
                 f"💡 **Файл доступен по пути выше для ручного скачивания**",
            parse_mode="Markdown"
        )
        
        return {
            "success": False,
            "error": str(e),
            "file_size": file_size,
            "file_path": file_path
        }
