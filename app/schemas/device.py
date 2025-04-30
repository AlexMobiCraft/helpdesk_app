# Файл: app/schemas/device.py
from pydantic import BaseModel, Field
from typing import Optional

# Импортируем схему для чтения типа устройства, чтобы вложить ее в DeviceRead
from .device_type import DeviceTypeRead

# --- Схемы для Устройств (Devices) ---

class DeviceBase(BaseModel):
    """Базовая схема для устройства."""
    name: str = Field(..., min_length=1, max_length=255, description="Название устройства")
    device_type_id: Optional[int] = Field(None, description="ID типа устройства (необязательно)")
    inventory_number: Optional[str] = Field(None, max_length=100, description="Инвентарный номер (уникальный, необязательно)")

class DeviceCreate(DeviceBase):
    """
    Схема для создания нового устройства.
    Требует явного указания device_id, так как он не автоинкрементный.
    """
    device_id: int = Field(..., description="Уникальный идентификатор устройства (задается вручную)")
    # Наследует name, device_type_id, inventory_number от DeviceBase

class DeviceUpdate(BaseModel):
    """
    Схема для обновления существующего устройства.
    Все поля опциональны. device_id не обновляется.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название устройства")
    device_type_id: Optional[int] = Field(None, description="Новый ID типа устройства")
    # Позволяем передавать null, чтобы "отвязать" инвентарный номер
    inventory_number: Optional[str | None] = Field(None, max_length=100, description="Новый инвентарный номер (уникальный, можно null)")

class DeviceRead(DeviceBase):
    """Схема для чтения данных устройства из БД."""
    device_id: int = Field(..., description="Уникальный идентификатор устройства")
    # Включаем информацию о типе устройства, если она есть
    device_type: Optional[DeviceTypeRead] = Field(None, description="Детали типа устройства")

    class Config:
        # Включаем режим ORM (from_attributes для Pydantic V2)
        from_attributes = True