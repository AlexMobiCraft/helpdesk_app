from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app import schemas # Импортируем модуль schemas
from app import crud # Импортируем модуль crud
from app.core import security
from app.db.session import get_session # Предполагаем, что сессия получается так

router = APIRouter()

@router.post("/login", response_model=schemas.token.Token, tags=["Authentication"])
async def login_for_access_token(
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Аутентифицирует пользователя и возвращает JWT токен доступа.

    Использует стандартную форму OAuth2 (поля username и password).
    """
    # 1. Получаем пользователя из БД по имени пользователя
    user = await crud.user.get_user_by_username(db, username=form_data.username)

    # 2. Проверяем, найден ли пользователь и верен ли пароль
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # Стандартный заголовок для 401
        )

    # 3. Проверяем, активен ли пользователь (если есть поле is_active)
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    # Загружаем роль пользователя для доступа к имени роли
    await db.refresh(user, ['role'])

    # 4. Создаем данные для токена
    token_data = {
        "sub": user.username, # Стандартное поле 'subject' для JWT
        "user_id": user.user_id,
        "role": user.role.name # Получаем имя роли из связанной модели UserRole
    }

    # 5. Генерируем токен доступа
    access_token = security.create_access_token(data=token_data)

    # 6. Возвращаем токен
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинт /me будет добавлен позже