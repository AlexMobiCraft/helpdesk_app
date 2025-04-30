# Файл: app/models/technician_assignment.py
import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем User и Ticket для проверки типов
if TYPE_CHECKING:
    from .user import User # type: ignore
    from .ticket import Ticket # type: ignore


class TechnicianAssignment(Base):
    """
    Модель Назначения техника на заявку SQLAlchemy (Связующая таблица).
    """
    __tablename__ = "technician_assignments"

    assignment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, # ТЗ указывает AUTO_INCREMENT
        comment="Уникальный идентификатор назначения (Автоинкремент)"
    )
    # Внешний ключ на Заявку (Ticket)
    ticket_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tickets.ticket_id"), # Ссылаемся на будущую таблицу tickets
        nullable=False,
        index=True,
        comment="Внешний ключ, ID заявки"
    )
    # Внешний ключ на Пользователя (User), который является техником
    technician_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"), # Ссылаемся на существующую таблицу users
        nullable=False,
        index=True,
        comment="Внешний ключ, ID техника (из таблицы users)"
    )
    # Время назначения
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время назначения техника на заявку"
    )

    # Отношения (добавим позже, когда будут Ticket и User с нужными back_populates)
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="assignments")
    technician: Mapped["User"] = relationship("User", back_populates="assignments") # Или другое имя в User

    # Гарантируем, что один и тот же техник не может быть назначен на одну и ту же заявку дважды
    __table_args__ = (
        UniqueConstraint('ticket_id', 'technician_id', name='uq_ticket_technician'),
    )

    def __repr__(self):
        return f"<TechnicianAssignment(id={self.assignment_id}, ticket={self.ticket_id}, tech={self.technician_id})>"

    @property
    def technician_name(self) -> str:
        # Возвращает полное имя техника или username
        first = getattr(self.technician, 'first_name', None)
        last = getattr(self.technician, 'last_name', None)
        full = ' '.join(filter(None, [first, last])).strip()
        return full if full else self.technician.username

    @property
    def technician_username(self) -> str:
        return self.technician.username