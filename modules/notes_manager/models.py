# modules/notes_manager/models.py
from sqlalchemy import String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from core.database.base import SDBBaseModel 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.database.core_models import User # Для type hinting в Mapped

# Модель для заметок пользователя
class UserNote(SDBBaseModel):
    __tablename__ = "mod_notes_manager_user_notes"

    # Telegram ID пользователя, которому принадлежит заметка
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True, 
        nullable=False, 
        comment="Telegram ID пользователя-владельца заметки"
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="Заголовок заметки")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Содержание заметки")

    def __repr__(self) -> str:
        return f"<UserNote(id={self.id}, user_tg_id={self.user_telegram_id}, title='{self.title[:20]}...')>"