from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Схема для ответа с JWT токеном."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Схема для данных, закодированных внутри JWT токена."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None # Добавим роль для удобства проверки прав