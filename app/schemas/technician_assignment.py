# Файл: app/schemas/technician_assignment.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- Схемы для Назначений техников (TechnicianAssignments) ---

class TechnicianAssignmentBase(BaseModel):
    """Базовая схема для назначения техника."""
    technician_id: int = Field(..., description="ID техника (пользователя с ролью 'tech')")

class TechnicianAssignmentCreate(TechnicianAssignmentBase):
    """Схема для создания нового назначения техника."""
    pass

class TechnicianAssignmentRead(TechnicianAssignmentBase):
    """Схема для чтения данных о назначении техника."""
    assignment_id: int = Field(..., description="Уникальный идентификатор назначения")
    ticket_id: int = Field(..., description="ID заявки")
    assigned_at: datetime = Field(..., description="Дата и время назначения")

    class Config:
        from_attributes = True

# --- Дополнительные схемы для API ---

class TechnicianIds(BaseModel):
    """Схема для передачи списка ID техников для массового назначения."""
    technician_ids: List[int] = Field(..., description="Список ID техников для назначения на заявку")

class TechnicianAssignmentWithDetails(TechnicianAssignmentRead):
    """Расширенная схема для чтения данных о назначении с информацией о технике."""
    technician_name: str = Field(..., description="Имя техника")
    technician_username: str = Field(..., description="Логин техника")
    
    class Config:
        from_attributes = False  # Эта схема будет заполняться программно
