# SwiftDevBot/core/ui/callback_data_factories.py
from typing import Optional, Literal, Union, Any, Dict 
from aiogram.filters.callback_data import CallbackData
from .callback_data_manager import callback_data_manager

CORE_CALLBACK_PREFIX = "sdb_core"
ADMIN_CALLBACK_PREFIX = "sdb_admin" 


class SmartCallbackData(CallbackData, prefix="smart_base"):
    """Базовый класс для callback_data с автоматическим сжатием"""
    
    def pack(self) -> str:
        """Упаковка данных с автоматическим сжатием при необходимости"""
        # Создаем словарь с данными
        data_dict = {
            "prefix": self.__class__.__prefix__,
        }
        
        # Добавляем все поля объекта
        for field_name, field_info in self.__class__.__annotations__.items():
            if field_name == 'prefix':
                continue
            value = getattr(self, field_name, None)
            if value is not None:
                data_dict[field_name] = value
        
        # Используем менеджер для создания callback_data
        return callback_data_manager.create_callback_data(data_dict)
    
    @classmethod
    def unpack(cls, value: str):
        """Распаковка данных с поддержкой сжатых данных"""
        # Получаем данные через менеджер
        data = callback_data_manager.get_callback_data(value)
        
        if data is None:
            raise ValueError(f"Cannot unpack callback data: {value}")
        
        # Проверяем префикс
        if data.get("prefix") != cls.__prefix__:
            raise ValueError(f"Invalid prefix for {cls.__name__}")
        
        # Создаем экземпляр
        kwargs = {}
        for field_name in cls.__annotations__.keys():
            if field_name == 'prefix':
                continue
            if field_name in data:
                kwargs[field_name] = data[field_name]
        
        return cls(**kwargs)


# --- Фабрики для навигации ядра ---
class CoreMenuNavigate(SmartCallbackData, prefix=f"{CORE_CALLBACK_PREFIX}_nav"):
    target_menu: str 
    page: Optional[int] = None
    action: Optional[str] = None 
    # Добавим параметр для передачи данных, например, кода языка
    payload: Optional[str] = None 

class ModuleMenuEntry(SmartCallbackData, prefix=f"{CORE_CALLBACK_PREFIX}_module_entry"):
    module_name: str

class CoreServiceAction(SmartCallbackData, prefix=f"{CORE_CALLBACK_PREFIX}_service"):
    action: Literal[
        "delete_this_message", 
        "close_menu_silently",
        "confirm_registration", 
        "cancel_registration",
    ]

# --- Фабрики для Админ-панели ---
ADMIN_MAIN_MENU_PREFIX = "sdb_admin_main"
class AdminMainMenuNavigate(SmartCallbackData, prefix=ADMIN_MAIN_MENU_PREFIX):
    target_section: str 

ADMIN_USERS_PREFIX = "sdb_admin_users"
class AdminUsersPanelNavigate(SmartCallbackData, prefix="sdb_admin_users"):
    """
    Структура данных для навигации по админ-панели пользователей
    """
    action: str
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    permission_id: Optional[int] = None
    permission_code: Optional[str] = None
    page: Optional[int] = None
    module_name: Optional[str] = None
    permission_type: Optional[str] = None
    category_key: Optional[str] = None
    entity_name: Optional[str] = None


ADMIN_ROLES_PREFIX = "sdb_admin_roles"
class AdminRolesPanelNavigate(SmartCallbackData, prefix=ADMIN_ROLES_PREFIX):
    action: str 
    item_id: Optional[int] = None       
    permission_id: Optional[int] = None 
    category_key: Optional[str] = None  
    entity_name: Optional[str] = None   
    page: Optional[int] = None          

ADMIN_SYSINFO_PREFIX = "sdb_admin_sysinfo"
class AdminSysInfoPanelNavigate(SmartCallbackData, prefix=ADMIN_SYSINFO_PREFIX):
    action: str 

ADMIN_MODULES_PREFIX = "sdb_admin_modules"
class AdminModulesPanelNavigate(SmartCallbackData, prefix=ADMIN_MODULES_PREFIX):
    action: str 
    item_id: Optional[str] = None 
    page: Optional[int] = None

ADMIN_LOGS_PREFIX = "sdb_admin_logs"
class AdminLogsPanelNavigate(SmartCallbackData, prefix=ADMIN_LOGS_PREFIX):
    action: str 
    item_id: Optional[str] = None 
    page: Optional[int] = None

class AdminPanelNavigate(SmartCallbackData, prefix=ADMIN_CALLBACK_PREFIX): 
    section: str 
    action: Optional[str] = None
    item_id: Optional[Union[int, str]] = None 
    page: Optional[int] = None
    role_id: Optional[int] = None 
    permission_name: Optional[str] = None