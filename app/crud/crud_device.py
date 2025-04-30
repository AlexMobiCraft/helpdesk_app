# Файл: app/crud/crud_device.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app import models, schemas # Импортируем модели и схемы

async def get_device(db: AsyncSession, device_id: int) -> Optional[models.Device]:
    """Получает устройство по его ID, подгружая связанный тип."""
    result = await db.execute(
        select(models.Device)
        .options(selectinload(models.Device.device_type)) # Загружаем связанный device_type
        .filter(models.Device.device_id == device_id)
    )
    return result.scalars().first()

async def get_device_by_inventory_number(db: AsyncSession, inventory_number: str) -> Optional[models.Device]:
    """Получает устройство по его инвентарному номеру."""
    result = await db.execute(
        select(models.Device).filter(models.Device.inventory_number == inventory_number)
    )
    return result.scalars().first()

async def get_devices(
    db: AsyncSession, skip: int = 0, limit: int = 100, device_type_id: Optional[int] = None
) -> List[models.Device]:
    """
    Получает список устройств с пагинацией и опциональной фильтрацией по типу.
    Подгружает связанные типы устройств.
    """
    statement = (
        select(models.Device)
        .options(selectinload(models.Device.device_type)) # Загружаем связанный device_type
        .offset(skip)
        .limit(limit)
        .order_by(models.Device.name) # Сортируем по имени
    )
    if device_type_id is not None:
        statement = statement.filter(models.Device.device_type_id == device_type_id)

    result = await db.execute(statement)
    return result.scalars().all()

async def create_device(db: AsyncSession, *, obj_in: schemas.device.DeviceCreate) -> models.Device:
    """
    Создает новое устройство.
    device_id должен быть предоставлен в obj_in.
    """
    # Проверяем, существует ли уже устройство с таким ID
    existing_device = await get_device(db, device_id=obj_in.device_id)
    if existing_device:
        raise ValueError(f"Device with ID {obj_in.device_id} already exists.") # Или можно использовать HTTPException в API слое

    # Проверяем, существует ли уже устройство с таким инвентарным номером (если он указан)
    if obj_in.inventory_number:
        existing_inv = await get_device_by_inventory_number(db, inventory_number=obj_in.inventory_number)
        if existing_inv:
            raise ValueError(f"Device with inventory number {obj_in.inventory_number} already exists.")

    # TODO: Проверить, существует ли device_type_id, если он указан?

    db_obj = models.Device(**obj_in.model_dump()) # Используем model_dump для Pydantic V2
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    # Перезагружаем объект с подгрузкой device_type для возврата
    await db.refresh(db_obj, attribute_names=['device_type'])
    return db_obj

async def update_device(
    db: AsyncSession, *, db_obj: models.Device, obj_in: schemas.device.DeviceUpdate
) -> models.Device:
    """Обновляет существующее устройство."""
    update_data = obj_in.model_dump(exclude_unset=True) # Используем model_dump для Pydantic V2

    # Проверяем уникальность инвентарного номера, если он меняется
    if "inventory_number" in update_data and update_data["inventory_number"] is not None:
        existing_inv = await get_device_by_inventory_number(db, inventory_number=update_data["inventory_number"])
        if existing_inv and existing_inv.device_id != db_obj.device_id:
            raise ValueError(f"Device with inventory number {update_data['inventory_number']} already exists.")

    # TODO: Проверить, существует ли device_type_id, если он указан?

    if update_data:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Перезагружаем объект с подгрузкой device_type для возврата
        await db.refresh(db_obj, attribute_names=['device_type'])
    return db_obj

async def remove_device(db: AsyncSession, *, device_id: int) -> Optional[models.Device]:
    """Удаляет устройство по ID."""
    db_obj = await get_device(db, device_id=device_id)
    if db_obj:
        # TODO: Добавить проверку, не связаны ли с устройством заявки?
        await db.delete(db_obj)
        await db.commit()
    return db_obj # Возвращаем удаленный объект или None, если не найден