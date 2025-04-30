from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app import crud, models, schemas # Импортируем нужные модули
from app.core import security
from app.db.session import get_session

# Определяем схему OAuth2. tokenUrl указывает на эндпоинт получения токена (/api/auth/login).
# Это используется FastAPI для автоматической генерации документации Swagger UI,
# позволяя пользователям вводить логин/пароль и получать токен прямо в интерфейсе документации.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Зависимость FastAPI для получения текущего аутентифицированного пользователя.

    1. Получает токен из заголовка Authorization: Bearer <token>.
    2. Декодирует и валидирует токен.
    3. Извлекает user_id из токена.
    4. Получает пользователя из базы данных по user_id.
    5. Возвращает объект пользователя models.User.

    Raises:
        HTTPException(401): Если токен невалиден или пользователь не найден.
    """
    try:
        # Декодируем токен, получаем данные (username, user_id, role)
        token_data: schemas.token.TokenData = security.decode_access_token(token)
    except HTTPException as e:
        # Перебрасываем исключение, если декодирование не удалось
        raise e
    except Exception:
        # Ловим другие возможные ошибки при декодировании
        raise security.credentials_exception

    if token_data.user_id is None:
        # Если в токене нет user_id, мы не можем найти пользователя
        raise security.credentials_exception

    # Получаем пользователя из БД по ID
    user = await crud.user.get_user_by_id(db, user_id=token_data.user_id)

    if user is None:
        # Если пользователь с таким ID не найден в БД (например, был удален после выдачи токена)
        raise security.credentials_exception

    # Возвращаем объект пользователя SQLAlchemy
    return user

# Можно добавить зависимости для проверки ролей, например:
# async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
#     if not current_user.is_active: # Предполагая наличие поля is_active
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

async def get_current_admin_user(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Зависимость для проверки, является ли текущий пользователь администратором."""
    # Загружаем данные о роли пользователя
    await db.refresh(current_user, ['role'])
    
    # Проверяем имя роли из связанной модели
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user