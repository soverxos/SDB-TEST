# core/admin_auto_setup.py

from typing import TYPE_CHECKING
from loguru import logger
from sqlalchemy import select
from datetime import datetime, timezone

from core.database.core_models import User as DBUser, Role as DBRole
from core.rbac.service import DEFAULT_ROLE_ADMIN

if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider


class AdminAutoSetup:
    def __init__(self, services_provider: 'BotServicesProvider'):
        self._services = services_provider
        self._logger = logger.bind(service="AdminAutoSetup")

    async def ensure_super_admin_exists(self) -> bool:
        """
        Автоматически создает супер администратора из конфигурации, если он не существует.
        Возвращает True, если администратор был создан или уже существует.
        """
        try:
            super_admin_id = getattr(self._services.config.core, 'super_admin_telegram_id', None)
            
            # Проверяем .env переменную
            import os
            env_super_admin_id = os.getenv('SUPER_ADMIN_TELEGRAM_ID')
            if env_super_admin_id:
                try:
                    super_admin_id = int(env_super_admin_id)
                except ValueError:
                    self._logger.error(f"Некорректный SUPER_ADMIN_TELEGRAM_ID в .env: {env_super_admin_id}")
                    return False

            # Проверяем config.yaml
            if not super_admin_id:
                admin_config = getattr(self._services.config, 'admin', None)
                if admin_config:
                    super_admin_id = getattr(admin_config, 'super_admin_telegram_id', None)

            if not super_admin_id or super_admin_id == 123456789:  # дефолтное значение
                self._logger.warning("Супер администратор не настроен! Укажите SUPER_ADMIN_TELEGRAM_ID в .env или admin.super_admin_telegram_id в config.yaml")
                return False

            async with self._services.db.get_session() as session:
                # Проверяем, существует ли уже этот пользователь
                existing_user = await session.execute(
                    select(DBUser).where(DBUser.telegram_id == super_admin_id)
                )
                user = existing_user.scalars().first()

                if user:
                    self._logger.info(f"Супер администратор уже существует: TG ID {super_admin_id}, DB ID {user.id}")
                    
                    # Убеждаемся, что у него есть роль администратора
                    if hasattr(self._services, 'rbac') and self._services.rbac:
                        has_admin_role = await session.execute(
                            select(DBRole)
                            .join(DBUser.roles)
                            .where(DBUser.id == user.id)
                            .where(DBRole.name == DEFAULT_ROLE_ADMIN)
                        )
                        
                        if not has_admin_role.scalars().first():
                            # Назначаем роль администратора
                            await self._services.rbac.assign_role_to_user(session, user, DEFAULT_ROLE_ADMIN)
                            await session.commit()
                            self._logger.info(f"Роль администратора назначена пользователю TG ID {super_admin_id}")
                    
                    return True

                # Создаем нового супер администратора
                self._logger.info(f"Создаю супер администратора с TG ID: {super_admin_id}")
                
                new_admin = DBUser(
                    telegram_id=super_admin_id,
                    username=f"super_admin_{super_admin_id}",
                    username_lower=f"super_admin_{super_admin_id}",
                    first_name="Super",
                    last_name="Admin",
                    preferred_language_code="ru",
                    is_active=True,
                    is_bot_blocked=False,
                    last_activity_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(new_admin)
                await session.flush([new_admin])  # Получаем ID
                
                # Назначаем роль администратора
                if hasattr(self._services, 'rbac') and self._services.rbac:
                    await self._services.rbac.assign_role_to_user(session, new_admin, DEFAULT_ROLE_ADMIN)
                
                await session.commit()
                
                self._logger.success(f"✅ Супер администратор создан: TG ID {super_admin_id}, DB ID {new_admin.id}")
                return True

        except Exception as e:
            self._logger.error(f"Ошибка при создании супер администратора: {e}", exc_info=True)
            return False

    async def initialize(self):
        """Инициализация - вызывается при старте бота"""
        self._logger.info("🔧 Проверка супер администратора...")
        
        # Проверяем настройки автосоздания
        auto_create = True
        
        try:
            admin_config = getattr(self._services.config, 'admin', None)
            if admin_config:
                auto_create = getattr(admin_config, 'auto_create_super_admin', True)
        except:
            pass
            
        if auto_create:
            success = await self.ensure_super_admin_exists()
            if success:
                self._logger.info("✅ Супер администратор готов к работе")
            else:
                self._logger.error("❌ Не удалось настроить супер администратора")
        else:
            self._logger.info("Автоматическое создание супер администратора отключено")
