# Файл: app/models/device.py
from sqlalchemy import Integer, String, ForeignKey, Index, UniqueConstraint # Добавлен UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING, Optional

# Импортируем DeviceType и Ticket для проверки типов
if TYPE_CHECKING:
    from .device_type import DeviceType # type: ignore
    # from .ticket import Ticket # Добавим позже


class Device(Base):
    """
    Модель Устройства SQLAlchemy.
    """
    __tablename__ = "devices"

    # ID устройства - БЕЗ автоинкремента согласно ТЗ
    device_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False, # Явно указываем False
        comment="Уникальный идентификатор устройства (НЕ автоинкремент)"
    )
    # Имя устройства, индексируем
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Название устройства"
    )
    # Внешний ключ на тип устройства, может быть NULL
    device_type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("device_types.device_type_id"), # Ссылка на PK таблицы device_types
        nullable=True, # Разрешаем NULL
        index=True, # Добавим индекс для FK для ускорения join'ов
        comment="Внешний ключ на тип устройства (может быть NULL)"
    )
    # Инвентарный номер, может быть NULL и должен быть уникальным
    inventory_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True, # Указываем уникальность здесь
        index=True,  # Индекс для быстрого поиска по инв. номеру
        comment="Инвентарный номер устройства (уникальный, может быть NULL)"
    )

    # Отношение "многие к одному" к DeviceType
    device_type: Mapped[Optional["DeviceType"]] = relationship(
        "DeviceType",
        back_populates="devices",
        lazy="selectin" # Оптимизация: загружать связанный тип сразу при запросе устройства
    )

    # Отношение "один ко многим" к Заявкам (Tickets)
    # tickets: Mapped[list["Ticket"]] = relationship(
    #     "Ticket",
    #     back_populates="device",
    #     cascade="all, delete-orphan"
    # ) # Раскомментируем и настроим позже

    # Дополнительные аргументы таблицы: индексы и ограничения
    # Alembic обычно сам создает индекс для unique=True и для ForeignKey,
    # но для надежности и ясности можно определить их явно.
    __table_args__ = (
        Index('ix_devices_device_type_id', 'device_type_id'), # Индекс для внешнего ключа
        Index('ix_devices_inventory_number', 'inventory_number'), # Индекс для инвентарного номера
        UniqueConstraint('inventory_number', name='uq_devices_inventory_number'), # Ограничение уникальности для инвентарного номера
    )


    def __repr__(self):
        inv_num = f", inv='{self.inventory_number}'" if self.inventory_number else ""
        type_id = f", type_id={self.device_type_id}" if self.device_type_id else ""
        return f"<Device(id={self.device_id}, name='{self.name}'{type_id}{inv_num})>"