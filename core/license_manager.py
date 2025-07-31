# core/license_manager.py
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Type
from enum import Enum
from dataclasses import dataclass, asdict, field
from loguru import logger

# --- Модели данных для лимитов ---

@dataclass
class BaseLimits:
    max_users: int = 100
    max_modules: int = 3
    allow_postgresql: bool = False
    allow_mysql: bool = False
    allow_redis: bool = False
    allow_advanced_cli: bool = False  # Для команд user, db, backup
    allow_full_admin_panel: bool = False
    allow_advanced_monitoring: bool = False # Health check

@dataclass
class ProLimits(BaseLimits):
    max_users: int = 2500
    max_modules: int = 25
    allow_postgresql: bool = True
    allow_mysql: bool = True
    allow_redis: bool = True
    allow_advanced_cli: bool = True
    allow_full_admin_panel: bool = True
    allow_advanced_monitoring: bool = True

@dataclass
class ProPlusLimits(ProLimits):
    max_users: int = -1  # -1 означает неограниченно
    max_modules: int = -1
    # В будущем здесь появятся фичи типа allow_prometheus_export, allow_obfuscation

# --- Перечисление типов лицензий ---

class LicenseType(Enum):
    LITE = "lite"
    PRO = "pro"
    PRO_PLUS = "pro_plus"

LIMITS_MAP: Dict[LicenseType, Type[BaseLimits]] = {
    LicenseType.LITE: BaseLimits,
    LicenseType.PRO: ProLimits,
    LicenseType.PRO_PLUS: ProPlusLimits,
}

@dataclass
class LicenseInfo:
    type: LicenseType = LicenseType.LITE
    key: Optional[str] = None
    activated_at: Optional[datetime] = None
    limits: BaseLimits = field(default_factory=BaseLimits)

    def __post_init__(self):
        # Убедимся, что self.limits соответствует self.type
        LimitsClass = LIMITS_MAP.get(self.type, BaseLimits)
        if not isinstance(self.limits, LimitsClass):
            self.limits = LimitsClass()

# --- Менеджер лицензий ---

class LicenseManager:
    def __init__(self, project_data_path: Path):
        self.license_file = project_data_path / "Config" / ".license"
        self.usage_file = project_data_path / ".usage_stats.json"
        self.license_info = LicenseInfo()
        self._usage_stats: Dict[str, Any] = {}
        self._logger = logger.bind(service="LicenseManager")
        self._load_license()
        self._load_usage_stats()

    def _load_license(self):
        if self.license_file.exists():
            try:
                data = json.loads(self.license_file.read_text())
                lic_type = LicenseType(data.get("type", "lite"))
                LimitsClass = LIMITS_MAP.get(lic_type, BaseLimits)
                self.license_info = LicenseInfo(
                    type=lic_type,
                    key=data.get("key"),
                    activated_at=datetime.fromisoformat(data["activated_at"]) if data.get("activated_at") else None,
                    limits=LimitsClass()
                )
                self._logger.success(f"Лицензия '{lic_type.value}' успешно загружена из {self.license_file}")
            except Exception as e:
                self._logger.error(f"Ошибка загрузки файла лицензии. Используется LITE по умолчанию. Ошибка: {e}")
                self.license_info = LicenseInfo()
        else:
            self._logger.info("Файл лицензии не найден. Активирована LITE версия.")

    def _save_license(self):
        try:
            data = {
                "type": self.license_info.type.value,
                "key": self.license_info.key,
                "activated_at": self.license_info.activated_at.isoformat() if self.license_info.activated_at else None,
            }
            self.license_file.parent.mkdir(parents=True, exist_ok=True)
            self.license_file.write_text(json.dumps(data, indent=2))
            self._logger.info(f"Информация о лицензии сохранена в {self.license_file}")
        except Exception as e:
            self._logger.error(f"Не удалось сохранить файл лицензии: {e}")

    def activate_license(self, key: str) -> bool:
        """Проверяет и активирует лицензионный ключ."""
        key = key.strip()
        lic_type = self._validate_key(key)

        if lic_type:
            self.license_info = LicenseInfo(
                type=lic_type,
                key=key,
                activated_at=datetime.now(tz=None),
                limits=LIMITS_MAP[lic_type]()
            )
            self._save_license()
            self._logger.success(f"Лицензия успешно активирована! Новый тип: {lic_type.value.upper()}")
            return True
        
        self._logger.error(f"Лицензионный ключ '{key}' недействителен.")
        return False

    def _validate_key(self, key: str) -> Optional[LicenseType]:
        """Простая заглушка для валидации ключа. В будущем замените на свою логику."""
        if key.startswith("PROPLUS-") and len(key) > 8:
            return LicenseType.PRO_PLUS
        if key.startswith("PRO-") and len(key) > 4:
            return LicenseType.PRO
        return None

    def get_current_usage(self, key: str) -> int:
        return self._usage_stats.get(key, 0)

    def is_feature_available(self, feature_name: str) -> bool:
        """Проверяет, доступна ли функция для текущей лицензии."""
        return getattr(self.license_info.limits, feature_name, False)

    def check_limit(self, limit_name: str, current_value: int) -> Tuple[bool, int]:
        """
        Проверяет, не превышен ли количественный лимит.
        Возвращает (разрешено_ли, лимит).
        """
        limit_value = getattr(self.license_info.limits, limit_name, 0)
        if limit_value == -1:  # -1 означает неограниченно
            return True, -1

        is_ok = current_value <= limit_value
        return is_ok, limit_value
    
    # Методы для обновления статистики (могут быть более сложными в будущем)
    def update_usage_stats(self, **kwargs: Any):
        """Обновляет и сохраняет статистику использования."""
        self._usage_stats.update(kwargs)
        self._save_usage_stats()

    def _load_usage_stats(self):
        if self.usage_file.exists():
            try:
                self._usage_stats = json.loads(self.usage_file.read_text())
            except Exception:
                self._usage_stats = {}
        else:
            self._usage_stats = {}
    
    def _save_usage_stats(self):
        try:
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            self.usage_file.write_text(json.dumps(self._usage_stats, indent=2))
        except Exception as e:
            self._logger.error(f"Не удалось сохранить статистику использования: {e}")


# Глобальный экземпляр менеджера
_license_manager: Optional[LicenseManager] = None

def get_license_manager() -> LicenseManager:
    """Возвращает глобальный экземпляр менеджера лицензий."""
    global _license_manager
    if _license_manager is None:
        from core.app_settings import settings
        _license_manager = LicenseManager(settings.core.project_data_path)
    return _license_manager