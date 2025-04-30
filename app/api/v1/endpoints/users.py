from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, crud # Импортируем crud
from app.core.dependencies import get_current_user, get_current_admin_user # Импортируем зависимости
from app.db.session import get_session # Импортируем сессию
from app.core import security # Импортируем security для проверки пароля

router = APIRouter()

@router.get("/me", response_model=schemas.user.UserRead, tags=["Users"])
async def read_users_me(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Получает данные текущего аутентифицированного пользователя.
    """
    # Загружаем данные о роли пользователя
    await db.refresh(current_user, ['role'])
    
    # Зависимость get_current_user уже выполнила аутентификацию
    # и вернула объект models.User. FastAPI автоматически преобразует
    # его в схему UserRead благодаря response_model.
    return current_user

# --- Эндпоинты для текущего пользователя ---

@router.put("/me", response_model=schemas.user.UserRead, tags=["Users"])
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_session),
    user_in: schemas.user.UserUpdate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Обновляет данные текущего аутентифицированного пользователя.
    """
    # Получаем текущего пользователя из БД, чтобы иметь доступ к связанным объектам
    await db.refresh(current_user, ['role'])
    
    # Удаляем возможность изменения роли из данных обновления
    if hasattr(user_in, "role_id"):
        delattr(user_in, "role_id")
    
    try:
        user = await crud.user.update_user(db=db, db_obj=current_user, obj_in=user_in)
    except ValueError as e: # Ловим ошибку уникальности username из CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def update_password_me(
    *,
    db: AsyncSession = Depends(get_session),
    password_in: schemas.user.PasswordUpdate,
    current_user: models.User = Depends(get_current_user)
) -> None:
    """
    Обновляет пароль текущего пользователя.
    """
    # Проверяем старый пароль
    if not security.verify_password(password_in.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    # Хэшируем и обновляем пароль
    hashed_password = security.get_password_hash(password_in.new_password)
    await crud.user.update_user(db=db, db_obj=current_user, obj_in={"password_hash": hashed_password})
    # Возвращаем 204 No Content при успехе

# --- Эндпоинты для Администратора ---

@router.post(
    "/admin/users",
    response_model=schemas.user.UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def create_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_in: schemas.user.UserCreate,
) -> Any:
    """
    Создает нового пользователя (только для администраторов).
    """
    try:
        user = await crud.user.create_user(db=db, obj_in=user_in)
    except ValueError as e: # Ловим ошибку уникальности username из CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

@router.get(
    "/admin/users",
    response_model=List[schemas.user.UserRead],
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def read_users(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список пользователей с пагинацией (только для администраторов).
    """
    users = await crud.user.get_users(db, skip=skip, limit=limit)
    
    # Загружаем данные о ролях для всех пользователей
    for user in users:
        await db.refresh(user, ['role'])
    
    return users

@router.get(
    "/admin/users/{user_id}",
    response_model=schemas.user.UserRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Получает пользователя по ID (только для администраторов).
    """
    user = await crud.user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    # Загружаем данные о роли пользователя
    await db.refresh(user, ['role'])
    
    return user

@router.put(
    "/admin/users/{user_id}",
    response_model=schemas.user.UserRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def update_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: int,
    user_in: schemas.user.UserUpdate,
) -> Any:
    """
    Обновляет пользователя по ID (только для администраторов).
    Пароль этим методом не обновляется.
    """
    db_user = await crud.user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        user = await crud.user.update_user(db=db, db_obj=db_user, obj_in=user_in)
    except ValueError as e: # Ловим ошибку уникальности username из CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

@router.post(
    "/admin/users/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def reset_password_admin(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: int,
    password_in: schemas.user.AdminPasswordReset,
) -> None:
    """
    Устанавливает новый пароль для пользователя (только для администраторов).
    """
    db_user = await crud.user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed_password = security.get_password_hash(password_in.new_password)
    await crud.user.update_user(db=db, db_obj=db_user, obj_in={"password_hash": hashed_password})
    # Возвращаем 204 No Content при успехе

@router.delete(
    "/admin/users/{user_id}",
    response_model=schemas.user.UserRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: int,
    current_admin: models.User = Depends(get_current_admin_user) # Получаем админа для проверки
) -> Any:
    """
    Удаляет пользователя по ID (только для администраторов).
    Не позволяет администратору удалить самого себя.
    """
    if user_id == current_admin.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin cannot delete themselves.")

    deleted_user = await crud.user.remove_user(db=db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return deleted_user

@router.patch(
    "/admin/users/{user_id}/role",
    response_model=schemas.user.UserRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Users"]
)
async def change_user_role(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: int,
    role_in: schemas.user.UserRoleChange,
) -> Any:
    """
    Изменяет роль пользователя (только для администраторов).
    """
    # Проверяем существование пользователя
    db_user = await crud.user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Проверяем, отличается ли новая роль от текущей
    if db_user.role_id == role_in.role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already has this role"
        )
    
    # Обновляем роль пользователя
    try:
        user = await crud.user.update_user(db=db, db_obj=db_user, obj_in={"role_id": role_in.role_id})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Загружаем данные о роли пользователя для ответа
    await db.refresh(user, ['role'])
    
    return user