# core/utils/rate_limiter.py

import time
from collections import defaultdict, deque
from typing import Dict, Optional


class SimpleRateLimiter:
    """
    Простой rate limiter для защиты от спама команд.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            max_requests: Максимальное количество запросов в окне
            window_seconds: Размер окна в секундах
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[int, deque] = defaultdict(deque)
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Проверяет, разрешен ли запрос для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если запрос разрешен, False если превышен лимит
        """
        now = time.time()
        user_requests = self._requests[user_id]
        
        # Удаляем старые запросы за пределами окна
        while user_requests and user_requests[0] < now - self.window_seconds:
            user_requests.popleft()
        
        # Проверяем лимит
        if len(user_requests) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        user_requests.append(now)
        return True
    
    def get_remaining_requests(self, user_id: int) -> int:
        """Возвращает количество оставшихся запросов для пользователя."""
        now = time.time()
        user_requests = self._requests[user_id]
        
        # Очищаем старые запросы
        while user_requests and user_requests[0] < now - self.window_seconds:
            user_requests.popleft()
        
        return max(0, self.max_requests - len(user_requests))
    
    def get_reset_time(self, user_id: int) -> Optional[float]:
        """Возвращает время (timestamp) когда лимит сбросится для пользователя."""
        user_requests = self._requests[user_id]
        if not user_requests:
            return None
        
        return user_requests[0] + self.window_seconds


# Глобальный rate limiter для команд
command_rate_limiter = SimpleRateLimiter(max_requests=30, window_seconds=60)
