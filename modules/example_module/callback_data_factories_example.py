# modules/example_module/callback_data_factories_example.py

from aiogram.filters.callback_data import CallbackData
from typing import Optional

EXAMPLE_MODULE_PREFIX = "exmpl" 

class ExampleModuleAction(CallbackData, prefix=EXAMPLE_MODULE_PREFIX):
    action: str 
    # Для общих действий
    item_id: Optional[int] = None # Может быть ID заметки, или чего-то еще

    # Для FSM, если нужно передать какой-то параметр
    param: Optional[str] = None