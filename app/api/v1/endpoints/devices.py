# Файл: app/api/v1/endpoints/devices.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional

from app import crud, models, schemas
from app.db.session import get_session
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

# --- Эндпоинты для Администратора ---

@router.post(
    "/admin/devices",
    response_model=schemas.device.DeviceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Devices"]
)
async def create_device(
    *,
    db: AsyncSession = Depends(get_session),
    device_in: schemas.device.DeviceCreate
) -> Any:
    """
    Создает новое устройство (только для администраторов).
    Требует явного указания device_id.
    """
    try:
        # Проверка существования device_type_id, если он указан
        if device_in.device_type_id:
            device_type = await crud.device_type.get_device_type(db, device_type_id=device_in.device_type_id)
            if not device_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Device type with ID {device_in.device_type_id} not found",
                )
        device = await crud.device.create_device(db=db, obj_in=device_in)
    except ValueError as e:
        # Ловим ошибки уникальности ID или инвентарного номера из CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return device

@router.get(
    "/admin/devices",
    response_model=List[schemas.device.DeviceRead],
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Devices"]
)
async def read_devices_admin(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата"),
    device_type_id: Optional[int] = Query(None, description="Фильтр по ID типа устройства")
) -> Any:
    """
    Получает список устройств с пагинацией и фильтрацией (только для администраторов).
    """
    devices = await crud.device.get_devices(db, skip=skip, limit=limit, device_type_id=device_type_id)
    return devices

@router.put(
    "/admin/devices/{device_id}",
    response_model=schemas.device.DeviceRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Devices"]
)
async def update_device(
    *,
    db: AsyncSession = Depends(get_session),
    device_id: int,
    device_in: schemas.device.DeviceUpdate
) -> Any:
    """
    Обновляет устройство по ID (только для администраторов).
    """
    db_device = await crud.device.get_device(db, device_id=device_id)
    if not db_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    try:
        # Проверка существования device_type_id, если он указан
        if device_in.device_type_id is not None:
            device_type = await crud.device_type.get_device_type(db, device_type_id=device_in.device_type_id)
            if not device_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Device type with ID {device_in.device_type_id} not found",
                )
        device = await crud.device.update_device(db=db, db_obj=db_device, obj_in=device_in)
    except ValueError as e:
        # Ловим ошибки уникальности инвентарного номера из CRUD
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return device

@router.delete(
    "/admin/devices/{device_id}",
    response_model=schemas.device.DeviceRead,
    dependencies=[Depends(get_current_admin_user)], # Защита: только админ
    tags=["Admin - Devices"]
)
async def delete_device(
    *,
    db: AsyncSession = Depends(get_session),
    device_id: int
) -> Any:
    """
    Удаляет устройство по ID (только для администраторов).
    """
    # TODO: Добавить проверку, не связаны ли с устройством заявки?
    deleted_device = await crud.device.remove_device(db=db, device_id=device_id)
    if not deleted_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return deleted_device


# --- Эндпоинты для Всех Аутентифицированных Пользователей ---

@router.get(
    "",
    response_model=List[schemas.device.DeviceRead],
    dependencies=[Depends(get_current_user)], # Защита: любой аутентифицированный пользователь
    tags=["Devices"]
)
async def read_devices_user(
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей для возврата"),
    device_type_id: Optional[int] = Query(None, description="Фильтр по ID типа устройства")
) -> Any:
    """
    Получает список устройств с пагинацией и фильтрацией (для всех аутентифицированных пользователей).
    """
    devices = await crud.device.get_devices(db, skip=skip, limit=limit, device_type_id=device_type_id)
    return devices

@router.get(
    "/{device_id}",
    response_model=schemas.device.DeviceRead,
    dependencies=[Depends(get_current_user)], # Защита: любой аутентифицированный пользователь
    tags=["Devices"]
)
async def read_device_user(
    device_id: int,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Получает информацию о конкретном устройстве по ID (для всех аутентифицированных пользователей).
    """
    db_device = await crud.device.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return db_device