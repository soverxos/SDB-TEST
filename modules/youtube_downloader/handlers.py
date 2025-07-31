# modules/youtube_downloader/handlers.py
"""
Обработчики для модуля YouTube Downloader
"""

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hitalic, hcode, hlink
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from core.database.core_models import User as DBUser
from core.ui.callback_data_factories import ModuleMenuEntry
from .callback_data import YouTubeAction
from .keyboards import (
    get_youtube_main_menu_keyboard,
    get_video_quality_keyboard,
    get_audio_quality_keyboard,
    get_download_confirmation_keyboard,
    get_history_keyboard,
    get_download_item_keyboard,
    get_url_input_keyboard,
    get_download_complete_keyboard
)
from .models import YouTubeDownload
from .utils import YouTubeDownloader, format_duration, format_file_size, format_count
from .file_sender import send_file_to_user
from .permissions import PERM_ACCESS_USER_FEATURES

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider

youtube_router = Router(name="youtube_downloader_handlers")

async def safe_edit_message(message, text: str, reply_markup=None, fallback_answer=None):
    """
    Безопасное редактирование сообщения с обработкой ошибки 'message is not modified'
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
        return True
    except Exception as e:
        if "message is not modified" in str(e):
            # Сообщение не изменилось, ничего не делаем
            logger.debug(f"Сообщение не изменилось: {e}")
            return False
        else:
            # Другая ошибка - логируем и поднимаем дальше
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            raise

class YouTubeStates(StatesGroup):
    waiting_for_url = State()
    selecting_quality = State()
    confirming_download = State()

# Временное хранилище для пользовательских данных
user_sessions: Dict[int, Dict[str, Any]] = {}

def get_go_to_history_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой перехода к истории загрузок"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Перейти к истории загрузок",
            callback_data=YouTubeAction(action="view_history", page=1).pack()
        )]
    ])
    return keyboard

def get_error_history_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой перехода к истории после ошибки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Посмотреть все загрузки",
            callback_data=YouTubeAction(action="view_history", page=1).pack()
        )]
    ])
    return keyboard

def get_history_with_download_keyboard(downloads, page: int, has_next: bool, has_prev: bool) -> InlineKeyboardMarkup:
    """Создает клавиатуру для истории загрузок с кнопками скачивания"""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки скачивания для завершенных загрузок
    for i, download in enumerate(downloads, 1):
        if download.status == "COMPLETED" and download.file_path and os.path.exists(download.file_path):
            # Ограничиваем длину названия для кнопки
            title = download.title[:25] + "..." if len(download.title) > 25 else download.title
            button_text = f"📥 {i}. {title}"
            
            # Кнопка скачивания
            builder.button(
                text=button_text,
                callback_data=YouTubeAction(action="download_file", item_id=download.id).pack()
            )
            
            # Кнопка удаления файла
            builder.button(
                text=f"🗑️ Удалить {i}",
                callback_data=YouTubeAction(action="delete_file", item_id=download.id).pack()
            )
    
    # Добавляем кнопки навигации
    nav_buttons = []
    if has_prev:
        nav_buttons.append(("⬅️ Назад", YouTubeAction(action="view_history", page=page-1).pack()))
    
    if has_next:
        nav_buttons.append(("Вперед ➡️", YouTubeAction(action="view_history", page=page+1).pack()))
    
    for text, callback_data in nav_buttons:
        builder.button(text=text, callback_data=callback_data)
    
    # Кнопка обновления
    builder.button(
        text="🔄 Обновить",
        callback_data=YouTubeAction(action="view_history", page=page).pack()
    )
    
    # Кнопка очистки истории (только если есть загрузки)
    if downloads:
        builder.button(
            text="🗑️ Очистить историю",
            callback_data=YouTubeAction(action="clear_history").pack()
        )
    
    # Кнопка "Назад к главному меню"
    builder.button(
        text="⬅️ Главное меню",
        callback_data=YouTubeAction(action="main_menu").pack()
    )
    
    # Устанавливаем размер клавиатуры
    completed_files = [d for d in downloads if d.status == "COMPLETED" and d.file_path and os.path.exists(d.file_path)]
    if completed_files:
        # Кнопки скачивания и удаления идут парами
        adjust_list = [2] * len(completed_files)  # По 2 кнопки в ряд (скачать + удалить)
        if nav_buttons:
            adjust_list.append(len(nav_buttons))
        if downloads:  # Есть загрузки - добавляем кнопку очистки
            adjust_list.extend([1, 1, 1])  # Обновить, Очистить, Главное меню
        else:
            adjust_list.extend([1, 1])  # Обновить, Главное меню
        builder.adjust(*adjust_list)
    else:
        if nav_buttons:
            if downloads:  # Есть загрузки но нет доступных файлов
                builder.adjust(len(nav_buttons), 1, 1, 1)  # Навигация, Обновить, Очистить, Главное меню
            else:
                builder.adjust(len(nav_buttons), 1, 1)  # Навигация, Обновить, Главное меню
        else:
            if downloads:  # Есть загрузки но нет навигации
                builder.adjust(1, 1, 1)  # Обновить, Очистить, Главное меню
            else:
                builder.adjust(1, 1)  # Обновить, Главное меню
    
    return builder.as_markup()

@youtube_router.callback_query(ModuleMenuEntry.filter(F.module_name == "youtube_downloader"))
async def youtube_main_menu(
    query: types.CallbackQuery,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Главное меню модуля YouTube Downloader"""
    user_id = sdb_user.telegram_id
    logger.info(f"Пользователь {user_id} открыл модуль YouTube Downloader")
    
    async with services_provider.db.get_session() as session:
        # Проверяем доступ к модулю
        if not await services_provider.rbac.user_has_permission(session, user_id, PERM_ACCESS_USER_FEATURES):
            await query.answer("У вас нет доступа к этому модулю", show_alert=True)
            return
        
        keyboard = await get_youtube_main_menu_keyboard(services_provider, user_id, session)
    
    text = (
        f"📺 {hbold('YouTube Загрузчик')}\n\n"
        f"Добро пожаловать в модуль загрузки контента с YouTube!\n\n"
        f"🎯 {hbold('Возможности:')}\n"
        f"• Скачивание видео в различных качествах\n"
        f"• Извлечение аудио в MP3\n"
        f"• История всех загрузок\n"
        f"• Отправка файлов через бота\n\n"
        f"Выберите действие:"
    )
    
    if query.message:
        await safe_edit_message(query.message, text, reply_markup=keyboard)
    
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "start_video_download"))
async def start_video_download(
    query: types.CallbackQuery,
    state: FSMContext,
    sdb_user: DBUser
):
    """Начало процесса загрузки видео"""
    user_id = sdb_user.telegram_id
    logger.info(f"Пользователь {user_id} начал загрузку видео")
    
    text = (
        f"📺 {hbold('Загрузка видео с YouTube')}\n\n"
        f"Отправьте ссылку на видео YouTube, которое хотите скачать.\n\n"
        f"🔗 {hbold('Поддерживаемые форматы ссылок:')}\n"
        f"• https://www.youtube.com/watch?v=...\n"
        f"• https://youtu.be/...\n"
        f"• https://m.youtube.com/watch?v=...\n\n"
        f"{hitalic('Для отмены используйте /cancel')}"
    )
    
    # Сохраняем тип загрузки в сессии
    user_sessions[user_id] = {"download_type": "video"}
    await state.set_state(YouTubeStates.waiting_for_url)
    
    if query.message:
        await query.message.edit_text(text, reply_markup=get_url_input_keyboard())
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "start_audio_download"))
async def start_audio_download(
    query: types.CallbackQuery,
    state: FSMContext,
    sdb_user: DBUser
):
    """Начало процесса загрузки аудио"""
    user_id = sdb_user.telegram_id
    logger.info(f"Пользователь {user_id} начал загрузку аудио")
    
    text = (
        f"🎵 {hbold('Извлечение аудио с YouTube')}\n\n"
        f"Отправьте ссылку на видео YouTube, из которого хотите извлечь аудио.\n\n"
        f"🔗 {hbold('Поддерживаемые форматы ссылок:')}\n"
        f"• https://www.youtube.com/watch?v=...\n"
        f"• https://youtu.be/...\n"
        f"• https://m.youtube.com/watch?v=...\n\n"
        f"🎧 Аудио будет сохранено в формате MP3\n\n"
        f"{hitalic('Для отмены используйте /cancel')}"
    )
    
    # Сохраняем тип загрузки в сессии
    user_sessions[user_id] = {"download_type": "audio"}
    await state.set_state(YouTubeStates.waiting_for_url)
    
    if query.message:
        await query.message.edit_text(text, reply_markup=get_url_input_keyboard())
    await query.answer()

@youtube_router.message(StateFilter(YouTubeStates.waiting_for_url), F.text)
async def process_youtube_url(
    message: types.Message,
    state: FSMContext,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Обработка введенного URL YouTube"""
    user_id = sdb_user.telegram_id
    url = message.text.strip()
    
    logger.info(f"Пользователь {user_id} ввел URL: {url}")
    
    # Проверяем валидность URL
    downloader = YouTubeDownloader(user_id=user_id)
    if not downloader.validate_youtube_url(url):
        await message.answer(
            "❌ Неверная ссылка на YouTube!\n\n"
            "Пожалуйста, отправьте корректную ссылку на видео YouTube."
        )
        return
    
    # Показываем индикатор обработки
    processing_msg = await message.answer("🔄 Получаю информацию о видео...")
    
    try:
        # Получаем информацию о видео
        video_info = await downloader.get_video_info(url)
        
        if not video_info:
            await processing_msg.edit_text(
                "❌ Не удалось получить информацию о видео.\n"
                "Проверьте ссылку и попробуйте снова."
            )
            return
        
        # Сохраняем данные в сессии
        session_data = user_sessions.get(user_id, {})
        session_data.update({
            "url": url,
            "video_info": video_info
        })
        user_sessions[user_id] = session_data
        
        # Формируем расширенную информацию о видео
        duration_str = format_duration(video_info.get('duration', 0))
        view_count = format_count(video_info.get('view_count', 0))
        like_count = format_count(video_info.get('like_count', 0))
        upload_date = video_info.get('upload_date', 'Неизвестно')
        category = video_info.get('category', 'Неизвестно')
        
        # Строим основную информацию
        text = (
            f"📺 {hbold('Информация о видео')}\n\n"
            f"🎬 {hbold('Название:')}\n{video_info.get('title', 'Неизвестно')}\n\n"
            f"👤 {hbold('Автор:')} {video_info.get('uploader', 'Неизвестно')}\n"
            f"⏱️ {hbold('Длительность:')} {duration_str}\n"
            f"👁️ {hbold('Просмотры:')} {view_count}\n"
            f"👍 {hbold('Лайки:')} {like_count}\n"
            f"📅 {hbold('Дата публикации:')} {upload_date}\n"
            f"📂 {hbold('Категория:')} {category}\n"
        )
        
        # Добавляем теги если есть
        tags = video_info.get('tags', [])
        if tags:
            tags_str = ', '.join(tags[:3])  # Показываем первые 3 тега
            text += f"🏷️ {hbold('Теги:')} {tags_str}\n"
        
        # Добавляем описание если есть
        description = video_info.get('description', '')
        if description:
            text += f"\n📝 {hbold('Описание:')}\n{description}\n"
        
        text += "\n"
        
        download_type = session_data.get("download_type", "video")
        
        if download_type == "video":
            text += "📹 Выберите качество видео:"
            keyboard = get_video_quality_keyboard(video_info)
        else:
            text += "🎵 Выберите качество аудио:"
            keyboard = get_audio_quality_keyboard()
        
        await processing_msg.edit_text(text, reply_markup=keyboard)
        await state.set_state(YouTubeStates.selecting_quality)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке URL {url}: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке видео.\n"
            "Попробуйте еще раз позже."
        )

@youtube_router.callback_query(YouTubeAction.filter(F.action.in_(["download_video_quality", "download_audio_quality"])))
async def select_quality(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    state: FSMContext,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Выбор качества загрузки"""
    user_id = sdb_user.telegram_id
    quality = callback_data.quality
    
    session_data = user_sessions.get(user_id, {})
    if not session_data:
        await query.answer("Сессия истекла. Начните сначала.", show_alert=True)
        return
    
    download_type = session_data.get("download_type")
    video_info = session_data.get("video_info", {})
    video_id = video_info.get('id')
    
    # Обновляем сессию
    session_data["quality"] = quality
    user_sessions[user_id] = session_data
    
    # Проверяем, есть ли уже загрузки этого видео (для информации)
    duplicate_warning = ""
    async with services_provider.db.get_session() as session:
        existing_downloads = await session.execute(
            select(YouTubeDownload)
            .where(
                YouTubeDownload.user_id == user_id,
                YouTubeDownload.video_id == video_id,
                YouTubeDownload.status.in_(["COMPLETED", "DOWNLOADING", "PENDING"])
            )
        )
        existing_records = existing_downloads.scalars().all()
        
        if existing_records:
            # Подсчитываем количество загрузок по типам
            video_count = len([r for r in existing_records if r.format_type == "VIDEO"])
            audio_count = len([r for r in existing_records if r.format_type == "AUDIO"])
            
            if video_count > 0 or audio_count > 0:
                duplicate_warning = f"\n⚠️ {hbold('Примечание:')} У вас уже есть загрузки этого видео"
                if video_count > 0:
                    duplicate_warning += f" (📹{video_count} видео"
                    if audio_count > 0:
                        duplicate_warning += f", 🎵{audio_count} аудио)"
                    else:
                        duplicate_warning += ")"
                elif audio_count > 0:
                    duplicate_warning += f" (🎵{audio_count} аудио)"
                duplicate_warning += "\n"
    
    # Формируем расширенный текст подтверждения
    duration_str = format_duration(video_info.get('duration', 0))
    view_count = format_count(video_info.get('view_count', 0))
    
    text = (
        f"✅ {hbold('Подтверждение загрузки')}\n\n"
        f"🎬 {hbold('Название:')}\n{video_info.get('title', 'Неизвестно')}\n\n"
        f"� {hbold('Автор:')} {video_info.get('uploader', 'Неизвестно')}\n"
        f"⏱️ {hbold('Длительность:')} {duration_str}\n"
        f"👁️ {hbold('Просмотры:')} {view_count}\n\n"
        f"�📥 {hbold('Тип загрузки:')} {'📹 Видео' if download_type == 'video' else '🎵 Аудио'}\n"
        f"🎯 {hbold('Качество:')} {quality}\n"
        f"{duplicate_warning}\n"
        f"❓ Подтвердите загрузку:"
    )
    
    keyboard = get_download_confirmation_keyboard(download_type, quality)
    
    if query.message:
        await query.message.edit_text(text, reply_markup=keyboard)
    
    await state.set_state(YouTubeStates.confirming_download)
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "confirm_download"))
async def confirm_download(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    state: FSMContext,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    bot: Bot
):
    """Подтверждение и начало загрузки"""
    user_id = sdb_user.telegram_id
    
    session_data = user_sessions.get(user_id, {})
    if not session_data:
        await query.answer("Сессия истекла. Начните сначала.", show_alert=True)
        return
    
    url = session_data.get("url")
    video_info = session_data.get("video_info", {})
    download_type = callback_data.format_type
    quality = callback_data.quality
    video_id = video_info.get('id')
    
    # Проверяем, не загружал ли пользователь уже этот файл
    async with services_provider.db.get_session() as session:
        existing_download = await session.execute(
            select(YouTubeDownload)
            .where(
                YouTubeDownload.user_id == user_id,
                YouTubeDownload.video_id == video_id,
                YouTubeDownload.format_type == download_type.upper(),
                YouTubeDownload.quality == quality,
                YouTubeDownload.status.in_(["COMPLETED", "DOWNLOADING", "PENDING"])
            )
        )
        existing_record = existing_download.scalar_one_or_none()
        
        if existing_record:
            # Файл уже был загружен или загружается
            status_text = {
                "COMPLETED": "завершена",
                "DOWNLOADING": "выполняется", 
                "PENDING": "ожидает выполнения"
            }.get(existing_record.status, "неизвестна")
            
            # Форматируем дату предыдущей загрузки
            created_date = existing_record.created_at.strftime('%d.%m.%Y %H:%M') if existing_record.created_at else 'Неизвестно'
            completed_date = existing_record.completed_at.strftime('%d.%m.%Y %H:%M') if existing_record.completed_at else None
            
            # Создаем клавиатуру с выбором действий
            builder = InlineKeyboardBuilder()
            
            if existing_record.status == "COMPLETED":
                builder.button(
                    text="📱 Отправить уже загруженный файл",
                    callback_data=YouTubeAction(action="send_file", item_id=existing_record.id).pack()
                )
                builder.button(
                    text="🔄 Перезагрузить файл (заменить существующий)",
                    callback_data=YouTubeAction(
                        action="replace_download", 
                        format_type=download_type,
                        quality=quality,
                        item_id=existing_record.id
                    ).pack()
                )
            elif existing_record.status in ["DOWNLOADING", "PENDING"]:
                builder.button(
                    text="🔄 Перезапустить загрузку (заменить текущую)",
                    callback_data=YouTubeAction(
                        action="replace_download", 
                        format_type=download_type,
                        quality=quality,
                        item_id=existing_record.id
                    ).pack()
                )
            
            builder.button(
                text="📋 Перейти к истории загрузок",
                callback_data=YouTubeAction(action="view_history", page=1).pack()
            )
            
            builder.button(
                text="⬅️ Назад в меню",
                callback_data=YouTubeAction(action="main_menu").pack()
            )
            
            builder.adjust(1)
            
            # Строим сообщение с подробной информацией
            text = (
                f"⚠️ {hbold('Файл уже был загружен!')}\n\n"
                f"🎬 {hbold('Видео:')} {video_info.get('title', 'Неизвестно')}\n"
                f"📥 {hbold('Тип:')} {'📹 Видео' if download_type == 'video' else '🎵 Аудио'}\n"
                f"🎯 {hbold('Качество:')} {quality}\n\n"
                f"📊 {hbold('Статус текущей загрузки:')} {status_text}\n"
                f"📅 {hbold('Дата запуска:')} {created_date}\n"
            )
            
            if completed_date and existing_record.status == "COMPLETED":
                text += f"✅ {hbold('Дата завершения:')} {completed_date}\n"
                if existing_record.file_size:
                    text += f"📦 {hbold('Размер файла:')} {format_file_size(existing_record.file_size)}\n"
            
            text += (
                f"\n💡 {hbold('Примечание:')} При повторной загрузке старый файл будет заменен новым.\n"
                f"❓ {hbold('Что хотите сделать?')}"
            )
            
            if query.message:
                await query.message.edit_text(text, reply_markup=builder.as_markup())
            await query.answer()
            return
        
        # Если дубликата нет, создаем новую запись
        download_record = YouTubeDownload(
            user_id=user_id,
            url=url,
            video_id=video_id,
            title=video_info.get('title'),
            duration=video_info.get('duration'),
            format_type=download_type.upper(),
            quality=quality,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        
        session.add(download_record)
        await session.commit()
        await session.refresh(download_record)
    
    # Запускаем загрузку в фоне
    asyncio.create_task(
        perform_download(download_record.id, services_provider, bot)
    )
    
    text = (
        f"🚀 {hbold('Загрузка запущена!')}\n\n"
        f"📊 Ваша загрузка добавлена в очередь.\n"
        f"Это может занять некоторое время в зависимости от размера файла.\n\n"
        f"💬 Вы получите уведомление, когда загрузка завершится.\n"
        f"📋 Проверить статус можно в разделе 'История загрузок'."
    )
    
    if query.message:
        await query.message.edit_text(text, reply_markup=None)
    
    # Очищаем состояние и сессию
    await state.clear()
    user_sessions.pop(user_id, None)
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "replace_download"))
async def replace_download(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    state: FSMContext,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    bot: Bot
):
    """Замена существующей загрузки"""
    user_id = sdb_user.telegram_id
    
    session_data = user_sessions.get(user_id, {})
    if not session_data:
        await query.answer("Сессия истекла. Начните сначала.", show_alert=True)
        return
    
    url = session_data.get("url")
    video_info = session_data.get("video_info", {})
    download_type = callback_data.format_type
    quality = callback_data.quality
    video_id = video_info.get('id')
    existing_id = callback_data.item_id
    
    # Заменяем существующую запись
    async with services_provider.db.get_session() as session:
        # Получаем существующую запись для удаления старого файла
        if existing_id:
            existing_download = await session.execute(
                select(YouTubeDownload).where(YouTubeDownload.id == existing_id)
            )
            old_record = existing_download.scalar_one_or_none()
            
            if old_record and old_record.file_path:
                # Удаляем старый файл если он существует
                try:
                    import os
                    if os.path.exists(old_record.file_path):
                        os.remove(old_record.file_path)
                        logger.info(f"🗑️ Удален старый файл: {old_record.file_path}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить старый файл: {e}")
                
                # Очищаем кэш для этого видео
                try:
                    downloader = YouTubeDownloader()
                    file_type = "video" if download_type == "video" else "audio"
                    downloader.clean_cache_for_video(video_id, file_type)
                except Exception as e:
                    logger.warning(f"Не удалось очистить кэш: {e}")
            
            # Обновляем существующую запись вместо создания новой
            if old_record:
                old_record.status = "PENDING"
                old_record.created_at = datetime.utcnow()
                old_record.completed_at = None
                old_record.file_path = None
                old_record.file_size = None
                old_record.error_message = None
                download_record = old_record
            else:
                # Если старая запись не найдена, создаем новую
                download_record = YouTubeDownload(
                    user_id=user_id,
                    url=url,
                    video_id=video_id,
                    title=video_info.get('title'),
                    duration=video_info.get('duration'),
                    format_type=download_type.upper(),
                    quality=quality,
                    status="PENDING",
                    created_at=datetime.utcnow()
                )
                session.add(download_record)
        else:
            # Создаем новую запись если ID не передан
            download_record = YouTubeDownload(
                user_id=user_id,
                url=url,
                video_id=video_id,
                title=video_info.get('title'),
                duration=video_info.get('duration'),
                format_type=download_type.upper(),
                quality=quality,
                status="PENDING",
                created_at=datetime.utcnow()
            )
            session.add(download_record)
        
        await session.commit()
        await session.refresh(download_record)
    
    # Запускаем загрузку в фоне
    asyncio.create_task(
        perform_download(download_record.id, services_provider, bot)
    )
    
    text = (
        f"� {hbold('Замена файла запущена!')}\n\n"
        f"📊 Старый файл будет заменен новой загрузкой.\n"
        f"Это может занять некоторое время в зависимости от размера файла.\n\n"
        f"💬 Вы получите уведомление, когда загрузка завершится.\n"
        f"📋 Проверить статус можно в разделе 'История загрузок'."
    )
    
    if query.message:
        await query.message.edit_text(text, reply_markup=None)
    
    # Очищаем состояние и сессию
    await state.clear()
    user_sessions.pop(user_id, None)
    await query.answer()

async def perform_download(download_id: int, services_provider: 'BotServicesProvider', bot: Bot):
    """Выполняет загрузку в фоне"""
    async with services_provider.db.get_session() as session:
        # Получаем запись загрузки
        result = await session.execute(
            select(YouTubeDownload).where(YouTubeDownload.id == download_id)
        )
        download = result.scalar_one_or_none()
        
        if not download:
            logger.error(f"Загрузка {download_id} не найдена")
            return
        
        try:
            # Обновляем статус
            download.status = "DOWNLOADING"
            download.started_at = datetime.now(timezone.utc)
            await session.commit()
            
            # Создаем загрузчик
            downloader = YouTubeDownloader(user_id=download.user_id)
            
            # Выполняем загрузку
            if download.format_type == "VIDEO":
                result = await downloader.download_video(download.url, download.quality)
            else:
                result = await downloader.download_audio(download.url, download.quality)
            
            if result["success"]:
                # Успешная загрузка
                download.status = "COMPLETED"
                download.file_path = result["file_path"]
                download.file_size = result["file_size"]
                download.completed_at = datetime.now(timezone.utc)
                
                # Проверяем, был ли файл взят из кэша
                from_cache = result.get("from_cache", False)
                cache_emoji = "💾" if from_cache else "📥"
                cache_text = " (из кэша)" if from_cache else ""
                
                # Отправляем файл пользователю
                file_result = await send_file_to_user(
                    bot, download.user_id, download.file_path, download.title, download.file_size
                )
                
                # Отправляем уведомление в зависимости от метода доставки
                file_sent = file_result.get("success", False) if file_result else False
                method = file_result.get("method") if file_result else None
                
                if file_sent and method == "telegram":
                    # Файл отправлен через Telegram
                    await bot.send_message(
                        download.user_id,
                        f"✅ {hbold('Загрузка завершена и файл отправлен!')}{cache_text}\n\n"
                        f"🎬 {hbold('Название:')} {download.title}\n"
                        f"👤 {hbold('Автор:')} {result.get('uploader', 'Неизвестно')}\n"
                        f"⏱️ {hbold('Длительность:')} {format_duration(result.get('duration', 0))}\n"
                        f"👁️ {hbold('Просмотры:')} {format_count(result.get('view_count', 0))}\n"
                        f"📦 {hbold('Размер файла:')} {format_file_size(download.file_size)}\n"
                        f"🎯 {hbold('Качество:')} {download.quality}\n"
                        f"{cache_emoji} {hbold('Источник:')} {'Получено из кэша' if from_cache else 'Загружено с YouTube'}\n\n"
                        f"📋 Также доступен в разделе 'История загрузок'",
                        reply_markup=get_download_complete_keyboard()
                    )
                elif file_sent and method == "web_download":
                    # Файл большой, создана ссылка для скачивания
                    download_url = file_result.get("download_url", "")
                    await bot.send_message(
                        download.user_id,
                        f"✅ {hbold('Загрузка завершена!')}{cache_text}\n\n"
                        f"🎬 {hbold('Название:')} {download.title}\n"
                        f"👤 {hbold('Автор:')} {result.get('uploader', 'Неизвестно')}\n"
                        f"⏱️ {hbold('Длительность:')} {format_duration(result.get('duration', 0))}\n"
                        f"👁️ {hbold('Просмотры:')} {format_count(result.get('view_count', 0))}\n"
                        f"📦 {hbold('Размер файла:')} {format_file_size(download.file_size)}\n"
                        f"🎯 {hbold('Качество:')} {download.quality}\n"
                        f"{cache_emoji} {hbold('Источник:')} {'Получено из кэша' if from_cache else 'Загружено с YouTube'}\n\n"
                        f"📁 {hbold('Файл готов для скачивания!')} (слишком большой для Telegram)\n"
                        f"🌐 {hlink('📥 Скачать файл', download_url)}\n"
                        f"⏰ Ссылка действительна 24 часа\n\n"
                        f"📋 Также доступен в разделе 'История загрузок'",
                        reply_markup=get_download_complete_keyboard()
                    )
                else:
                    # Ошибка при создании файла или ссылки
                    await bot.send_message(
                        download.user_id,
                        f"❌ {hbold('Загрузка завершена, но произошла ошибка при подготовке файла')}{cache_text}\n\n"
                        f"🎬 {hbold('Название:')} {download.title}\n"
                        f"👤 {hbold('Автор:')} {result.get('uploader', 'Неизвестно')}\n"
                        f"⏱️ {hbold('Длительность:')} {format_duration(result.get('duration', 0))}\n"
                        f"👁️ {hbold('Просмотры:')} {format_count(result.get('view_count', 0))}\n"
                        f"📦 {hbold('Размер файла:')} {format_file_size(download.file_size)}\n"
                        f"🎯 {hbold('Качество:')} {download.quality}\n"
                        f"{cache_emoji} {hbold('Источник:')} {'Получено из кэша' if from_cache else 'Загружено с YouTube'}\n\n"
                        f"📋 Файл доступен в разделе 'История загрузок'",
                        reply_markup=get_download_complete_keyboard()
                    )
            else:
                # Ошибка загрузки
                download.status = "FAILED"
                download.error_message = result["error"]
                download.completed_at = datetime.now(timezone.utc)
                
                # Отправляем уведомление об ошибке
                await bot.send_message(
                    download.user_id,
                    f"❌ {hbold('Ошибка загрузки')}\n\n"
                    f"🎬 {download.title}\n"
                    f"📝 Ошибка: {result['error']}",
                    reply_markup=get_error_history_keyboard()
                )
            
            await session.commit()
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении загрузки {download_id}: {e}")
            download.status = "FAILED"
            download.error_message = str(e)
            download.completed_at = datetime.now(timezone.utc)
            await session.commit()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "view_history"))
async def view_history(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Просмотр истории загрузок"""
    user_id = sdb_user.telegram_id
    page = callback_data.page or 1
    per_page = 5
    offset = (page - 1) * per_page
    
    async with services_provider.db.get_session() as session:
        # Получаем загрузки пользователя
        result = await session.execute(
            select(YouTubeDownload)
            .where(YouTubeDownload.user_id == user_id)
            .order_by(desc(YouTubeDownload.created_at))
            .offset(offset)
            .limit(per_page + 1)  # +1 для проверки наличия следующей страницы
        )
        downloads = result.scalars().all()
        
        has_next = len(downloads) > per_page
        if has_next:
            downloads = downloads[:-1]  # Убираем лишний элемент
        
        has_prev = page > 1
        
        if not downloads:
            text = (
                f"📋 {hbold('История загрузок')}\n\n"
                f"📭 У вас пока нет загрузок.\n\n"
                f"Начните с главного меню модуля!"
            )
        else:
            text = f"📋 {hbold('История загрузок')} (страница {page})\n\n"
            
            # Подсчитываем количество доступных для скачивания файлов
            available_downloads = sum(1 for d in downloads if d.status == "COMPLETED" and d.file_path and os.path.exists(d.file_path))
            if available_downloads > 0:
                text += f"💡 {hitalic('Нажмите на кнопку ниже, чтобы скачать файл')}\n\n"
            
            for i, download in enumerate(downloads, 1):
                status_emoji = {
                    "PENDING": "⏳",
                    "DOWNLOADING": "🔄",
                    "COMPLETED": "✅",
                    "FAILED": "❌"
                }
                
                type_emoji = "📺" if download.format_type == "VIDEO" else "🎵"
                
                text += (
                    f"{status_emoji[download.status]} {type_emoji} {hbold(f'{i}.')} "
                    f"{download.title[:30]}{'...' if len(download.title) > 30 else ''}\n"
                    f"📅 {download.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                )
                
                if download.status == "COMPLETED":
                    text += f"📦 {format_file_size(download.file_size)}"
                    if download.file_path and os.path.exists(download.file_path):
                        text += " 📥 Доступен для скачивания"
                    text += "\n"
                elif download.status == "FAILED":
                    text += f"❌ {download.error_message[:50]}...\n"
                
                text += "\n"
        
        # Добавляем метку времени обновления для предотвращения ошибки Telegram
        current_time = datetime.now().strftime("%H:%M:%S")
        text += f"\n🕐 Обновлено: {current_time}"
        
        # Используем функцию, определенную в этом файле, которая показывает кнопки скачивания
        keyboard = get_history_with_download_keyboard(downloads, page, has_next, has_prev)
        
        if query.message:
            # Используем безопасное редактирование сообщения
            edit_success = await safe_edit_message(query.message, text, reply_markup=keyboard)
            if not edit_success:
                # Сообщение не изменилось, уведомляем пользователя
                await query.answer("📋 История загрузок актуальна", show_alert=False)
                return
        
        await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "send_file"))
async def send_existing_file(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    bot: Bot
):
    """Отправка уже загруженного файла пользователю"""
    user_id = sdb_user.telegram_id
    download_id = callback_data.item_id
    
    if not download_id:
        await query.answer("❌ Ошибка: не указан ID загрузки", show_alert=True)
        return
    
    async with services_provider.db.get_session() as session:
        # Получаем запись загрузки
        result = await session.execute(
            select(YouTubeDownload)
            .where(YouTubeDownload.id == download_id)
            .where(YouTubeDownload.user_id == user_id)  # Проверяем, что файл принадлежит пользователю
        )
        download = result.scalar_one_or_none()
        
        if not download:
            await query.answer("❌ Загрузка не найдена", show_alert=True)
            return
        
        if download.status != "COMPLETED":
            await query.answer("❌ Загрузка не завершена", show_alert=True)
            return
        
        if not download.file_path or not os.path.exists(download.file_path):
            await query.answer("❌ Файл не найден на сервере", show_alert=True)
            return
        
        # Отправляем уведомление о начале отправки
        await query.answer("📤 Отправляю файл...", show_alert=False)
        
        try:
            # Отправляем файл пользователю
            file_result = await send_file_to_user(
                bot, user_id, download.file_path, download.title, download.file_size
            )
            
            file_sent = file_result.get("success", False) if file_result else False
            if file_sent and file_result.get("method") == "telegram":
                # Уведомляем об успешной отправке
                await bot.send_message(
                    user_id,
                    f"✅ {hbold('Файл отправлен!')}\n\n"
                    f"🎬 {download.title}\n"
                    f"📦 Размер: {format_file_size(download.file_size)}\n"
                    f"📅 Загружен: {download.created_at.strftime('%d.%m.%Y %H:%M') if download.created_at else 'Неизвестно'}"
                )
            elif file_sent and file_result.get("method") in ["web_download", "ssh_fallback"]:
                # Файл доставлен через веб-ссылку - сообщение уже отправлено в send_file_to_user
                pass
            else:
                # Файл слишком большой для отправки или ошибка
                await bot.send_message(
                    user_id,
                    f"📁 {hbold('Файл готов, но слишком большой для отправки')}\n\n"
                    f"🎬 {download.title}\n"
                    f"📦 Размер: {format_file_size(download.file_size)}\n"
                    f"💡 Файл превышает лимит Telegram (50МБ)\n"
                    f"📋 Файл доступен в разделе 'История загрузок'"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке файла {download_id}: {e}")
            await bot.send_message(
                user_id,
                f"❌ {hbold('Ошибка при отправке файла')}\n\n"
                f"🎬 {download.title}\n"
                f"📝 Попробуйте еще раз позже"
            )

@youtube_router.callback_query(YouTubeAction.filter(F.action == "download_file"))
async def download_file_from_history(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    bot: Bot
):
    """Скачивание файла из истории загрузок"""
    user_id = sdb_user.telegram_id
    download_id = callback_data.item_id
    
    if not download_id:
        await query.answer("❌ Ошибка: не указан ID загрузки", show_alert=True)
        return
    
    async with services_provider.db.get_session() as session:
        # Получаем запись загрузки
        result = await session.execute(
            select(YouTubeDownload)
            .where(YouTubeDownload.id == download_id)
            .where(YouTubeDownload.user_id == user_id)  # Проверяем, что файл принадлежит пользователю
        )
        download = result.scalar()
        
        if not download:
            await query.answer("❌ Загрузка не найдена", show_alert=True)
            return
        
        if download.status != "COMPLETED":
            await query.answer("❌ Загрузка не завершена", show_alert=True)
            return
        
        if not download.file_path or not os.path.exists(download.file_path):
            await query.answer("❌ Файл не найден на сервере", show_alert=True)
            return
        
        # Отправляем уведомление о начале отправки
        await query.answer("📤 Отправляю файл...", show_alert=False)
        
        # Отправляем файл пользователю
        file_result = await send_file_to_user(
            bot, user_id, download.file_path, download.title, download.file_size
        )
        # Результат обработки отправки уже показан пользователю в send_file_to_user

@youtube_router.callback_query(YouTubeAction.filter(F.action == "delete_file"))
async def delete_file_confirm(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Подтверждение удаления отдельного файла"""
    user_id = sdb_user.telegram_id
    download_id = callback_data.item_id
    
    if not download_id:
        await query.answer("❌ Ошибка: не указан ID загрузки", show_alert=True)
        return
    
    async with services_provider.db.get_session() as session:
        # Получаем запись загрузки
        result = await session.execute(
            select(YouTubeDownload)
            .where(YouTubeDownload.id == download_id)
            .where(YouTubeDownload.user_id == user_id)
        )
        download = result.scalar()
        
        if not download:
            await query.answer("❌ Загрузка не найдена", show_alert=True)
            return
        
        # Создаем клавиатуру подтверждения
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить файл", 
                    callback_data=YouTubeAction(action="confirm_delete", item_id=download_id).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена", 
                    callback_data=YouTubeAction(action="view_history", page=1).pack()
                )
            ]
        ])
        
        file_size_text = ""
        if download.file_size:
            file_size_text = f"\n📦 Размер: {format_file_size(download.file_size)}"
        
        await query.message.edit_text(
            f"🗑️ {hbold('Удаление файла')}\n\n"
            f"📹 {hbold('Название:')}\n{download.title}\n"
            f"📊 {hbold('Качество:')} {download.quality or 'N/A'}"
            f"{file_size_text}\n\n"
            f"⚠️ {hitalic('Внимание! Это действие удалит файл с сервера.')}\n"
            f"❗ Это действие нельзя отменить!",
            reply_markup=keyboard
        )
        await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "confirm_delete"))
async def confirm_delete_file(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Выполнение удаления отдельного файла"""
    user_id = sdb_user.telegram_id
    download_id = callback_data.item_id
    
    if not download_id:
        await query.answer("❌ Ошибка: не указан ID загрузки", show_alert=True)
        return
    
    try:
        async with services_provider.db.get_session() as session:
            # Получаем запись загрузки
            result = await session.execute(
                select(YouTubeDownload)
                .where(YouTubeDownload.id == download_id)
                .where(YouTubeDownload.user_id == user_id)
            )
            download = result.scalar()
            
            if not download:
                await query.answer("❌ Загрузка не найдена", show_alert=True)
                return
            
            file_deleted = False
            
            # Удаляем файл с диска
            if download.file_path and os.path.exists(download.file_path):
                try:
                    os.remove(download.file_path)
                    file_deleted = True
                    logger.info(f"Файл удален: {download.file_path}")
                except Exception as file_error:
                    logger.error(f"Ошибка при удалении файла {download.file_path}: {file_error}")
            
            # Удаляем запись из базы данных
            await session.delete(download)
            await session.commit()
            
            await query.message.edit_text(
                f"✅ {hbold('Файл удален!')}\n\n"
                f"📹 {download.title}\n"
                f"📊 {download.quality or 'N/A'}\n\n"
                f"{'🗂️ Файл удален с сервера' if file_deleted else '📝 Запись удалена из истории'}\n\n"
                f"Вы можете вернуться к истории загрузок.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="⬅️ К истории",
                        callback_data=YouTubeAction(action="view_history", page=1).pack()
                    )]
                ])
            )
            
    except Exception as e:
        logger.error(f"Ошибка при удалении файла пользователя {user_id}: {e}")
        await query.message.edit_text(
            f"❌ {hbold('Ошибка при удалении файла')}\n\n"
            f"📝 {str(e)}\n\n"
            f"Попробуйте позже или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬅️ Назад к истории",
                    callback_data=YouTubeAction(action="view_history", page=1).pack()
                )]
            ])
        )
    await query.answer()


@youtube_router.callback_query(YouTubeAction.filter(F.action == "clear_history"))
async def clear_history_confirm(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Подтверждение очистки истории"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, очистить всё", 
                callback_data=YouTubeAction(action="confirm_clear").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отмена", 
                callback_data=YouTubeAction(action="view_history", page=1).pack()
            )
        ]
    ])
    
    await query.message.edit_text(
        f"🗑️ {hbold('Очистка истории загрузок')}\n\n"
        f"⚠️ {hitalic('Внимание! Это действие удалит:')}\n"
        f"• Всю историю ваших загрузок\n"
        f"• Все скачанные файлы с сервера\n\n"
        f"❗ Это действие нельзя отменить!",
        reply_markup=keyboard
    )
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action == "confirm_clear"))
async def confirm_clear_history(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Выполнение очистки истории"""
    user_id = sdb_user.telegram_id
    
    try:
        async with services_provider.db.get_session() as session:
            # Получаем все загрузки пользователя
            result = await session.execute(
                select(YouTubeDownload)
                .where(YouTubeDownload.user_id == user_id)
            )
            downloads = result.scalars().all()
            
            # Удаляем файлы с диска
            deleted_files = 0
            for download in downloads:
                if download.file_path and os.path.exists(download.file_path):
                    try:
                        os.remove(download.file_path)
                        deleted_files += 1
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {download.file_path}: {e}")
            
            # Удаляем записи из базы данных
            for download in downloads:
                await session.delete(download)
            
            await session.commit()
            
            # Удаляем пользовательскую папку если она пустая
            user_dir = Path(f"project_data/downloads/user_{user_id}")
            if user_dir.exists():
                try:
                    if not any(user_dir.iterdir()):  # Папка пустая
                        user_dir.rmdir()
                except Exception as e:
                    logger.error(f"Ошибка при удалении папки пользователя {user_dir}: {e}")
            
            await query.message.edit_text(
                f"✅ {hbold('История очищена!')}\n\n"
                f"📊 Удалено записей: {len(downloads)}\n"
                f"🗂️ Удалено файлов: {deleted_files}\n\n"
                f"Теперь вы можете начать загружать новые видео!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="⬅️ Главное меню",
                        callback_data=YouTubeAction(action="main_menu").pack()
                    )]
                ])
            )
            
    except Exception as e:
        logger.error(f"Ошибка при очистке истории пользователя {user_id}: {e}")
        await query.message.edit_text(
            f"❌ {hbold('Ошибка при очистке истории')}\n\n"
            f"📝 {str(e)}\n\n"
            f"Попробуйте позже или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬅️ Назад к истории",
                    callback_data=YouTubeAction(action="view_history", page=1).pack()
                )]
            ])
        )
    
    await query.answer()

@youtube_router.callback_query(YouTubeAction.filter(F.action.in_(["cancel_download", "no_actions"])))
async def cancel_or_no_action(
    query: types.CallbackQuery,
    callback_data: YouTubeAction,
    state: FSMContext,
    sdb_user: DBUser
):
    """Отмена загрузки или обработка отсутствия действий"""
    user_id = sdb_user.telegram_id
    
    if callback_data.action == "cancel_download":
        # Очищаем состояние и сессию
        await state.clear()
        user_sessions.pop(user_id, None)
        
        text = "❌ Загрузка отменена."
    else:
        text = "🤷‍♂️ У вас нет доступа к функциям этого модуля."
    
    await query.answer(text, show_alert=True)

@youtube_router.callback_query(YouTubeAction.filter(F.action == "main_menu"))
async def back_to_main_menu(
    query: types.CallbackQuery,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser,
    state: FSMContext
):
    """Возврат в главное меню модуля"""
    user_id = sdb_user.telegram_id
    
    # Очищаем состояние и сессию
    await state.clear()
    user_sessions.pop(user_id, None)
    
    await youtube_main_menu(query, services_provider, sdb_user)

@youtube_router.message(Command("cancel"), StateFilter(YouTubeStates))
async def cancel_state(message: types.Message, state: FSMContext, sdb_user: DBUser):
    """Отмена текущего состояния"""
    user_id = sdb_user.telegram_id
    await state.clear()
    user_sessions.pop(user_id, None)
    await message.answer("❌ Операция отменена.")

# Команда для модуля
@youtube_router.message(Command("youtube"))
async def youtube_command(
    message: types.Message,
    services_provider: 'BotServicesProvider',
    sdb_user: DBUser
):
    """Команда для быстрого доступа к модулю"""
    user_id = sdb_user.telegram_id
    
    async with services_provider.db.get_session() as session:
        if not await services_provider.rbac.user_has_permission(session, user_id, PERM_ACCESS_USER_FEATURES):
            await message.answer("❌ У вас нет доступа к модулю YouTube Downloader")
            return
        
        keyboard = await get_youtube_main_menu_keyboard(services_provider, user_id, session)
    
    text = (
        f"📺 {hbold('YouTube Загрузчик')}\n\n"
        f"Модуль для скачивания видео и аудио с YouTube.\n"
        f"Выберите действие:"
    )
    
    await message.answer(text, reply_markup=keyboard)


# Обработчики для кнопок помощи
@youtube_router.callback_query(F.data == "download_help")
async def handle_download_help_callback(callback_query: types.CallbackQuery):
    """Обработчик кнопки помощи по скачиванию"""
    # Импортируем функцию-обработчик
    from .file_sender import handle_download_help_callback
    await handle_download_help_callback(callback_query)


@youtube_router.callback_query(F.data == "back_to_download")
async def handle_back_to_download_callback(callback_query: types.CallbackQuery):
    """Возврат к исходному сообщению о скачивании"""
    await callback_query.message.edit_text(
        text="ℹ️ Информация о скачивании была обновлена. Для получения новой ссылки запросите файл снова.",
        parse_mode="Markdown"
    )
    await callback_query.answer()
