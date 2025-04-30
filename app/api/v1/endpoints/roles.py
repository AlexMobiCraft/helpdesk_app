from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app import models, schemas, crud
from app.core.dependencies import get_current_user, get_current_admin_user
from app.db.session import get_session

router = APIRouter()

# Эндпоинт #22: Получение списка ролей (только для администратора)
@router.get(
    "/admin/roles",
    response_model=List[schemas.user_role.UserRoleRead],
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Roles"]
)
async def read_user_roles(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список ролей пользователей с пагинацией (только для администраторов).
    """
    roles = await crud.user_role.get_user_roles(db, skip=skip, limit=limit)
    return roles

# Эндпоинт #23: Получение одной роли по ID (только для администратора)
@router.get(
    "/admin/roles/{role_id}",
    response_model=schemas.user_role.UserRoleRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Roles"]
)
async def read_user_role(
    role_id: int,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Получает роль пользователя по ID (только для администраторов).
    """
    role = await crud.user_role.get_user_role(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Роль не найдена"
        )
    return role

# Эндпоинт #24: Создание новой роли (только для администратора)
@router.post(
    "/admin/roles",
    response_model=schemas.user_role.UserRoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Roles"]
)
async def create_user_role(
    *,
    db: AsyncSession = Depends(get_session),
    role_in: schemas.user_role.UserRoleCreate,
) -> Any:
    """
    Создает новую роль пользователя (только для администраторов).
    """
    try:
        role = await crud.user_role.create_user_role(db=db, obj_in=role_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return role

# Эндпоинт #25: Обновление роли (только для администратора)
@router.put(
    "/admin/roles/{role_id}",
    response_model=schemas.user_role.UserRoleRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Roles"]
)
async def update_user_role(
    *,
    db: AsyncSession = Depends(get_session),
    role_id: int,
    role_in: schemas.user_role.UserRoleUpdate,
) -> Any:
    """
    Обновляет роль пользователя по ID (только для администраторов).
    """
    try:
        role = await crud.user_role.update_user_role(db=db, role_id=role_id, obj_in=role_in)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Роль не найдена"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return role

# Эндпоинт #26: Удаление роли (только для администратора)
@router.delete(
    "/admin/roles/{role_id}",
    response_model=schemas.user_role.UserRoleRead,
    dependencies=[Depends(get_current_admin_user)],
    tags=["Admin - Roles"]
)
async def delete_user_role(
    *,
    db: AsyncSession = Depends(get_session),
    role_id: int,
) -> Any:
    """
    Удаляет роль пользователя по ID (только для администраторов).
    
    Роль не может быть удалена, если она используется пользователями.
    """
    # Проверка на наличие пользователей с этой ролью
    result = await db.execute(
        text("SELECT COUNT(*) FROM users WHERE role_id = :role_id"), 
        {"role_id": role_id}
    )
    count = result.scalar()
    
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить роль, так как она используется {count} пользователями"
        )
    
    role = await crud.user_role.delete_user_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Роль не найдена"
        )
    return role
