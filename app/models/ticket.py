# Файл: app/models/ticket.py
import datetime
from typing import Optional # Используем Optional для nullable полей
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем связанные модели для проверки типов
if TYPE_CHECKING:
    from .user import User # type: ignore
    from .device import Device # type: ignore
    from .priority import Priority # type: ignore
    from .status import Status # type: ignore
    from .file import File # type: ignore
    from .technician_assignment import TechnicianAssignment # type: ignore


class Ticket(Base):
    """
    Модель Заявки (Ticket) SQLAlchemy.
    """
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Уникальный идентификатор заявки (Автоинкремент)"
    )
    # Внешний ключ на Устройство (Device)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.device_id"), nullable=False, index=True, comment="Внешний ключ, ID устройства"
    )
    # Внешний ключ на Пользователя (User), создавшего заявку
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False, index=True, comment="Внешний ключ, ID пользователя-автора"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Описание проблемы"
    )
    # Внешний ключ на Приоритет (Priority)
    priority_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("priorities.priority_id"), nullable=False, index=True, comment="Внешний ключ, ID приоритета"
    )
    # Внешний ключ на Статус (Status)
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("statuses.status_id"), nullable=False, index=True, comment="Внешний ключ, ID статуса"
    )
    # Примечания по решению (новое поле из ТЗ)
    resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Примечание по решению (может быть NULL)"
    )
    # Временные метки
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Дата и время создания"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Дата и время последнего обновления"
    )
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Дата и время закрытия (может быть NULL)"
    )

    # --- Определяем Отношения (Relationships) ---

    # Связь с Пользователем (автором)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin") # Указываем foreign_keys

    # Связь с Устройством
    device: Mapped["Device"] = relationship("Device", foreign_keys=[device_id], lazy="selectin") # Указываем foreign_keys

    # Связь с Приоритетом
    priority: Mapped["Priority"] = relationship("Priority", foreign_keys=[priority_id], lazy="selectin") # Указываем foreign_keys

    # Связь со Статусом
    status: Mapped["Status"] = relationship("Status", foreign_keys=[status_id], lazy="selectin") # Указываем foreign_keys

    # Связь с Файлами (один ко многим)
    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="ticket", # Добавим, когда определим 'ticket' в модели File
        cascade="all, delete-orphan" # Если удаляем заявку, удаляем и связанные файлы
    )

    # Связь с Назначениями Техников (один ко многим)
    assignments: Mapped[list["TechnicianAssignment"]] = relationship(
        "TechnicianAssignment",
        back_populates="ticket", # Добавим, когда определим 'ticket' в модели TechnicianAssignment
        cascade="all, delete-orphan" # Если удаляем заявку, удаляем и назначения
    )

    # Явно создаем индексы для внешних ключей
    __table_args__ = (
        Index('ix_tickets_device_id', 'device_id'),
        Index('ix_tickets_user_id', 'user_id'),
        Index('ix_tickets_priority_id', 'priority_id'),
        Index('ix_tickets_status_id', 'status_id'),
    )

    def __repr__(self):
        return f"<Ticket(id={self.ticket_id}, user={self.user_id}, device={self.device_id}, status={self.status_id})>"