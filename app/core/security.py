from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.token import TokenData # Импортируем схему TokenData

# Создаем контекст для хэширования паролей
# Используем bcrypt как основную схему
# Помечаем все остальные схемы как устаревшие (для будущей миграции хэшей, если потребуется)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Исключение для невалидных учетных данных
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли открытый пароль хэшированному."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хэширует пароль."""
    return pwd_context.hash(password)

def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data: Словарь с данными для кодирования в токене (например, 'sub' - username, 'id', 'role').
        expires_delta: Необязательное время жизни токена. Если не указано,
                       используется значение из настроек ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Сгенерированный JWT токен в виде строки.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Добавляем стандартное поле 'iat' (issued at)
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Декодирует и валидирует JWT токен доступа.

    Args:
        token: JWT токен в виде строки.

    Raises:
        credentials_exception: Если токен невалиден (ошибка подписи, истек срок, неверный формат).

    Returns:
        Объект TokenData с данными из токена.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Проверяем наличие обязательных полей (хотя бы username или user_id)
        username: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        role: Optional[str] = payload.get("role")

        if username is None and user_id is None:
            raise credentials_exception # Недостаточно данных в токене

        # Валидируем данные с помощью Pydantic схемы
        token_data = TokenData(username=username, user_id=user_id, role=role)

    except JWTError: # Ловим ошибки декодирования/валидации JWT
        raise credentials_exception
    except Exception: # Ловим другие возможные ошибки (например, при валидации Pydantic)
        raise credentials_exception

    return token_data