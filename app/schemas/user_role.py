from pydantic import BaseModel, Field
from typing import Optional

class UserRoleBase(BaseModel):
    """Базовая схема для роли пользователя."""
    name: str = Field(..., min_length=1, max_length=50, description="Название роли")
    description: Optional[str] = Field(None, description="Описание роли")

class UserRoleCreate(UserRoleBase):
    """Схема для создания роли пользователя."""
    pass

class UserRoleUpdate(BaseModel):
    """Схема для обновления роли пользователя."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Название роли")
    description: Optional[str] = Field(None, description="Описание роли")

class UserRoleRead(UserRoleBase):
    """Схема для чтения роли пользователя."""
    id: int

    class Config:
        from_attributes = True
