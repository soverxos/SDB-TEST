# core/ui/progress.py

import asyncio
from typing import Optional, Callable, Any
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console


class AsyncProgressBar:
    """
    Асинхронный прогресс-бар для отображения хода длительных операций.
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
    
    async def __aenter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        self.progress.__enter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)
    
    def add_task(self, description: str, total: int = 100) -> TaskID:
        """Добавляет новую задачу с прогрессом."""
        if not self.progress:
            raise RuntimeError("Progress bar not initialized. Use 'async with' statement.")
        
        self.task_id = self.progress.add_task(description, total=total)
        return self.task_id
    
    def update(self, task_id: Optional[TaskID] = None, advance: int = 1, description: Optional[str] = None):
        """Обновляет прогресс задачи."""
        if not self.progress:
            return
        
        update_task_id = task_id or self.task_id
        if update_task_id is None:
            return
        
        self.progress.update(update_task_id, advance=advance, description=description)
    
    def set_progress(self, completed: int, task_id: Optional[TaskID] = None, description: Optional[str] = None):
        """Устанавливает абсолютное значение прогресса."""
        if not self.progress:
            return
        
        update_task_id = task_id or self.task_id
        if update_task_id is None:
            return
        
        self.progress.update(update_task_id, completed=completed, description=description)


async def run_with_progress(
    operation: Callable[..., Any], 
    description: str,
    *args, 
    console: Optional[Console] = None,
    **kwargs
) -> Any:
    """
    Запускает операцию с отображением спиннера прогресса.
    
    Args:
        operation: Функция или корутина для выполнения
        description: Описание операции
        *args, **kwargs: Аргументы для операции
        console: Консоль для вывода (опционально)
    
    Returns:
        Результат выполнения операции
    """
    console = console or Console()
    
    async with AsyncProgressBar(console) as progress:
        task_id = progress.add_task(description, total=1)
        
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
            
            progress.set_progress(1, task_id, f"{description} - Завершено")
            return result
            
        except Exception as e:
            progress.set_progress(1, task_id, f"{description} - Ошибка: {str(e)}")
            raise


# Пример использования в CLI командах
async def example_long_operation():
    """Пример длительной операции с прогресс-баром."""
    async with AsyncProgressBar() as progress:
        task_id = progress.add_task("Загрузка данных...", total=100)
        
        for i in range(100):
            # Имитация работы
            await asyncio.sleep(0.05)
            progress.update(task_id, advance=1)
        
        progress.update(task_id, description="Загрузка завершена!")


if __name__ == "__main__":
    # Тест прогресс-бара
    asyncio.run(example_long_operation())
