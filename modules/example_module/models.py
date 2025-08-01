# modules/example_module/models.py
from sqlalchemy import String, Integer, ForeignKey, Text, Boolean, BigInteger # <--- Добавил BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import SDBBaseModel 
from core.database.core_models import SDB_CORE_TABLE_PREFIX # Импортируем префикс для ForeignKey
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.database.core_models import User # Для type hinting в Mapped

# Оставляем существующие модели
class ExampleTableOne(SDBBaseModel): 
    __tablename__ = "mod_example_table_one"
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Пример текстового поля")
    description: Mapped[Optional[str]] = mapped_column(String(255), comment="Описание для примера")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    def __repr__(self):
        return f"<ExampleTableOne(id={self.id}, name='{self.name}')>"

class AnotherExampleTable(SDBBaseModel): 
    __tablename__ = "mod_another_example_table"
    example_one_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('mod_example_table_one.id', ondelete='CASCADE')) 
    value: Mapped[str] = mapped_column(String(200), nullable=False, comment="Пример строкового значения")
    example_one: Mapped[Optional["ExampleTableOne"]] = relationship("ExampleTableOne", backref="another_examples") 

    def __repr__(self):
        return f"<AnotherExampleTable(id={self.id}, value='{self.value}')>"

# Новая модель для заметок пользователя
class UserNote(SDBBaseModel):
    __tablename__ = "mod_example_user_notes"

    # Telegram ID пользователя, которому принадлежит заметка. Используем BigInteger.
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, # <--- ИЗМЕНЕНО ЗДЕСЬ
        index=True, 
        nullable=False, 
        comment="Telegram ID пользователя-владельца заметки"
    )
    note_text: Mapped[str] = mapped_column(Text, nullable=False, comment="Текст заметки")
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="Отмечена ли заметка как выполненная")

    # Связь с основной таблицей пользователей SDB (если нужна)
    # Внешний ключ на ID пользователя в таблице sdb_users.
    # Это поле опционально, если ты идентифицируешь пользователя только по user_telegram_id.
    # Если используешь, то UserNote.user_id будет ссылаться на User.id из core_models.
    # И user_telegram_id здесь может быть избыточным, если есть user_id.
    # Но если модуль должен работать независимо и не всегда имеет доступ к объекту User из ядра,
    # то хранение user_telegram_id в самой таблице модуля полезно.
    # Для примера оставим оба, но для реального проекта выбери один подход.
    
    # user_db_id: Mapped[int] = mapped_column(ForeignKey(f"{SDB_CORE_TABLE_PREFIX}users.id", ondelete="CASCADE"), index=True)
    # user: Mapped["User"] = relationship(backref="example_module_notes")

    def __repr__(self) -> str:
        return f"<UserNote(id={self.id}, user_tg_id={self.user_telegram_id}, text='{self.note_text[:20]}...', done={self.is_done})>"