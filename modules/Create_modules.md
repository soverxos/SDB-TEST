
**Структура папки универсального модуля (например, `modules/my_universal_module/`)**

```
my_universal_module/
├── __init__.py                   # ОБЯЗАТЕЛЬНО: Точка входа модуля
├── manifest.yaml                 # ОБЯЗАТЕЛЬНО: Описание модуля
├── handlers.py                   # РЕКОМЕНДУЕТСЯ: Основные хэндлеры сообщений и колбэков
├── keyboards.py                  # РЕКОМЕНДУЕТСЯ: Функции для генерации клавиатур
├── callback_data.py              # РЕКОМЕНДУЕТСЯ: Фабрики CallbackData для модуля
├── permissions.py                # РЕКОМЕНДУЕТСЯ: Определение констант разрешений модуля
├── states.py                     # ОПЦИОНАЛЬНО: Состояния FSM, если модуль их использует
├── models.py                     # ОПЦИОНАЛЬНО: Модели SQLAlchemy, если модуль работает с БД
├── module_settings_defaults.yaml # ОПЦИОНАЛЬНО: Файл с настройками по умолчанию для модуля
└── services.py                   # ОПЦИОНАЛЬНО: Вспомогательные сервисы или логика модуля
```

---

**Содержимое файлов с комментариями:**

**1. `modules/my_universal_module/manifest.yaml` (ОБЯЗАТЕЛЬНО)**

```yaml
# ОБЯЗАТЕЛЬНО: Уникальное имя модуля в snake_case. Должно совпадать с именем папки.
name: "my_universal_module" 

# ОБЯЗАТЕЛЬНО: Отображаемое имя модуля для пользователя.
display_name: "Мой Универсальный Модуль"

# ОБЯЗАТЕЛЬНО: Версия модуля в формате SemVer (например, "0.1.0", "1.0.0-beta.1").
version: "0.1.0"

# РЕКОМЕНДУЕТСЯ: Краткое описание функциональности модуля.
description: "Этот модуль демонстрирует универсальную структуру и лучшие практики для создания модулей SwiftDevBot."

# РЕКОМЕНДУЕТСЯ: Имя или ник автора/команды разработчиков.
author: "Ваше Имя / Название Команды"

# ОПЦИОНАЛЬНО: Список Python-зависимостей, которые требуются этому модулю.
# Эти зависимости должны быть установлены в окружение отдельно.
# Формат: как в requirements.txt (например, "requests>=2.20.0", "beautifulsoup4")
python_requirements:
  # - "some_package==1.2.3"

# ОПЦИОНАЛЬНО: Список других модулей SDB, от которых зависит этот модуль.
# Ядро проверит их наличие и активность перед загрузкой этого модуля.
# Указываются 'name' модулей-зависимостей.
sdb_module_dependencies:
  # - "another_sdb_module_name"

# ОПЦИОНАЛЬНО: Список полных путей к классам моделей SQLAlchemy, определенных в этом модуле.
# Используется CLI командой 'sdb module clean-tables' для удаления таблиц модуля.
# Пример: "modules.my_universal_module.models.MyTableModel"
model_definitions:
  # - "modules.my_universal_module.models.MyFirstTable"
  # - "modules.my_universal_module.models.MySecondTable"

# ОПЦИОНАЛЬНО: Список команд, которые предоставляет модуль.
# Будут добавлены в общее меню команд бота (если admin_only=false).
commands:
  - command: "universal_hello" # Сама команда (без "/")
    description: "Сказать привет от универсального модуля" # Описание для /help
    icon: "👋" # Опциональная иконка
    category: "Универсальные" # Опциональная категория
    admin_only: false # Требует ли команда прав администратора (для показа в /help)
                      # Фактическая проверка прав должна быть в хэндлере!
  # - command: "universal_admin_action"
  #   description: "Выполнить административное действие модуля"
  #   icon: "🛠️"
  #   category: "Универсальные (Админ)"
  #   admin_only: true # Не будет показана в /help обычным пользователям

# ОПЦИОНАЛЬНО: Разрешения, которые объявляет и использует этот модуль.
# Имена должны быть в формате "module_name.permission_key".
# Описание используется в админ-панели при назначении прав ролям.
permissions:
  - name: "my_universal_module.access" # Базовое право на доступ/использование модуля
    description: "Доступ к основным функциям Универсального Модуля."
  - name: "my_universal_module.view_sensitive_data"
    description: "Просмотр чувствительных данных в Универсальном Модуле."
  - name: "my_universal_module.perform_special_action"
    description: "Выполнение специального действия в Универсальном Модуле."
  # - name: "my_universal_module.admin_manage"
  #   description: "[АДМИН] Полное управление Универсальным Модулем."

# ОПЦИОНАЛЬНО: Настройки модуля, которые администратор может изменять.
# Ключ словаря (здесь 'greeting_message') будет именем настройки.
settings:
  greeting_message:
    type: "string" # Типы: string, int, float, bool, choice, multichoice, text
    label: "Приветственное сообщение" # Отображаемое имя настройки
    description: "Сообщение, которое модуль будет использовать для приветствия." # Описание
    default: "Привет от Универсального Модуля!" # Значение по умолчанию
    required: false # Обязательна ли настройка (если true, default должен быть указан)
  # enable_feature_x:
  #   type: "bool"
  #   label: "Включить Функцию X"
  #   default: true
  # item_limit:
  #   type: "int"
  #   label: "Лимит элементов"
  #   default: 10
  #   min_value: 1
  #   max_value: 100
  # theme_color:
  #   type: "choice"
  #   label: "Цветовая схема"
  #   default: "blue"
  #   options:
  #     - value: "blue"
  #       display_name: "Синяя"
  #     - value: "green"
  #       display_name: "Зеленая"
  #     - "red" # Можно и так, если display_name не нужен
  # admin_email:
  #   type: "string"
  #   label: "Email администратора модуля"
  #   regex_validator: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$" # Пример валидации email
  #   required: true # default здесь не нужен, если required и ожидается ввод от админа

# ОПЦИОНАЛЬНО: Информация о фоновых задачах, если модуль их использует.
# 'entry_point' - полный путь к асинхронной функции задачи.
# 'schedule' - cron-подобная строка для планировщика (если используется).
background_tasks:
  # daily_cleanup:
  #   entry_point: "modules.my_universal_module.tasks.run_daily_cleanup"
  #   schedule: "0 3 * * *" # Каждый день в 3:00
  #   description: "Ежедневная очистка временных данных модуля."

# ОПЦИОНАЛЬНО: Дополнительная метаинформация о модуле.
metadata:
  homepage: "https://example.com/my_universal_module" # URL домашней страницы модуля
  license: "MIT" # Лицензия модуля
  tags: ["universal", "template", "example"] # Теги для поиска/категоризации
  min_sdb_core_version: "0.1.0" # Минимальная совместимая версия ядра SDB
  assign_default_access_to_user_role: true # Если true, право '{module_name}.access' будет автоматически назначено роли 'User'
                                           # Имя базового права доступа должно быть '{module_name}.access_user_features' или '{module_name}.access'
                                           # В нашем случае это "my_universal_module.access" (см. permissions выше)
```

---

**2. `modules/my_universal_module/__init__.py` (ОБЯЗАТЕЛЬНО)**

```python
# modules/my_universal_module/__init__.py

from aiogram import Dispatcher, Bot, Router
from loguru import logger

# РЕКОМЕНДУЕТСЯ: Импортировать основной роутер модуля
from .handlers import universal_module_router 
# ОБЯЗАТЕЛЬНО: Импортировать имя модуля (должно совпадать с 'name' в манифесте)
from .permissions import MODULE_NAME 
# РЕКОМЕНДУЕТСЯ: Импортировать базовое разрешение для UI точки входа
from .permissions import PERM_ACCESS_USER_FEATURES 

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from core.module_loader import ModuleInfo # Для получения информации о модуле

async def setup_module(dp: Dispatcher, bot: Bot, services: 'BotServicesProvider'):
    """
    ОБЯЗАТЕЛЬНАЯ функция. Вызывается ядром для инициализации модуля.
    Здесь происходит регистрация хэндлеров, UI-точек входа, подписка на события и т.д.
    """
    
    # Получение информации о модуле (включая манифест и загруженные настройки)
    module_info: Optional['ModuleInfo'] = services.modules.get_module_info(MODULE_NAME)
    
    if not module_info or not module_info.manifest:
        logger.error(f"Не удалось получить информацию или манифест для модуля '{MODULE_NAME}'. "
                     "Модуль не будет настроен.")
        return

    # Логирование начала настройки модуля
    display_name = module_info.manifest.display_name
    version = module_info.manifest.version
    logger.info(f"[{MODULE_NAME}] Настройка модуля: '{display_name}' v{version}...")

    # 1. РЕКОМЕНДУЕТСЯ: Регистрация хэндлеров (роутеров) этого модуля
    if isinstance(universal_module_router, Router):
        # ОПЦИОНАЛЬНО: Можно добавить фильтр на весь роутер модуля,
        # например, чтобы он работал только в личных чатах или для пользователей с определенным правом.
        # universal_module_router.message.filter(F.chat.type == "private") 
        dp.include_router(universal_module_router)
        logger.info(f"[{MODULE_NAME}] Роутер '{universal_module_router.name}' успешно зарегистрирован.")
    else:
        logger.error(f"[{MODULE_NAME}] Ошибка: 'universal_module_router' не является экземпляром aiogram.Router.")

    # 2. РЕКОМЕНДУЕТСЯ: Регистрация UI-точки входа модуля в UIRegistry ядра
    # Это позволит модулю появиться в общем списке "Модули" в UI ядра.
    # Callback_data для входа в модуль будет ModuleMenuEntry(module_name=MODULE_NAME).pack()
    # Хэндлер для этого callback_data должен быть определен в handlers.py.
    
    # Импортируем фабрику ModuleMenuEntry из ядра
    from core.ui.callback_data_factories import ModuleMenuEntry 

    entry_cb_data = ModuleMenuEntry(module_name=MODULE_NAME).pack()
    
    # ОПЦИОНАЛЬНО: Иконка и описание для кнопки в меню "Модули"
    icon = "✨" # Дефолтная иконка
    # Попробуем взять иконку из первой команды в манифесте, если она есть
    if module_info.manifest.commands:
        primary_command_name = MODULE_NAME # Или другое имя команды, которую считаем главной
        main_command_manifest = next((cmd for cmd in module_info.manifest.commands if cmd.command == primary_command_name), None)
        if not main_command_manifest and module_info.manifest.commands: # Если нет команды с именем модуля, берем первую
             main_command_manifest = module_info.manifest.commands[0]
        
        if main_command_manifest and main_command_manifest.icon:
            icon = main_command_manifest.icon

    description_for_ui = module_info.manifest.description or f"Функционал модуля {display_name}"

    services.ui_registry.register_module_entry(
        module_name=MODULE_NAME, 
        display_name=display_name,
        entry_callback_data=entry_cb_data, 
        icon=icon,
        description=description_for_ui,
        order=100, # Порядок в общем списке модулей (меньше - выше)
        # ОБЯЗАТЕЛЬНО, если хотите, чтобы доступ к кнопке модуля в общем меню "Модули"
        # проверялся автоматически ядром:
        required_permission_to_view=PERM_ACCESS_USER_FEATURES 
    )
    logger.info(f"[{MODULE_NAME}] UI-точка входа для модуля '{display_name}' зарегистрирована в UIRegistry.")

    # 3. ОПЦИОНАЛЬНО: Инициализация специфичных для модуля сервисов или задач
    # if hasattr(self, 'my_module_service'): # Если есть свой сервис
    #     await self.my_module_service.initialize(services_provider=services)
    #     logger.info(f"[{MODULE_NAME}] Внутренний сервис MyModuleService инициализирован.")

    # 4. ОПЦИОНАЛЬНО: Подписка на события ядра или других модулей
    # async def handle_user_registered_event(user_id: int, source_module: str):
    #     logger.info(f"[{MODULE_NAME}] Получено событие 'sdb:user:registered'. Пользователь: {user_id} из {source_module}")
    # services.events.subscribe("sdb:user:registered", handle_user_registered_event)
    # logger.info(f"[{MODULE_NAME}] Подписан на событие 'sdb:user:registered'.")

    # 5. ОПЦИОНАЛЬНО: Публикация собственных событий модуля, если это нужно для других модулей
    # await services.events.publish(f"{MODULE_NAME}:initialized", module_version=version)

    logger.success(f"✅ Модуль '{MODULE_NAME}' ({display_name} v{version}) успешно настроен.")
```

---

**3. `modules/my_universal_module/permissions.py` (РЕКОМЕНДУЕТСЯ)**

```python
# modules/my_universal_module/permissions.py

# ОБЯЗАТЕЛЬНО: Уникальное имя модуля, должно совпадать с именем папки и 'name' в manifest.yaml
MODULE_NAME = "my_universal_module"

# РЕКОМЕНДУЕТСЯ: Базовое разрешение для доступа к пользовательскому интерфейсу и основным функциям модуля.
# Его можно автоматически назначать роли 'User', если в manifest.yaml metadata.assign_default_access_to_user_role: true
PERM_ACCESS_USER_FEATURES = f"{MODULE_NAME}.access_user_features"

# ОПЦИОНАЛЬНО: Примеры других разрешений, специфичных для этого модуля
PERM_VIEW_SENSITIVE_DATA = f"{MODULE_NAME}.view_sensitive_data"
PERM_PERFORM_SPECIAL_ACTION = f"{MODULE_NAME}.perform_special_action"

# ОПЦИОНАЛЬНО: Разрешения для административных функций внутри модуля
PERM_ADMIN_MANAGE_SETTINGS = f"{MODULE_NAME}.admin_manage_settings"
PERM_ADMIN_VIEW_ALL_DATA = f"{MODULE_NAME}.admin_view_all_data"

# Для удобства можно собрать все разрешения модуля в один список или словарь,
# но это необязательно, так как они будут зарегистрированы из манифеста.
ALL_MODULE_PERMISSIONS = {
    PERM_ACCESS_USER_FEATURES: "Доступ к основным функциям Универсального Модуля.",
    PERM_VIEW_SENSITIVE_DATA: "Просмотр чувствительных данных в Универсальном Модуле.",
    PERM_PERFORM_SPECIAL_ACTION: "Выполнение специального действия в Универсальном Модуле.",
    PERM_ADMIN_MANAGE_SETTINGS: "[АДМИН] Управление настройками Универсального Модуля.",
    PERM_ADMIN_VIEW_ALL_DATA: "[АДМИН] Просмотр всех данных Универсального Модуля.",
}
# Этот словарь ALL_MODULE_PERMISSIONS здесь просто для примера,
# описания для регистрации берутся из manifest.yaml.
```

---

**4. `modules/my_universal_module/handlers.py` (РЕКОМЕНДУЕТСЯ)**

```python
# modules/my_universal_module/handlers.py

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from loguru import logger

# РЕКОМЕНДУЕТСЯ: Импорт фабрик колбэков этого модуля и фабрик ядра для навигации
from .callback_data import MyUniversalModuleAction
from core.ui.callback_data_factories import ModuleMenuEntry 

# РЕКОМЕНДУЕТСЯ: Импорт функций для генерации клавиатур этого модуля
from .keyboards import get_universal_module_main_menu_keyboard

# РЕКОМЕНДУЕТСЯ: Импорт констант разрешений этого модуля
from .permissions import (
    MODULE_NAME,
    PERM_ACCESS_USER_FEATURES,
    PERM_VIEW_SENSITIVE_DATA,
    PERM_PERFORM_SPECIAL_ACTION
)

# ОПЦИОНАЛЬНО: Импорт FSM состояний, если используются
# from .states import MyFSMState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession # Для проверок прав

# ОБЯЗАТЕЛЬНО: Создание роутера для этого модуля
universal_module_router = Router(name=f"sdb_{MODULE_NAME}_handlers")

# --- Вспомогательная функция для проверки прав (может быть общей для модуля) ---
async def check_module_permission(
    user_id: int, 
    permission_name: str, 
    services: 'BotServicesProvider', 
    session: 'AsyncSession' # Передаем сессию явно
) -> bool:
    has_perm = await services.rbac.user_has_permission(session, user_id, permission_name)
    if not has_perm:
        logger.warning(f"[{MODULE_NAME}] Пользователь {user_id} попытался выполнить действие, требующее права "
                       f"'{permission_name}', но не имеет его.")
    return has_perm

# --- Обработчик команды входа в модуль (пример) ---
@universal_module_router.message(Command(MODULE_NAME)) # Команда совпадает с именем модуля
async def cmd_universal_module_entry(message: types.Message, services_provider: 'BotServicesProvider'):
    user_id = message.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вызвал команду /{MODULE_NAME}.")

    async with services_provider.db.get_session() as session:
        if not await check_module_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await message.answer("У вас нет доступа к этому модулю.")
            return
    
    module_info = services_provider.modules.get_module_info(MODULE_NAME)
    display_name = module_info.manifest.display_name if module_info and module_info.manifest else MODULE_NAME

    text = f"🌟 Добро пожаловать в {hbold(display_name)}!"
    async with services_provider.db.get_session() as session: # Новая сессия для клавиатуры
        keyboard = await get_universal_module_main_menu_keyboard(services_provider, user_id, session)
    await message.answer(text, reply_markup=keyboard)

# --- Обработчик входа в меню модуля через общий список модулей ---
@universal_module_router.callback_query(ModuleMenuEntry.filter(F.module_name == MODULE_NAME))
async def cq_universal_module_main_menu(
    query: types.CallbackQuery, 
    services_provider: 'BotServicesProvider'
):
    user_id = query.from_user.id
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} вошел в меню модуля '{MODULE_NAME}'.")
    
    async with services_provider.db.get_session() as session:
        if not await check_module_permission(user_id, PERM_ACCESS_USER_FEATURES, services_provider, session):
            await query.answer("У вас нет доступа к этому меню.", show_alert=True)
            return

        module_info = services_provider.modules.get_module_info(MODULE_NAME)
        display_name = module_info.manifest.display_name if module_info and module_info.manifest else MODULE_NAME
        text = f"Меню модуля {hbold(display_name)}. Выберите действие:"
        keyboard = await get_universal_module_main_menu_keyboard(services_provider, user_id, session)

        if query.message:
            try:
                await query.message.edit_text(text, reply_markup=keyboard)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e).lower():
                    logger.warning(f"[{MODULE_NAME}] Ошибка edit_text в меню модуля: {e}")
            await query.answer()

# --- Обработчики действий модуля ---
@universal_module_router.callback_query(MyUniversalModuleAction.filter(F.action == "view_data"))
async def cq_view_module_data(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        # Для этого действия не требуется спец. разрешение, только PERM_ACCESS_USER_FEATURES (уже проверено при входе в меню)
        # Здесь будет логика получения данных, специфичных для пользователя
        # Например, если модуль хранит персональные данные пользователя
        
        # Доступ к настройкам модуля, если они нужны
        module_settings = services_provider.modules.get_module_settings(MODULE_NAME)
        greeting = module_settings.get("greeting_message", "Привет!") if module_settings else "Привет!"

        await query.answer(f"{greeting} Вот ваши данные из модуля!", show_alert=False)
        logger.info(f"[{MODULE_NAME}] Пользователь {user_id} просмотрел свои данные.")

@universal_module_router.callback_query(MyUniversalModuleAction.filter(F.action == "view_sensitive"))
async def cq_view_sensitive_data(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_module_permission(user_id, PERM_VIEW_SENSITIVE_DATA, services_provider, session):
            await query.answer("У вас нет прав для просмотра этой информации.", show_alert=True)
            return
    await query.answer("Это очень чувствительные данные!", show_alert=True)
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} просмотрел чувствительные данные.")


@universal_module_router.callback_query(MyUniversalModuleAction.filter(F.action == "special_action"))
async def cq_do_special_action(query: types.CallbackQuery, services_provider: 'BotServicesProvider'):
    user_id = query.from_user.id
    async with services_provider.db.get_session() as session:
        if not await check_module_permission(user_id, PERM_PERFORM_SPECIAL_ACTION, services_provider, session):
            await query.answer("Это специальное действие доступно не всем.", show_alert=True)
            return
    await query.answer("✨ Специальное действие выполнено! ✨", show_alert=True)
    logger.info(f"[{MODULE_NAME}] Пользователь {user_id} выполнил специальное действие.")

# ОПЦИОНАЛЬНО: Хэндлеры для административных действий модуля (если есть)
# @universal_module_router.message(Command("universal_admin_manage"))
# async def cmd_admin_manage_module(message: types.Message, services_provider: 'BotServicesProvider'):
#     user_id = message.from_user.id
#     async with services_provider.db.get_session() as session:
#         if not await check_module_permission(user_id, PERM_ADMIN_MANAGE_MODULE, services_provider, session):
#             await message.answer("У вас нет прав для администрирования этого модуля.")
#             return
#     await message.answer("Добро пожаловать в админ-панель Универсального Модуля!")
```

---

**5. `modules/my_universal_module/keyboards.py` (РЕКОМЕНДУЕТСЯ)**

```python
# modules/my_universal_module/keyboards.py

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# РЕКОМЕНДУЕТСЯ: Импорт фабрик для этого модуля
from .callback_data import MyUniversalModuleAction
# РЕКОМЕНДУЕТСЯ: Импорт фабрик ядра для стандартной навигации (назад и т.д.)
from core.ui.callback_data_factories import CoreMenuNavigate 
# РЕКОМЕНДУЕТСЯ: Импорт констант разрешений для динамического отображения кнопок
from .permissions import PERM_VIEW_SENSITIVE_DATA, PERM_PERFORM_SPECIAL_ACTION

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_universal_module_main_menu_keyboard(
    services: 'BotServicesProvider', 
    user_id: int, 
    session: 'AsyncSession' # Нужна для проверки прав
) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру для главного меню универсального модуля.
    Кнопки отображаются в зависимости от прав пользователя.
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка 1: Простое действие, доступное с базовым разрешением (PERM_ACCESS_USER_FEATURES)
    # Право PERM_ACCESS_USER_FEATURES уже должно быть проверено перед показом этого меню.
    builder.button(
        text="📊 Посмотреть мои данные",
        callback_data=MyUniversalModuleAction(action="view_data").pack()
    )

    # Кнопка 2: Доступна только при наличии разрешения PERM_VIEW_SENSITIVE_DATA
    if await services.rbac.user_has_permission(session, user_id, PERM_VIEW_SENSITIVE_DATA):
        builder.button(
            text="🔒 Просмотреть чувствительные данные",
            callback_data=MyUniversalModuleAction(action="view_sensitive").pack()
        )

    # Кнопка 3: Доступна только при наличии разрешения PERM_PERFORM_SPECIAL_ACTION
    if await services.rbac.user_has_permission(session, user_id, PERM_PERFORM_SPECIAL_ACTION):
        builder.button(
            text="🚀 Выполнить специальное действие",
            callback_data=MyUniversalModuleAction(action="special_action").pack()
        )

    # Если ни одна из "основных" кнопок не была добавлена (из-за отсутствия прав),
    # можно добавить информационную кнопку.
    if not builder.export(): # Проверяем, были ли добавлены какие-либо кнопки выше
         builder.button(text="🤷‍♂️ Нет доступных действий", callback_data="my_universal_module:no_actions_dummy")


    # Кнопка "Назад" в общее меню модулей SDB
    builder.button(
        text="⬅️ Назад к списку модулей",
        callback_data=CoreMenuNavigate(target_menu="modules_list", page=1).pack() 
    )
    
    builder.adjust(1) # Каждая кнопка на новой строке
    return builder.as_markup()
```

---

**6. `modules/my_universal_module/callback_data.py` (РЕКОМЕНДУЕТСЯ)**

```python
# modules/my_universal_module/callback_data.py

from aiogram.filters.callback_data import CallbackData
from typing import Optional

# РЕКОМЕНДУЕТСЯ: Уникальный префикс для колбэков этого модуля
MY_UNIVERSAL_MODULE_PREFIX = "muniv" 

class MyUniversalModuleAction(CallbackData, prefix=MY_UNIVERSAL_MODULE_PREFIX):
    # ОБЯЗАТЕЛЬНО: Поле 'action' для определения типа действия
    action: str 
    
    # ОПЦИОНАЛЬНО: Дополнительные поля, если нужны для передачи данных
    item_id: Optional[int] = None
    page: Optional[int] = None
    # ... другие поля
```

---

**7. `modules/my_universal_module/states.py` (ОПЦИОНАЛЬНО)**

```python
# modules/my_universal_module/states.py

from aiogram.fsm.state import State, StatesGroup

# ОПЦИОНАЛЬНО: Определите здесь состояния FSM, если ваш модуль их использует.
class MyUniversalModuleFSM(StatesGroup):
    first_step = State()
    second_step = State()
    # ... другие состояния
```

---

**8. `modules/my_universal_module/models.py` (ОПЦИОНАЛЬНО)**
(Мы уже добавили `UserNote` в предыдущем примере, здесь может быть больше моделей)

```python
# modules/my_universal_module/models.py
from sqlalchemy import String, Integer, ForeignKey, Text, Boolean 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import SDBBaseModel 
from typing import Optional

# Пример модели для этого модуля
class MyFirstTable(SDBBaseModel): 
    __tablename__ = "mod_universal_my_first_table" # РЕКОМЕНДУЕТСЯ: Префикс mod_{module_name}_
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self):
        return f"<MyFirstTable(id={self.id}, name='{self.name}')>"

# Не забудьте добавить "modules.my_universal_module.models.MyFirstTable"
# в 'model_definitions' в manifest.yaml, если хотите, чтобы CLI мог ее чистить.
```

---

**9. `modules/my_universal_module/module_settings_defaults.yaml` (ОПЦИОНАЛЬНО)**

Файл с настройками по умолчанию для модуля. Имена ключей должны совпадать с теми, что описаны в секции `settings` файла `manifest.yaml`.

```yaml
# modules/my_universal_module/module_settings_defaults.yaml

greeting_message: "Универсальный модуль приветствует вас (из файла дефолтов)!"
enable_feature_x: false
item_limit: 5
# theme_color: "green" # Если это значение есть в options в манифесте
# admin_email: # Обязательные поля без default в манифесте должны быть заданы в пользовательском конфиге
```

---

**10. `modules/my_universal_module/services.py` (ОПЦИОНАЛЬНО)**

Здесь можно разместить вспомогательные классы, функции, бизнес-логику, специфичную для этого модуля.

```python
# modules/my_universal_module/services.py

from loguru import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.services_provider import BotServicesProvider
    from sqlalchemy.ext.asyncio import AsyncSession

class UniversalModuleHelperService:
    def __init__(self, services: 'BotServicesProvider', module_name: str):
        self.services = services
        self.module_name = module_name
        self.logger = logger.bind(service=f"{module_name}_helper")
        self.logger.info("UniversalModuleHelperService инициализирован.")

    async def get_user_specific_data(self, user_id: int, session: 'AsyncSession') -> str:
        # Пример: получение данных из БД или настроек
        module_settings = self.services.modules.get_module_settings(self.module_name)
        max_items = module_settings.get("item_limit", 10) if module_settings else 10
        
        # Здесь может быть запрос к БД для получения данных пользователя
        # user_items = await session.execute(select(SomeModel).where(SomeModel.user_id == user_id).limit(max_items))
        # items = list(user_items.scalars().all())
        
        self.logger.debug(f"Получение данных для пользователя {user_id} с лимитом {max_items}.")
        return f"Ваши данные (до {max_items} шт.) из Универсального Модуля!"

    async def perform_complex_action(self, user_id: int, data: dict) -> bool:
        self.logger.info(f"Пользователь {user_id} выполняет сложное действие с данными: {data}")
        # ... логика сложного действия ...
        # await self.services.events.publish(f"{self.module_name}:complex_action_done", user_id=user_id, result="success")
        return True

# Использовать этот сервис можно было бы в __init__.py модуля:
# from .services import UniversalModuleHelperService
# ...
# async def setup_module(dp, bot, services):
#     module_name = "my_universal_module"
#     helper = UniversalModuleHelperService(services, module_name)
#     services.ext.register_module_service(module_name, "helper", helper) 
#     # services.ext - это гипотетический способ регистрации кастомных сервисов модуля
#     # Либо просто передавать helper в хэндлеры через data['module_helper'] = helper в __init__
# ...
```

---

**Важные моменты для разработчика модуля:**

*   **Именование**: Старайся использовать `snake_case` для имен файлов, переменных, функций. Имя модуля (`name` в манифесте) должно совпадать с именем папки.
*   **Разрешения**:
    *   Всегда объявляй разрешения, которые использует твой модуль, в `manifest.yaml` в секции `permissions`. Имя разрешения должно начинаться с `имя_модуля.`.
    *   В хэндлерах всегда проверяй права пользователя перед выполнением привилегированных действий или показом чувствительных данных.
    *   Для UI-точки входа модуля (кнопки в общем меню "Модули") указывай `required_permission_to_view` в `services.ui_registry.register_module_entry`, чтобы ядро автоматически скрывало кнопку от тех, у кого нет этого базового права.
    *   Если модуль должен быть доступен всем пользователям по умолчанию, установи `metadata.assign_default_access_to_user_role: true` в манифесте и убедись, что у тебя есть разрешение вида `имя_модуля.access_user_features`.
*   **Настройки**:
    *   Описывай все настройки модуля в секции `settings` манифеста.
    *   Предоставляй файл `module_settings_defaults.yaml` с разумными значениями по умолчанию.
    *   В коде модуля получай настройки через `services.modules.get_module_settings(MODULE_NAME)`.
*   **База данных**:
    *   Все модели SQLAlchemy должны наследоваться от `core.database.base.SDBBaseModel`.
    *   Имена таблиц должны иметь префикс, например, `mod_{module_name}_`.
    *   Указывай полные пути к классам моделей в `model_definitions` манифеста.
    *   Для работы с БД в хэндлерах используй `async with services_provider.db.get_session() as session:`.
*   **Логирование**: Используй `logger` из `loguru`, который доступен через `services.logger` или импортируется напрямую. Рекомендуется биндить логгер к имени модуля: `logger.bind(module=MODULE_NAME)`.
*   **Изоляция**: Старайся минимизировать прямые импорты из других модулей (кроме ядра). Если нужна межмодульная коммуникация, используй систему событий (`services.events`).
*   **Асинхронность**: Все хэндлеры и функции, работающие с I/O (БД, сеть, файловая система), должны быть асинхронными (`async def`).
*   **Чистота кода**: Следуй PEP 8, добавляй комментарии, пиши понятный код.

Этот шаблон должен покрыть большинство сценариев. Если у тебя есть конкретные пожелания или идеи по его дополнению, дай знать!