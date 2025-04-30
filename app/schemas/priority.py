# Файл: app/schemas/priority.py
from pydantic import BaseModel, Field
from typing import Optional

# --- Схемы для Приоритетов (Priorities) ---

class PriorityBase(BaseModel):
    """Базовая схема для приоритета."""
    name: str = Field(..., min_length=1, max_length=100, description="Название приоритета")
    display_order: Optional[int] = Field(None, description="Порядок отображения (необязательно)")

class PriorityCreate(PriorityBase):
    """Схема для создания нового приоритета."""
    # Наследует 'name' и 'display_order' от PriorityBase
    pass

class PriorityUpdate(BaseModel):
    """
    Схема для обновления существующего приоритета.
    Все поля опциональны.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Новое название приоритета")
    display_order: Optional[int] = Field(None, description="Новый порядок отображения")

class PriorityRead(PriorityBase):
    """Схема для чтения данных приоритета из БД."""
    priority_id: int = Field(..., description="Уникальный идентификатор приоритета")

    class Config:
        # Включаем режим ORM (from_attributes для Pydantic V2)
        from_attributes = True