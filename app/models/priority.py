# Файл: app/models/priority.py
from typing import Optional # Используем Optional для display_order
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем Ticket только для проверки типов
if TYPE_CHECKING:
    from .ticket import Ticket # type: ignore

class Priority(Base):
    """
    Модель Приоритета SQLAlchemy.
    """
    __tablename__ = "priorities"

    priority_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, # ТЗ указывает AUTO_INCREMENT
        comment="Уникальный идентификатор приоритета (Автоинкремент)"
    )
    # Имя приоритета должно быть уникальным
    name: Mapped[str] = mapped_column(
        String(100), # Длина для имени приоритета
        nullable=False,
        unique=True,
        index=True,
        comment="Название приоритета"
    )
    # Порядок отображения - необязательное поле
    display_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True, # Разрешаем NULL
        comment="Порядок отображения приоритетов (необязательно)"
    )

    # Отношение "один ко многим" к заявкам (Tickets)
    # tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="priority") # Добавим позже

    # Явное ограничение уникальности на имя
    __table_args__ = (
        UniqueConstraint('name', name='uq_priorities_name'),
    )

    def __repr__(self):
        order = f", order={self.display_order}" if self.display_order is not None else ""
        return f"<Priority(id={self.priority_id}, name='{self.name}'{order})>"