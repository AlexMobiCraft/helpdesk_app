# Файл: app/models/file.py
import datetime
from sqlalchemy import Integer, String, BigInteger, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем Ticket только для проверки типов
if TYPE_CHECKING:
    from .ticket import Ticket # type: ignore


class File(Base):
    """
    Модель Файла, прикрепленного к заявке SQLAlchemy.
    """
    __tablename__ = "files"

    file_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, # ТЗ указывает AUTO_INCREMENT
        comment="Уникальный идентификатор файла (Автоинкремент)"
    )
    # Внешний ключ на заявку (Ticket)
    ticket_id: Mapped[int] = mapped_column(
        Integer,
        # Внешний ключ определяется здесь, но target_column указывается в ForeignKey
        # ForeignKey("tickets.ticket_id", ondelete="CASCADE"), # Раскомментировать/добавить ondelete позже, если нужно каскадное удаление
        ForeignKey("tickets.ticket_id"), # Пока без каскадного удаления
        nullable=False,
        index=True, # Индексируем для быстрого поиска файлов по заявке
        comment="Внешний ключ, ID заявки, к которой прикреплен файл"
    )
    file_name: Mapped[str] = mapped_column(
        String(255), # Ограничим длину имени файла
        nullable=False,
        comment="Оригинальное имя файла"
    )
    # Путь к файлу может быть длинным
    file_path: Mapped[str] = mapped_column(
        Text, # Используем Text для потенциально длинных путей
        nullable=False,
        comment="Путь к файлу в хранилище"
    )
    # MIME-тип файла
    file_type: Mapped[str] = mapped_column(
        String(100), # Длина для MIME-типа
        nullable=False,
        comment="MIME-тип файла"
    )
    # Размер файла в байтах (может быть большим)
    file_size: Mapped[int] = mapped_column(
        BigInteger, # Используем BigInteger для больших файлов
        nullable=False,
        comment="Размер файла в байтах"
    )
    # Время загрузки файла
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время загрузки файла"
    )

    # Отношение "многие к одному" к Заявке (Ticket)
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.file_id}, name='{self.file_name}', ticket_id={self.ticket_id})>"