# Файл: app/api/v1/endpoints/priorities.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app import crud, models, schemas
from app.db.session import get_session
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

# --- Эндпоинты для Администратора ---

@router.post(
    "/admin/priorities",
    response_model=schemas.priority.PriorityRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Priorities"]
)
async def create_priority(
    *,
    db: AsyncSession = Depends(get_session),
    priority_in: schemas.priority.PriorityCreate
) -> Any:
    """
    Создает новый приоритет (только для администраторов).
    """
    existing_priority = await crud.priority.get_priority_by_name(db, name=priority_in.name)
    if existing_priority:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority with this name already exists",
        )
    priority = await crud.priority.create_priority(db=db, obj_in=priority_in)
    return priority

@router.get(
    "/admin/priorities",
    response_model=List[schemas.priority.PriorityRead],
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Priorities"]
)
async def read_priorities_admin(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список приоритетов с пагинацией (только для администраторов).
    """
    priorities = await crud.priority.get_priorities(db, skip=skip, limit=limit)
    return priorities

@router.get(
    "/admin/priorities/{priority_id}",
    response_model=schemas.priority.PriorityRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Priorities"]
)
async def read_priority_admin(
    priority_id: int,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Получает приоритет по ID (только для администраторов).
    """
    db_priority = await crud.priority.get_priority(db, priority_id=priority_id)
    if db_priority is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")
    return db_priority

@router.put(
    "/admin/priorities/{priority_id}",
    response_model=schemas.priority.PriorityRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Priorities"]
)
async def update_priority(
    *,
    db: AsyncSession = Depends(get_session),
    priority_id: int,
    priority_in: schemas.priority.PriorityUpdate
) -> Any:
    """
    Обновляет приоритет по ID (только для администраторов).
    """
    db_priority = await crud.priority.get_priority(db, priority_id=priority_id)
    if not db_priority:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")
    if priority_in.name:
        existing_priority = await crud.priority.get_priority_by_name(db, name=priority_in.name)
        if existing_priority and existing_priority.priority_id != priority_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority with this name already exists",
            )
    priority = await crud.priority.update_priority(db=db, db_obj=db_priority, obj_in=priority_in)
    return priority

@router.delete(
    "/admin/priorities/{priority_id}",
    response_model=schemas.priority.PriorityRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Priorities"]
)
async def delete_priority(
    *,
    db: AsyncSession = Depends(get_session),
    priority_id: int
) -> Any:
    """
    Удаляет приоритет по ID (только для администраторов).
    """
    # TODO: Добавить проверку использования перед удалением.
    deleted_priority = await crud.priority.remove_priority(db=db, priority_id=priority_id)
    if not deleted_priority:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")
    return deleted_priority


# --- Эндпоинт для Всех Аутентифицированных Пользователей ---

@router.get(
    "",
    response_model=List[schemas.priority.PriorityRead],
    dependencies=[Depends(get_current_user)], # Защита: любой аутентифицированный пользователь
    tags=["Priorities"] # Отдельный тег для общего доступа
)
async def read_priorities_user(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список приоритетов с пагинацией (для всех аутентифицированных пользователей).
    """
    priorities = await crud.priority.get_priorities(db, skip=skip, limit=limit)
    return priorities