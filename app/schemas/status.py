# Файл: app/schemas/status.py
from pydantic import BaseModel, Field
from typing import Optional

# --- Схемы для Статусов (Statuses) ---

class StatusBase(BaseModel):
    """Базовая схема для статуса."""
    name: str = Field(..., min_length=1, max_length=100, description="Название статуса")
    display_order: Optional[int] = Field(None, description="Порядок отображения (необязательно)")
    is_final: bool = Field(False, description="Флаг завершающего статуса (закрывает заявку)")

class StatusCreate(StatusBase):
    """Схема для создания нового статуса."""
    # Наследует 'name', 'display_order' и 'is_final' от StatusBase
    pass

class StatusUpdate(BaseModel):
    """
    Схема для обновления существующего статуса.
    Все поля опциональны.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Новое название статуса")
    display_order: Optional[int] = Field(None, description="Новый порядок отображения")
    is_final: Optional[bool] = Field(None, description="Флаг завершающего статуса (закрывает заявку)")

class StatusRead(StatusBase):
    """Схема для чтения данных статуса из БД."""
    status_id: int = Field(..., description="Уникальный идентификатор статуса")

    class Config:
        # Включаем режим ORM (from_attributes для Pydantic V2)
        from_attributes = True