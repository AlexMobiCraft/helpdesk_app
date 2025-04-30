from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import enum

# Используем Enum из модели, если он там определен, или определяем здесь
# Импортируем UserRole из модели, если он там есть
try:
    from app.models.user import UserRole
except ImportError:
    # Если в модели нет UserRole, определяем его здесь как запасной вариант
    class UserRole(str, enum.Enum):
        USER = "user"
        TECHNICIAN = "technician"
        ADMIN = "admin"

# Определение схемы для роли пользователя
class UserRoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Базовая схема для пользователя, общие поля."""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None # Делаем email опциональным
    first_name: Optional[str] = Field(None, max_length=255)  # Необязательное поле - имя пользователя
    last_name: Optional[str] = Field(None, max_length=255)  # Необязательное поле - фамилия пользователя
    phone_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=255)
    role_id: int = Field(default=3)  # По умолчанию роль "user" (id=3)

class UserCreate(UserBase):
    """Схема для создания пользователя (требует пароль)."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Схема для обновления пользователя (все поля опциональны)."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)  # Добавлено поле для обновления имени пользователя
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=255)
    role_id: Optional[int] = Field(None, description="ID роли пользователя")  # Добавлено для поддержки изменения роли администратором
    # Пароль обновляется через отдельный эндпоинт

class UserRead(UserBase):
    """Схема для чтения данных пользователя (возвращается из API)."""
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True # Добавим поле is_active, если оно есть в модели
    
    # Уберем поле role - будем использовать только role_id, которое уже есть в UserBase

    class Config:
        # Включаем режим ORM (from_attributes для Pydantic V2)
        from_attributes = True

# --- Схемы для смены/установки пароля ---

class PasswordUpdate(BaseModel):
    """Схема для смены пароля текущим пользователем."""
    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль (минимум 8 символов)")

class AdminPasswordReset(BaseModel):
    """Схема для установки нового пароля пользователю администратором."""
    new_password: str = Field(..., min_length=8, description="Новый пароль (минимум 8 символов)")

# --- Схема для изменения роли пользователя ---

class UserRoleChange(BaseModel):
    """Схема для изменения роли пользователя администратором."""
    role_id: int = Field(..., description="ID новой роли пользователя")