# core/services_provider.py

from typing import Optional, TYPE_CHECKING

from loguru import logger as global_logger 

if TYPE_CHECKING:
    from core.app_settings import AppSettings
    from core.database.manager import DBManager
    from core.cache.manager import CacheManager
    from core.http_client.manager import HTTPClientManager
    from core.module_loader import ModuleLoader
    from core.events.dispatcher import EventDispatcher
    from core.ui.registry_ui import UIRegistry
    from core.rbac.service import RBACService
    from core.users.service import UserService


class BotServicesProvider:
    def __init__(self, settings: 'AppSettings'):
        self._settings: 'AppSettings' = settings
        self._logger = global_logger.bind(service="BotServicesProvider")

        self._db_manager: Optional['DBManager'] = None
        self._cache_manager: Optional['CacheManager'] = None
        self._http_client_manager: Optional['HTTPClientManager'] = None
        self._module_loader: Optional['ModuleLoader'] = None
        self._event_dispatcher: Optional['EventDispatcher'] = None
        self._ui_registry: Optional['UIRegistry'] = None
        self._rbac_service: Optional['RBACService'] = None
        self._user_service: Optional['UserService'] = None

        self._logger.info(f"BotServicesProvider создан (версия SDB: {settings.core.sdb_version}). Ожидает настройки сервисов.")

    async def setup_services(self) -> None:
        self._logger.info("Начало асинхронной настройки основных сервисов SDB...")
        
        from core.database.manager import DBManager 
        try:
            self._db_manager = DBManager(db_settings=self._settings.db, app_settings=self._settings)
            await self._db_manager.initialize() 
            self._logger.success("Сервис DBManager успешно настроен.")
        except Exception as e:
            self._logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА настройки DBManager: {e}", exc_info=True)
            raise

        # Сначала инициализируем ModuleLoader, так как RBACService может от него зависеть для получения разрешений модулей
        from core.module_loader import ModuleLoader 
        try:
            self._module_loader = ModuleLoader(settings=self._settings, services_provider=self)
            self._module_loader.scan_all_available_modules() 
            self._module_loader._load_enabled_plugin_names() 
            self._logger.success(f"Сервис ModuleLoader инициализирован (найдено {len(self._module_loader.available_modules)} модулей, "
                                 f"активно плагинов {len(self._module_loader.enabled_plugin_names)}).")
        except Exception as e_mod_load:
            self._logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА инициализации ModuleLoader: {e_mod_load}", exc_info=True)
            raise 

        from core.rbac.service import RBACService 
        try:
            # Передаем self (BotServicesProvider) в RBACService
            self._rbac_service = RBACService(services=self) # <--- ИЗМЕНЕНИЕ ЗДЕСЬ
            if self._db_manager and self._rbac_service:
                try:
                    async with self._db_manager.get_session() as db_session:
                        # Вызываем ensure_default_entities_exist
                        roles_c, core_perms_c, mod_perms_c = await self._rbac_service.ensure_default_entities_exist(db_session) # <--- ИЗМЕНЕНИЕ ЗДЕСЬ
                        self._logger.info(f"RBACService.ensure_default_entities_exist отработал. "
                                          f"Ролей создано: {roles_c}, Разрешений ядра: {core_perms_c}, Разрешений модулей: {mod_perms_c}")
                except Exception as e_roles:
                    self._logger.error(f"Критическая ошибка при создании/проверке стандартных RBAC сущностей: {e_roles}", exc_info=True)
            self._logger.success("Сервис RBACService успешно настроен.")
        except ValueError as e_rbac_val: # Например, если DBManager не был передан
            self._logger.error(f"Ошибка инициализации RBACService (возможно, проблема с DBManager или ModuleLoader): {e_rbac_val}")
            self._rbac_service = None
        except Exception as e_rbac:
            self._logger.error(f"Не удалось настроить RBACService: {e_rbac}", exc_info=True)
            self._rbac_service = None 

        from core.users.service import UserService
        try:
            self._user_service = UserService(services_provider=self) 
            self._logger.success("Сервис UserService успешно настроен.")
        except Exception as e_user_svc:
            self._logger.error(f"Не удалось настроить UserService: {e_user_svc}", exc_info=True)
            self._user_service = None
        
        from core.cache.manager import CacheManager 
        try:
            self._cache_manager = CacheManager(cache_settings=self._settings.cache)
            await self._cache_manager.initialize()
            if self._cache_manager.is_available():
                 self._logger.success(f"Сервис CacheManager ({self._settings.cache.type}) успешно настроен.")
            else:
                 self._logger.warning(f"CacheManager ({self._settings.cache.type}) инициализирован, но кэш недоступен.")
        except ImportError as e_cache_imp: 
             self._logger.warning(f"Не удалось инициализировать CacheManager: {e_cache_imp}")
        except Exception as e_cache:
            self._logger.error(f"Ошибка настройки CacheManager: {e_cache}", exc_info=True)
            self._cache_manager = None

        from core.http_client.manager import HTTPClientManager 
        try:
            self._http_client_manager = HTTPClientManager(app_settings=self._settings) 
            await self._http_client_manager.initialize()
            if self._http_client_manager.is_available():
                self._logger.success("Сервис HTTPClientManager успешно настроен.")
            else:
                self._logger.warning("HTTPClientManager инициализирован, но HTTP-клиент недоступен.")
        except ImportError as e_http_imp: 
            self._logger.warning(f"Не удалось инициализировать HTTPClientManager: {e_http_imp}")
        except Exception as e_http:
            self._logger.error(f"Ошибка настройки HTTPClientManager: {e_http}", exc_info=True)
            self._http_client_manager = None

        from core.events.dispatcher import EventDispatcher 
        try:
            self._event_dispatcher = EventDispatcher()
            self._logger.success("Сервис EventDispatcher успешно инициализирован.")
        except Exception as e_event:
            self._logger.error(f"Ошибка инициализации EventDispatcher: {e_event}", exc_info=True)
            self._event_dispatcher = None

        from core.ui.registry_ui import UIRegistry 
        try:
            self._ui_registry = UIRegistry()
            self._logger.success("Сервис UIRegistry успешно инициализирован.")
        except Exception as e_ui_reg:
            self._logger.error(f"Ошибка инициализации UIRegistry: {e_ui_reg}", exc_info=True)
            self._ui_registry = None
        
        # ModuleLoader уже инициализирован выше

        self._logger.info("✅ Первичная настройка всех основных сервисов SDB завершена.")


    async def close_services(self) -> None:
        self._logger.info("Начало процедуры закрытия и освобождения ресурсов сервисов SDB...")
        
        if self._module_loader: self._logger.debug("ModuleLoader не требует специального dispose().")
        if self._ui_registry:
            try: await self._ui_registry.dispose(); self._logger.info("UIRegistry ресурсы освобождены.")
            except Exception as e: self._logger.error(f"Ошибка при освобождении UIRegistry: {e}", exc_info=True)
        if self._event_dispatcher:
            try: await self._event_dispatcher.dispose(); self._logger.info("EventDispatcher ресурсы освобождены.")
            except Exception as e: self._logger.error(f"Ошибка при освобождении EventDispatcher: {e}", exc_info=True)
        if self._http_client_manager:
            try: await self._http_client_manager.dispose(); self._logger.info("HTTPClientManager ресурсы освобождены.")
            except Exception as e: self._logger.error(f"Ошибка при освобождении HTTPClientManager: {e}", exc_info=True)
        if self._cache_manager:
            try: await self._cache_manager.dispose(); self._logger.info("CacheManager ресурсы освобождены.")
            except Exception as e: self._logger.error(f"Ошибка при освобождении CacheManager: {e}", exc_info=True)
        
        if self._user_service: self._logger.debug("UserService не требует специального dispose().")
        if self._rbac_service: self._logger.debug("RBACService не требует специального dispose().")
        
        if self._db_manager:
            try: await self._db_manager.dispose(); self._logger.info("DBManager ресурсы освобождены.")
            except Exception as e: self._logger.error(f"Ошибка при освобождении DBManager: {e}", exc_info=True)
        
        self._logger.info("🏁 Процедура закрытия всех сервисов SDB завершена.")
    
    @property
    def config(self) -> 'AppSettings':
        return self._settings

    @property
    def logger(self):
        return global_logger 

    @property
    def db(self) -> 'DBManager':
        if self._db_manager is None:
            msg = "DBManager не инициализирован! Обращение к БД невозможно."
            self._logger.critical(msg)
            raise RuntimeError(msg)
        return self._db_manager

    @property
    def rbac(self) -> 'RBACService':
        if self._rbac_service is None:
            msg = "RBACService не инициализирован! Функции RBAC будут недоступны."
            self._logger.error(msg) 
            raise AttributeError(msg) 
        return self._rbac_service
    
    @property
    def user_service(self) -> 'UserService':
        if self._user_service is None:
            msg = "UserService не инициализирован! Функции управления пользователями будут недоступны."
            self._logger.error(msg)
            raise AttributeError(msg)
        return self._user_service

    @property
    def cache(self) -> 'CacheManager':
        if self._cache_manager is None or not self._cache_manager.is_available():
            # msg = "CacheManager не инициализирован или кэш недоступен!" # Закомментировано чтобы не спамить, если кэш опционален
            # self._logger.warning(msg)
            raise AttributeError("CacheManager не инициализирован или кэш недоступен! Попытка использовать недоступный кэш.")
        return self._cache_manager

    @property
    def http(self) -> 'HTTPClientManager': 
        if self._http_client_manager is None or not self._http_client_manager.is_available():
            raise AttributeError("HTTPClientManager не инициализирован или HTTP-клиент недоступен! Попытка использовать недоступный HTTP-клиент.")
        return self._http_client_manager

    @property
    def modules(self) -> 'ModuleLoader': 
        if self._module_loader is None:
            msg = "ModuleLoader не инициализирован!" 
            self._logger.critical(msg)
            raise RuntimeError(msg)
        return self._module_loader

    @property
    def events(self) -> 'EventDispatcher':
        if self._event_dispatcher is None:
            msg = "EventDispatcher не инициализирован!"
            self._logger.error(msg) 
            raise AttributeError(msg)
        return self._event_dispatcher
    
    @property
    def ui_registry(self) -> 'UIRegistry':
        if self._ui_registry is None:
            msg = "UIRegistry не инициализирован!"
            self._logger.error(msg)
            raise AttributeError(msg)
        return self._ui_registry