# Файл: app/models/status.py
from typing import Optional
from sqlalchemy import Integer, String, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем Ticket только для проверки типов
if TYPE_CHECKING:
    from .ticket import Ticket # type: ignore

class Status(Base):
    """
    Модель Статуса заявки SQLAlchemy.
    """
    __tablename__ = "statuses"

    status_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, # ТЗ указывает AUTO_INCREMENT
        comment="Уникальный идентификатор статуса (Автоинкремент)"
    )
    # Имя статуса должно быть уникальным
    name: Mapped[str] = mapped_column(
        String(100), # Длина для имени статуса
        nullable=False,
        unique=True,
        index=True,
        comment="Название статуса"
    )
    # Порядок отображения - необязательное поле
    display_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True, # Разрешаем NULL
        comment="Порядок отображения статусов (необязательно)"
    )
    # Флаг, указывающий, является ли статус финальным (закрывающим заявку)
    is_final: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Флаг завершающего статуса (закрывает заявку)"
    )

    # Отношение "один ко многим" к заявкам (Tickets)
    # tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="status") # Добавим позже

    # Явное ограничение уникальности на имя
    __table_args__ = (
        UniqueConstraint('name', name='uq_statuses_name'),
    )

    def __repr__(self):
        order = f", order={self.display_order}" if self.display_order is not None else ""
        final = f", is_final={self.is_final}"
        return f"<Status(id={self.status_id}, name='{self.name}'{order}{final})>"