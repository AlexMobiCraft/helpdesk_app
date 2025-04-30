# Файл: app/models/device_type.py
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Импортируем Device только для проверки типов, чтобы избежать циклического импорта
if TYPE_CHECKING:
    from .device import Device # type: ignore


class DeviceType(Base):
    """
    Модель Типа Устройства SQLAlchemy.
    """
    __tablename__ = "device_types"

    device_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, # ТЗ указывает AUTO_INCREMENT
        comment="Уникальный идентификатор типа устройства (Автоинкремент)"
    )
    # Имя типа должно быть уникальным и не пустым
    name: Mapped[str] = mapped_column(
        String(255), # Можно указать длину для varchar
        nullable=False,
        unique=True,
        index=True,
        comment="Название типа устройства"
    )

    # Отношение "один ко многим": один тип может иметь много устройств
    # 'devices' - имя атрибута для доступа к списку устройств этого типа
    # 'Device' - имя связанной модели (в кавычках для отложенной загрузки)
    # 'back_populates="device_type"' - связывает это отношение с атрибутом 'device_type' в модели Device
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="device_type")

    # Явно определяем ограничение уникальности на имя через __table_args__
    # Это гарантирует уникальность на уровне БД и помогает Alembic
    __table_args__ = (
        UniqueConstraint('name', name='uq_device_types_name'),
    )

    def __repr__(self):
        return f"<DeviceType(id={self.device_type_id}, name='{self.name}')>"