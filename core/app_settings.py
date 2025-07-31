# core/app_settings.py

import os
import sys
import yaml
from pathlib import Path
from typing import List, Optional, Literal, Any, Dict 
from pydantic import BaseModel, Field, field_validator, HttpUrl, ValidationInfo, AliasChoices

# <-- ИЗМЕНЕНИЕ: Исправлена опечатка pantic -> pydantic
try:
    from loguru import logger as global_logger 
except ImportError:
    import logging
    global_logger = logging.getLogger("sdb_app_settings_fallback")
    global_logger.warning("Loguru не найден, используется стандартный logging. Пожалуйста, установите Loguru.")

from dotenv import load_dotenv, find_dotenv
from pydantic.networks import PostgresDsn, MySQLDsn, AnyUrl 
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILENAME = ".env"
DEFAULT_PROJECT_DATA_DIR_NAME = "project_data" 
USER_CONFIG_DIR_NAME = "Config" 
USER_CONFIG_FILENAME = "core_settings.yaml"
ENABLED_MODULES_FILENAME = "enabled_modules.json" 
ROOT_CONFIG_TEMPLATE_FILENAME = "config.yaml" 
STRUCTURED_LOGS_ROOT_DIR_NAME = "Logs" 

# --- Модели настроек ---
# (Этот блок остается без изменений, я его скопировал из вашего файла)
class DBSettings(BaseModel):
    type: Literal["sqlite", "postgresql", "mysql"] = Field(default="sqlite", description="Тип используемой базы данных.")
    sqlite_path: str = Field(
        default=f"Database_files/sdb.db", 
        description="Относительный путь к файлу SQLite (от корня проекта или project_data_path)."
    )
    pg_dsn: Optional[PostgresDsn] = Field(default=None, description="DSN для PostgreSQL.")
    mysql_dsn: Optional[MySQLDsn] = Field(default=None, description="DSN для MySQL.")
    echo_sql: bool = Field(default=False, description="Логировать SQL-запросы SQLAlchemy (уровень DEBUG).")

    @field_validator('pg_dsn', mode='before')
    @classmethod
    def check_pg_dsn(cls, v: Optional[PostgresDsn], info: ValidationInfo) -> Optional[PostgresDsn]:
        if info.data.get('type') == "postgresql" and not v:
            raise ValueError("pg_dsn должен быть указан для типа БД 'postgresql'.")
        return v

    @field_validator('mysql_dsn', mode='before')
    @classmethod
    def check_mysql_dsn(cls, v: Optional[MySQLDsn], info: ValidationInfo) -> Optional[MySQLDsn]:
        if info.data.get('type') == "mysql" and not v:
            raise ValueError("mysql_dsn должен быть указан для типа БД 'mysql'.")
        return v

class CacheSettings(BaseModel):
    type: Literal["memory", "redis"] = Field(default="memory", description="Тип кэша.")
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", description="URL для Redis.")

    @field_validator('redis_url', mode='before')
    @classmethod
    def check_redis_url(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        cache_type = info.data.get('type') if info.data else None
        if cache_type == "redis" and not v:
            raise ValueError("redis_url должен быть указан для типа кэша 'redis'.")
        return v

class TelegramSettings(BaseModel):
    # <-- ИЗМЕНЕНИЕ: Токен теперь опциональный, чтобы не падать при отсутствии .env
    token: Optional[str] = Field(default=None, description="Токен Telegram бота (рекомендуется указывать в .env).")
    polling_timeout: int = Field(default=30, ge=1, description="Таймаут long polling (секунды).")

class ModuleRepoSettings(BaseModel):
    index_url: Optional[HttpUrl] = Field(
        default=HttpUrl("https://raw.githubusercontent.com/soverxos/SwiftDevBot-Modules/main/modules_index.json"),
        description="URL к JSON-индексу официальных модулей SDB."
    )

class I18nSettings(BaseModel):
    locales_dir: Path = Field(default=PROJECT_ROOT_DIR / "locales", description="Путь к директории с файлами переводов.")
    domain: str = Field(default="bot", description="Имя домена для gettext.")
    default_locale: str = Field(default="en", description="Язык по умолчанию.")
    available_locales: List[str] = Field(default_factory=lambda: ["en", "ua"], description="Список доступных языков.")

class CoreAppSettings(BaseModel):
    project_data_path: Path = Field(
        default=PROJECT_ROOT_DIR / DEFAULT_PROJECT_DATA_DIR_NAME,
        description="Путь к директории данных проекта."
    )
    super_admins: List[int] = Field(default_factory=list, description="Список Telegram ID супер-администраторов.")
    enabled_modules_config_path: Path = Field(
        default=Path(f"{USER_CONFIG_DIR_NAME}/{ENABLED_MODULES_FILENAME}"), 
        description="Путь к файлу со списком активных модулей (относительно директории данных)."
    )
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_to_file: bool = Field(default=True)
    log_structured_dir: str = Field(
        default=STRUCTURED_LOGS_ROOT_DIR_NAME, 
        description="Базовая директория для структурированных лог-файлов (относительно project_data_path)."
    )
    log_rotation_size: str = Field(
        default="100 MB", 
        description="Максимальный размер одного часового лог-файла перед ротацией (e.g., '100 MB')."
    ) 
    log_retention_period_structured: str = Field(
        default="3 months", 
        description="Как долго хранить структурированные логи."
    )
    sdb_version: str = Field(default="0.1.0", pattern=r"^\d+\.\d+\.\d+([\w.-]*[\w])?(\+[\w.-]+)?$",
                             description="Версия ядра SwiftDevBot.")
    setup_bot_commands_on_startup: bool = Field(default=True, description="Устанавливать команды бота при старте.")
    i18n: I18nSettings = Field(default_factory=I18nSettings)

class AppSettings(BaseModel):
    db: DBSettings = Field(default_factory=DBSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    # <-- ИЗМЕНЕНИЕ: TelegramSettings теперь имеет default_factory
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    module_repo: ModuleRepoSettings = Field(default_factory=ModuleRepoSettings)
    core: CoreAppSettings = Field(default_factory=CoreAppSettings)
    model_config = {"validate_assignment": True}

# --- КЭШ И НОВАЯ ЛОГИКА ЗАГРУЗКИ ---

_loaded_settings_cache: Optional[AppSettings] = None
_loguru_console_configured_flag = False

def load_app_settings() -> AppSettings:
    """
    Загружает настройки из .env и config.yaml, объединяет их и возвращает объект AppSettings.
    Кэширует результат для последующих вызовов.
    """
    global _loaded_settings_cache, _loguru_console_configured_flag
    if _loaded_settings_cache is not None:
        return _loaded_settings_cache

    env_file_path = find_dotenv(filename=ENV_FILENAME, usecwd=True, raise_error_if_not_found=False)
    if env_file_path:
        load_dotenv(dotenv_path=env_file_path, override=True)

    bot_token = os.getenv("BOT_TOKEN")

    config_file_path = PROJECT_ROOT_DIR / "config.yaml"
    yaml_data: Dict[str, Any] = {}
    if config_file_path.is_file():
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f: 
                yaml_data = yaml.safe_load(f) or {}
        except Exception as e_yaml: 
            global_logger.error(f"Ошибка загрузки YAML из {config_file_path}: {e_yaml}.")
    
    # Собираем настройки
    db_config = yaml_data.get("database", {})
    db_s = DBSettings(
        type=db_config.get("type", "sqlite"),
        sqlite_path=db_config.get("sqlite_path", "Database_files/sdb.db"),
        pg_dsn=os.getenv("DB_PG_DSN") or db_config.get("pg_dsn"),
        mysql_dsn=os.getenv("DB_MYSQL_DSN") or db_config.get("mysql_dsn"),
        echo_sql=db_config.get("echo", False)
    )

    cache_config = yaml_data.get("cache", {})
    cache_s = CacheSettings(
        type=cache_config.get("backend", "memory"),
        redis_url=os.getenv("REDIS_URL") or cache_config.get("redis_url")
    )
    
    telegram_config = yaml_data.get("bot", {})
    # <-- ИЗМЕНЕНИЕ: Больше не падаем, если токена нет. Просто передаем None.
    telegram_s = TelegramSettings(
        token=bot_token, 
        polling_timeout=telegram_config.get("polling_timeout", 30)
    )
    
    modules_config = yaml_data.get("modules", {})
    module_repo_s = ModuleRepoSettings(
        index_url=HttpUrl(str(modules_config.get("repo_index_url", "https://raw.githubusercontent.com/soverxos/SwiftDevBot-Modules/main/modules_index.json")))
    )
    
    super_admin_ids_str = os.getenv("SUPER_ADMIN_IDS")
    s_admins_final_list: List[int] = []
    if super_admin_ids_str:
        try: 
            s_admins_final_list = [int(x.strip()) for x in super_admin_ids_str.split(',') if x.strip().isdigit()]
        except ValueError: 
             global_logger.error(f"Ошибка парсинга SUPER_ADMIN_IDS из .env: '{super_admin_ids_str}'")

    logging_config = yaml_data.get("logging", {})
    i18n_config = yaml_data.get("i18n", {})
    i18n_s = I18nSettings(
        available_locales=i18n_config.get("available_locales", ["en", "ua", "ru"]),
        default_locale=i18n_config.get("default_locale", "en")
    )

    core_s = CoreAppSettings(
        super_admins=s_admins_final_list,
        log_level=logging_config.get("level", "INFO").upper(),
        log_to_file=logging_config.get("file_logging", True),
        i18n=i18n_s,
    )

    final_settings = AppSettings(
        db=db_s, 
        cache=cache_s, 
        telegram=telegram_s, 
        module_repo=module_repo_s, 
        core=core_s
    )
    
    if not _loguru_console_configured_flag:
        global_logger.remove()
        log_level = "DEBUG" if os.getenv("SDB_CLI_DEBUG_MODE_FOR_LOGGING") == "true" else final_settings.core.log_level
        global_logger.add(sys.stderr, level=log_level, colorize=True)
        _loguru_console_configured_flag = True

    _loaded_settings_cache = final_settings
    return final_settings

# --- ГЛОБАЛЬНЫЙ ОБЪЕКТ settings ---

class SettingsProxy:
    """
    Прокси-объект, который загружает настройки только при первом обращении к ним.
    Это предотвращает падение при импорте, если конфиг еще не создан.
    """
    _instance: Optional[AppSettings] = None

    def __getattr__(self, name):
        if self._instance is None:
            try:
                self._instance = load_app_settings()
            except Exception as e:
                # В CLI режиме лучше просто показать ошибку и продолжить, если возможно
                print(f"ОШИБКА ЗАГРУЗКИ НАСТРОЕК: {e}", file=sys.stderr)
                # Возвращаем "пустую" модель, чтобы CLI не упал при импорте
                self._instance = AppSettings()
        return getattr(self._instance, name)

# <-- ИЗМЕНЕНИЕ: `settings` теперь "ленивый" прокси-объект.
settings = SettingsProxy()