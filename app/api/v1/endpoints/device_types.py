# Файл: app/api/v1/endpoints/device_types.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app import crud, models, schemas
from app.db.session import get_session
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

# --- Эндпоинты для Администратора ---

@router.post(
    "/admin/device-types",
    response_model=schemas.device_type.DeviceTypeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Device Types"]
)
async def create_device_type(
    *,
    db: AsyncSession = Depends(get_session),
    device_type_in: schemas.device_type.DeviceTypeCreate
) -> Any:
    """
    Создает новый тип устройства (только для администраторов).
    """
    # Проверяем, существует ли тип с таким именем
    existing_device_type = await crud.device_type.get_device_type_by_name(db, name=device_type_in.name)
    if existing_device_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device type with this name already exists",
        )
    device_type = await crud.device_type.create_device_type(db=db, obj_in=device_type_in)
    return device_type

@router.get(
    "/admin/device-types",
    response_model=List[schemas.device_type.DeviceTypeRead],
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Device Types"]
)
async def read_device_types_admin(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список типов устройств с пагинацией (только для администраторов).
    """
    device_types = await crud.device_type.get_device_types(db, skip=skip, limit=limit)
    return device_types

@router.get(
    "/admin/device-types/{device_type_id}",
    response_model=schemas.device_type.DeviceTypeRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Device Types"]
)
async def read_device_type_admin(
    device_type_id: int,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Получает тип устройства по ID (только для администраторов).
    """
    db_device_type = await crud.device_type.get_device_type(db, device_type_id=device_type_id)
    if db_device_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")
    return db_device_type

@router.put(
    "/admin/device-types/{device_type_id}",
    response_model=schemas.device_type.DeviceTypeRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Device Types"]
)
async def update_device_type(
    *,
    db: AsyncSession = Depends(get_session),
    device_type_id: int,
    device_type_in: schemas.device_type.DeviceTypeUpdate
) -> Any:
    """
    Обновляет тип устройства по ID (только для администраторов).
    """
    db_device_type = await crud.device_type.get_device_type(db, device_type_id=device_type_id)
    if not db_device_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")
    # Проверяем, не пытается ли админ установить имя, которое уже занято другим типом
    if device_type_in.name:
        existing_device_type = await crud.device_type.get_device_type_by_name(db, name=device_type_in.name)
        if existing_device_type and existing_device_type.device_type_id != device_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device type with this name already exists",
            )
    device_type = await crud.device_type.update_device_type(db=db, db_obj=db_device_type, obj_in=device_type_in)
    return device_type

@router.delete(
    "/admin/device-types/{device_type_id}",
    response_model=schemas.device_type.DeviceTypeRead, # Возвращаем удаленный объект
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Device Types"]
)
async def delete_device_type(
    *,
    db: AsyncSession = Depends(get_session),
    device_type_id: int
) -> Any:
    """
    Удаляет тип устройства по ID (только для администраторов).
    """
    # TODO: Добавить проверку, не используются ли устройства этого типа перед удалением?
    #       Или использовать ON DELETE SET NULL/RESTRICT в ForeignKey в модели Device.
    #       Пока просто удаляем.
    deleted_device_type = await crud.device_type.remove_device_type(db=db, device_type_id=device_type_id)
    if not deleted_device_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")
    return deleted_device_type


# --- Эндпоинт для Всех Аутентифицированных Пользователей ---

@router.get(
    "/device-types",
    response_model=List[schemas.device_type.DeviceTypeRead],
    dependencies=[Depends(get_current_user)], # Защита: любой аутентифицированный пользователь
    tags=["Device Types"] # Отдельный тег для общего доступа
)
async def read_device_types_user(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата")
) -> Any:
    """
    Получает список типов устройств с пагинацией (для всех аутентифицированных пользователей).
    """
    device_types = await crud.device_type.get_device_types(db, skip=skip, limit=limit)
    return device_types