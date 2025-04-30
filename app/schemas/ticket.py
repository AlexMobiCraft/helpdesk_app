# Файл: app/schemas/ticket.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.user import UserRead
from app.schemas.device import DeviceRead
from app.schemas.priority import PriorityRead
from app.schemas.status import StatusRead
from app.schemas.file import FileRead
from app.schemas.technician_assignment import TechnicianAssignmentWithDetails

# Базовая схема для заявки с общими полями
class TicketBase(BaseModel):
    """Базовая схема для заявки с общими полями."""
    device_id: int = Field(..., description="ID устройства, с которым связана заявка")
    description: str = Field(..., min_length=10, description="Подробное описание проблемы")
    priority_id: int = Field(..., description="ID приоритета заявки")

# Схема для создания заявки
class TicketCreateBase(TicketBase):
    """Базовая схема для создания новой заявки."""
    pass

# Схема для создания заявки (пользователь)
class TicketCreate(TicketCreateBase):
    """Схема для создания новой заявки."""
    # user_id будет автоматически установлен из токена
    # status_id будет автоматически установлен как начальный статус

# Схема для создания заявки (администратор от имени пользователя)
class AdminTicketCreate(TicketCreateBase):
    """Схема для создания новой заявки администратором от имени пользователя."""
    user_id: int = Field(..., description="ID пользователя, от имени которого создается заявка")

# Схема для обновления заявки
class TicketUpdate(BaseModel):
    """Схема для обновления существующей заявки."""
    device_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=10)
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    resolution_notes: Optional[str] = None

# Схема для обновления статуса заявки
class TicketStatusUpdate(BaseModel):
    """Схема для обновления статуса заявки."""
    status_id: int = Field(..., description="Новый ID статуса заявки")
    resolution_notes: Optional[str] = Field(None, description="Примечания по решению (только при закрытии)")

# Схема для чтения информации о заявке
class TicketRead(BaseModel):
    """Схема для чтения данных заявки."""
    ticket_id: int
    device_id: int
    user_id: int
    description: str
    priority_id: int
    status_id: int
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    files: List[FileRead] = []

    class Config:
        from_attributes = True

# Схема для детального чтения заявки со связанными объектами
class TicketDetailRead(TicketRead):
    """Схема для детального чтения заявки со всеми связанными объектами."""
    user: Optional[UserRead] = None
    device: Optional[DeviceRead] = None
    priority: Optional[PriorityRead] = None
    status: Optional[StatusRead] = None
    files: List[FileRead] = []
    assignments: List[TechnicianAssignmentWithDetails] = []
    # Здесь позже добавим поля для связанных файлов и назначений техников

    class Config:
        from_attributes = True
