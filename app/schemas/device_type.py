# Файл: app/schemas/device_type.py
from pydantic import BaseModel, Field
from typing import Optional

# --- Схемы для Типов Устройств (Device Types) ---

class DeviceTypeBase(BaseModel):
    """Базовая схема для типа устройства."""
    name: str = Field(..., min_length=1, max_length=255, description="Название типа устройства")

class DeviceTypeCreate(DeviceTypeBase):
    """Схема для создания нового типа устройства."""
    # Наследует 'name' от DeviceTypeBase
    pass

class DeviceTypeUpdate(BaseModel):
    """
    Схема для обновления существующего типа устройства.
    Все поля опциональны.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название типа устройства")

class DeviceTypeRead(DeviceTypeBase):
    """Схема для чтения данных типа устройства из БД."""
    device_type_id: int = Field(..., description="Уникальный идентификатор типа устройства")

    class Config:
        # Включаем режим ORM (from_attributes для Pydantic V2)
        from_attributes = True