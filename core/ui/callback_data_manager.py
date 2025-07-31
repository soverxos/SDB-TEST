# core/ui/callback_data_manager.py
"""
Менеджер для управления длинными callback_data через хеширование
"""

import hashlib
import json
import asyncio # <-- ДОБАВЛЕН ИМПОРТ
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class CallbackDataManager:
    """Менеджер для сжатия длинных callback_data"""
    
    def __init__(self):
        # Хранилище хешей: hash -> original_data
        self._hash_storage: Dict[str, Dict[str, Any]] = {}
        # Время создания хешей для очистки старых
        self._hash_timestamps: Dict[str, datetime] = {}
        # Максимальный размер callback_data (Telegram лимит)
        self.MAX_CALLBACK_SIZE = 64
        # Время жизни хешей (12 часов)
        self.HASH_TTL = timedelta(hours=12)
    
    def create_callback_data(self, callback_data_dict: Dict[str, Any]) -> str:
        """
        Создает callback_data, сжимая его если он превышает лимит
        
        Args:
            callback_data_dict: Словарь с данными callback_data
            
        Returns:
            Строка callback_data (либо оригинальная, либо хешированная)
        """
        # Сериализуем данные
        original_data = json.dumps(callback_data_dict, separators=(',', ':'), sort_keys=True)
        
        # Если данные помещаются в лимит, возвращаем как есть
        if len(original_data.encode('utf-8')) <= self.MAX_CALLBACK_SIZE:
            return original_data
        
        # Создаем хеш
        hash_value = self._create_hash(original_data)
        
        # Сохраняем в хранилище
        self._hash_storage[hash_value] = callback_data_dict
        self._hash_timestamps[hash_value] = datetime.now()
        
        # Возвращаем сжатую версию
        compressed_data = {
            "__hash__": hash_value,
            "__compressed__": True
        }
        
        return json.dumps(compressed_data, separators=(',', ':'))
    
    def get_callback_data(self, callback_string: str) -> Optional[Dict[str, Any]]:
        """
        Получает оригинальные данные callback_data
        
        Args:
            callback_string: Строка callback_data
            
        Returns:
            Словарь с данными или None если не найдено
        """
        try:
            data = json.loads(callback_string)
            
            # Если это обычные данные
            if not isinstance(data, dict) or not data.get("__compressed__"):
                return data
            
            # Если это сжатые данные
            hash_value = data.get("__hash__")
            if not hash_value:
                return None
            
            # Проверяем наличие в хранилище
            if hash_value not in self._hash_storage:
                return None
            
            # Проверяем срок действия
            if self._is_hash_expired(hash_value):
                self._remove_hash(hash_value)
                return None
            
            return self._hash_storage[hash_value]
            
        except (json.JSONDecodeError, KeyError):
            return None
    
    def _create_hash(self, data: str) -> str:
        """Создает короткий хеш для данных"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()[:12]
    
    def _is_hash_expired(self, hash_value: str) -> bool:
        """Проверяет, истек ли срок действия хеша"""
        if hash_value not in self._hash_timestamps:
            return True
        
        return datetime.now() - self._hash_timestamps[hash_value] > self.HASH_TTL
    
    def _remove_hash(self, hash_value: str):
        """Удаляет хеш из хранилища"""
        self._hash_storage.pop(hash_value, None)
        self._hash_timestamps.pop(hash_value, None)
    
    # ИЗМЕНЕНИЕ: Старый метод переименован в _cleanup..._sync для внутреннего использования
    def _cleanup_expired_hashes_sync(self):
        """Очищает устаревшие хеши (синхронная версия)"""
        expired_hashes = [
            hash_val for hash_val in list(self._hash_timestamps.keys()) # list() для безопасного удаления
            if self._is_hash_expired(hash_val)
        ]
        
        for hash_val in expired_hashes:
            self._remove_hash(hash_val)
        
        return len(expired_hashes)

    # ИЗМЕНЕНИЕ: Создаем асинхронную задачу для фонового выполнения
    async def cleanup_expired_hashes_task(self):
        """Бесконечная асинхронная задача для периодической очистки устаревших хешей."""
        logger.info("[CallbackManager] Фоновая задача очистки хешей запущена.")
        while True:
            try:
                # Пауза. 1 час.
                await asyncio.sleep(3600)
                
                logger.trace("[CallbackManager] Выполнение плановой очистки устаревших хешей...")
                deleted_count = self._cleanup_expired_hashes_sync()
                if deleted_count > 0:
                    stats = self.get_storage_stats()
                    logger.debug(f"[CallbackManager] Очистка хешей: {stats['total_hashes']} активных, удалено {deleted_count} устаревших.")
                
            except asyncio.CancelledError:
                logger.info("[CallbackManager] Задача очистки хешей отменена.")
                break
            except Exception as e:
                logger.error(f"[CallbackManager] Ошибка в задаче очистки хешей: {e}", exc_info=True)
                # Пауза перед повторной попыткой в случае ошибки
                await asyncio.sleep(60)

    def get_storage_stats(self) -> Dict[str, int]:
        """Возвращает статистику хранилища"""
        # Считаем просроченные на лету
        expired_count = sum(1 for h in self._hash_timestamps.keys() if self._is_hash_expired(h))
        return {
            'total_hashes': len(self._hash_storage),
            'expired_hashes': expired_count
        }


# Глобальный экземпляр менеджера
callback_data_manager = CallbackDataManager()