# core/monitoring/performance.py

import time
import psutil
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


@dataclass
class PerformanceMetric:
    """Метрика производительности."""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    active_tasks: int
    response_time_ms: Optional[float] = None


class PerformanceMonitor:
    """
    Монитор производительности для отслеживания состояния системы.
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.metrics: List[PerformanceMetric] = []
        self._start_time = time.time()
        self._request_times: Dict[str, float] = {}
    
    def record_metric(self, response_time_ms: Optional[float] = None) -> PerformanceMetric:
        """Записывает текущую метрику производительности."""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            active_tasks = len(asyncio.all_tasks())
            
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                active_tasks=active_tasks,
                response_time_ms=response_time_ms
            )
            
            self.metrics.append(metric)
            
            # Ограничиваем историю
            if len(self.metrics) > self.max_history:
                self.metrics = self.metrics[-self.max_history:]
            
            return metric
            
        except Exception as e:
            logger.error(f"Ошибка записи метрики производительности: {e}")
            # Возвращаем пустую метрику
            return PerformanceMetric(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_mb=0.0,
                active_tasks=0
            )
    
    def start_request_timer(self, request_id: str):
        """Начинает отсчет времени для запроса."""
        self._request_times[request_id] = time.time()
    
    def end_request_timer(self, request_id: str) -> float:
        """Завершает отсчет времени для запроса и возвращает время в мс."""
        start_time = self._request_times.pop(request_id, None)
        if start_time is None:
            return 0.0
        
        duration_ms = (time.time() - start_time) * 1000
        self.record_metric(response_time_ms=duration_ms)
        return duration_ms
    
    def get_average_metrics(self, minutes: int = 5) -> Dict[str, float]:
        """Возвращает средние метрики за указанное количество минут."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {
                "avg_cpu_percent": 0.0,
                "avg_memory_mb": 0.0,
                "avg_active_tasks": 0.0,
                "avg_response_time_ms": 0.0
            }
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "avg_memory_mb": sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            "avg_active_tasks": sum(m.active_tasks for m in recent_metrics) / len(recent_metrics),
            "avg_response_time_ms": sum(
                m.response_time_ms for m in recent_metrics if m.response_time_ms is not None
            ) / len([m for m in recent_metrics if m.response_time_ms is not None]) if any(
                m.response_time_ms is not None for m in recent_metrics
            ) else 0.0
        }
    
    def get_uptime(self) -> float:
        """Возвращает время работы в секундах."""
        return time.time() - self._start_time
    
    def log_health_status(self):
        """Логирует текущее состояние здоровья системы."""
        try:
            metrics = self.get_average_metrics(minutes=1)
            uptime = self.get_uptime()
            
            logger.info(
                "System health status",
                extra={
                    "uptime_seconds": uptime,
                    "avg_cpu_percent": metrics["avg_cpu_percent"],
                    "avg_memory_mb": metrics["avg_memory_mb"],
                    "avg_active_tasks": metrics["avg_active_tasks"],
                    "avg_response_time_ms": metrics["avg_response_time_ms"]
                }
            )
            
            # Предупреждения при высоких значениях
            if metrics["avg_cpu_percent"] > 80:
                logger.warning(f"High CPU usage: {metrics['avg_cpu_percent']:.1f}%")
            
            if metrics["avg_memory_mb"] > 500:
                logger.warning(f"High memory usage: {metrics['avg_memory_mb']:.1f} MB")
            
            if metrics["avg_response_time_ms"] > 1000:
                logger.warning(f"Slow response time: {metrics['avg_response_time_ms']:.1f} ms")
                
        except Exception as e:
            logger.error(f"Ошибка логирования состояния здоровья: {e}")


# Глобальный монитор производительности
performance_monitor = PerformanceMonitor()
