# modules/notes_manager/callback_data_factories.py

from aiogram.filters.callback_data import CallbackData
from typing import Optional

class NotesAction(CallbackData, prefix="notes"):
    """Callback data для действий в модуле заметок"""
    action: str  # list, create, view, edit, delete, back_to_main, back_to_list
    note_id: Optional[int] = None
