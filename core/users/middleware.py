# SwiftDevBot/core/users/middleware.py
from typing import Callable, Dict, Any, Awaitable, Optional
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User as AiogramUser, Update, ReplyKeyboardRemove
from loguru import logger
from datetime import datetime, timezone 

from core.database.core_models import User as DBUser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.ui.keyboards_core import TEXTS_CORE_KEYBOARDS_EN


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from core.users.service import UserService 

MODULE_NAME_FOR_LOG = "UserStatusMiddleware"

class UserStatusMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update, 
        data: Dict[str, Any]
    ) -> Any:
        
        aiogram_event_user: Optional[AiogramUser] = data.get("event_from_user")
        if not aiogram_event_user:
            return await handler(event, data)

        user_tg_id = aiogram_event_user.id
        user_mention = f"@{aiogram_event_user.username}" if aiogram_event_user.username else f"ID:{user_tg_id}"
        
        services_provider: Optional['BotServicesProvider'] = data.get("services_provider")
        if not (services_provider and hasattr(services_provider, 'db') and hasattr(services_provider, 'user_service')):
            logger.critical(f"[{MODULE_NAME_FOR_LOG}] Необходимые сервисы (DBManager, UserService) не инициализированы "
                           f"или отсутствуют в data. Проверка/создание пользователя {user_mention} невозможно. Прерывание.")
            if event.message: await event.message.reply("Ошибка конфигурации сервисов бота. Пожалуйста, сообщите администратору.")
            elif event.callback_query: await event.callback_query.answer("Ошибка конфигурации сервисов.", show_alert=True)
            return None

        user_service: 'UserService' = services_provider.user_service
        db_user: Optional[DBUser] = None
        user_was_created_in_this_middleware_call = False # Флаг для этого вызова middleware

        # 1. СНАЧАЛА получаем пользователя из БД, чтобы немедленно проверить его статус
        try:
            async with services_provider.db.get_session() as session:
                stmt = select(DBUser).where(DBUser.telegram_id == user_tg_id)
                result = await session.execute(stmt)
                db_user = result.scalars().first()
        except Exception as e_get_user:
            logger.error(f"[{MODULE_NAME_FOR_LOG}] Ошибка БД при первоначальном получении пользователя {user_mention}: {e_get_user}", exc_info=True)
            if event.message: await event.message.reply("Внутренняя ошибка сервера. Попробуйте позже.")
            elif event.callback_query: await event.callback_query.answer("Внутренняя ошибка сервера.", show_alert=True)
            return None

        # 2. ПРОВЕРЯЕМ СТАТУС, ЕСЛИ ПОЛЬЗОВАТЕЛЬ СУЩЕСТВУЕТ
        if db_user:
            bot: Optional[Bot] = data.get("bot")
            gettext: Callable = data.get("gettext", lambda key, **kwargs: key) # Безопасный gettext

            if not db_user.is_active:
                logger.warning(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_mention} (DB ID: {db_user.id}) неактивен. Доступ запрещен.")
                if bot:
                    try:
                        key = "account_deactivated_message"
                        alert_text = gettext(key)
                        if alert_text == key:
                            alert_text = TEXTS_CORE_KEYBOARDS_EN.get(key, "Your account has been deactivated. Please contact an administrator for more information.")
                        
                        if event.message:
                            await bot.send_message(user_tg_id, alert_text, reply_markup=ReplyKeyboardRemove())
                        elif event.callback_query:
                            await event.callback_query.answer(alert_text, show_alert=True)
                    except Exception as e_send_alert:
                        logger.error(f"[{MODULE_NAME_FOR_LOG}] Не удалось отправить уведомление о деактивации пользователю {user_tg_id}: {e_send_alert}")
                return None 

            if db_user.is_bot_blocked:
                logger.warning(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_mention} (DB ID: {db_user.id}) заблокирован администратором. Доступ запрещен.")
                if bot:
                    try:
                        key = "account_blocked_message"
                        alert_text = gettext(key)
                        if alert_text == key:
                            alert_text = TEXTS_CORE_KEYBOARDS_EN.get(key, "Your access to the bot has been restricted by an administrator. Please contact support for details.")

                        if event.message:
                            await bot.send_message(user_tg_id, alert_text, reply_markup=ReplyKeyboardRemove())
                        elif event.callback_query:
                            await event.callback_query.answer(alert_text, show_alert=True)
                    except Exception as e_send_alert:
                        logger.debug(f"[{MODULE_NAME_FOR_LOG}] Не удалось отправить уведомление о блокировке пользователю {user_tg_id} (возможно, он заблокировал бота): {e_send_alert}")
                return None

        is_start_command = event.message and event.message.text and event.message.text.startswith("/start")
        is_owner_from_config = user_tg_id in services_provider.config.core.super_admins

        # 3. ЕСЛИ ПОЛЬЗОВАТЕЛЯ НЕТ, проверяем, можно ли ему регистрироваться
        if not db_user and not is_start_command and not is_owner_from_config:
            logger.info(f"[{MODULE_NAME_FOR_LOG}] Незарегистрированный пользователь {user_mention} попытался использовать бота без /start. Отправка призыва к регистрации.")
            please_register_text = TEXTS_CORE_KEYBOARDS_EN.get("user_middleware_please_register", "Пожалуйста, используйте /start для начала работы с ботом.")
            if event.message:
                try: await event.message.reply(please_register_text)
                except Exception as e_reply: logger.error(f"Не удалось отправить сообщение о регистр. {user_mention}: {e_reply}")
            elif event.callback_query:
                try: await event.callback_query.answer(please_register_text, show_alert=True)
                except Exception as e_answer: logger.error(f"Не удалось ответить на callback о регистр. {user_mention}: {e_answer}")
            return None 

        # 4. Если все проверки пройдены, ТОЛЬКО ТОГДА обновляем данные пользователя
        try:
            processed_user, created_flag = await user_service.process_user_on_start(aiogram_event_user)
            db_user = processed_user
            user_was_created_in_this_middleware_call = created_flag
            if not db_user:
                raise RuntimeError("process_user_on_start вернул None, что является критической ошибкой после проверок.")
        except Exception as e_process:
            logger.error(f"[{MODULE_NAME_FOR_LOG}] Критическая ошибка при обработке пользователя {user_mention} в UserService: {e_process}", exc_info=True)
            # Более информативные сообщения об ошибках
            if event.message: 
                await event.message.reply("Временная техническая проблема. Попробуйте позже или обратитесь к администратору.")
            elif event.callback_query: 
                await event.callback_query.answer("Техническая ошибка. Попробуйте позже.", show_alert=True)
            return None

        # 5. Передаем данные в хэндлер
        logger.trace(f"[{MODULE_NAME_FOR_LOG}] Пользователь {user_mention} (DB ID: {db_user.id}) проверки прошел. Доступ разрешен.")
        data['sdb_user'] = db_user
        if is_start_command:
            data['user_was_just_created'] = user_was_created_in_this_middleware_call
            logger.debug(f"[{MODULE_NAME_FOR_LOG}] Для /start пользователя {user_mention} установлен флаг user_was_just_created = {user_was_created_in_this_middleware_call}")

        return await handler(event, data)