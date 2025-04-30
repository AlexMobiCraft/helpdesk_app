# Файл: app/api/v1/endpoints/statuses.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app import crud, models, schemas
from app.db.session import get_session
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

# --- Эндпоинты для Администратора ---

@router.post(
    "/admin/statuses",
    response_model=schemas.status.StatusRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Statuses"]
)
async def create_status(
    *,
    db: AsyncSession = Depends(get_session),
    status_in: schemas.status.StatusCreate
) -> Any:
    """
    Создает новый статус (только для администраторов).
    """
    existing_status = await crud.status.get_status_by_name(db, name=status_in.name)
    if existing_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status with this name already exists",
        )
    new_status = await crud.status.create_status(db=db, obj_in=status_in)
    return new_status

@router.get(
    "/admin/statuses",
    response_model=List[schemas.status.StatusRead],
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Statuses"]
)
async def read_statuses_admin(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список статусов с пагинацией (только для администраторов).
    """
    statuses = await crud.status.get_statuses(db, skip=skip, limit=limit)
    return statuses

@router.get(
    "/admin/statuses/{status_id}",
    response_model=schemas.status.StatusRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Statuses"]
)
async def read_status_admin(
    status_id: int,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Получает статус по ID (только для администраторов).
    """
    db_status = await crud.status.get_status(db, status_id=status_id)
    if db_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return db_status

@router.put(
    "/admin/statuses/{status_id}",
    response_model=schemas.status.StatusRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Statuses"]
)
async def update_status(
    *,
    db: AsyncSession = Depends(get_session),
    status_id: int,
    status_in: schemas.status.StatusUpdate
) -> Any:
    """
    Обновляет статус по ID (только для администраторов).
    """
    db_status = await crud.status.get_status(db, status_id=status_id)
    if not db_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    if status_in.name:
        existing_status = await crud.status.get_status_by_name(db, name=status_in.name)
        if existing_status and existing_status.status_id != status_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status with this name already exists",
            )
    updated_status = await crud.status.update_status(db=db, db_obj=db_status, obj_in=status_in)
    return updated_status

@router.delete(
    "/admin/statuses/{status_id}",
    response_model=schemas.status.StatusRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Statuses"]
)
async def delete_status(
    *,
    db: AsyncSession = Depends(get_session),
    status_id: int
) -> Any:
    """
    Удаляет статус по ID (только для администраторов).
    """
    # TODO: Добавить проверку использования перед удалением.
    deleted_status = await crud.status.remove_status(db=db, status_id=status_id)
    if not deleted_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return deleted_status


# --- Эндпоинт для Всех Аутентифицированных Пользователей ---

@router.get(
    "/statuses",
    response_model=List[schemas.status.StatusRead],
    dependencies=[Depends(get_current_user)], # Защита: любой аутентифицированный пользователь
    tags=["Statuses"] # Отдельный тег для общего доступа
)
async def read_statuses_user(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список статусов с пагинацией (для всех аутентифицированных пользователей).
    """
    statuses = await crud.status.get_statuses(db, skip=skip, limit=limit)
    return statuses