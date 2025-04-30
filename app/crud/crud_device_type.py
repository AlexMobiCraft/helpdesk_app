# Файл: app/crud/crud_device_type.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app import models, schemas # Импортируем модели и схемы

async def get_device_type(db: AsyncSession, device_type_id: int) -> Optional[models.DeviceType]:
    """Получает тип устройства по его ID."""
    result = await db.execute(
        select(models.DeviceType).filter(models.DeviceType.device_type_id == device_type_id)
    )
    return result.scalars().first()

async def get_device_type_by_name(db: AsyncSession, name: str) -> Optional[models.DeviceType]:
    """Получает тип устройства по его имени."""
    result = await db.execute(
        select(models.DeviceType).filter(models.DeviceType.name == name)
    )
    return result.scalars().first()

async def get_device_types(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.DeviceType]:
    """Получает список типов устройств с пагинацией."""
    result = await db.execute(
        select(models.DeviceType).offset(skip).limit(limit).order_by(models.DeviceType.name) # Сортируем по имени
    )
    return result.scalars().all()

async def create_device_type(db: AsyncSession, *, obj_in: schemas.device_type.DeviceTypeCreate) -> models.DeviceType:
    """Создает новый тип устройства."""
    db_obj = models.DeviceType(name=obj_in.name)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_device_type(
    db: AsyncSession, *, db_obj: models.DeviceType, obj_in: schemas.device_type.DeviceTypeUpdate
) -> models.DeviceType:
    """Обновляет существующий тип устройства."""
    update_data = obj_in.model_dump(exclude_unset=True) # Используем model_dump для Pydantic V2
    if update_data:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def remove_device_type(db: AsyncSession, *, device_type_id: int) -> Optional[models.DeviceType]:
    """Удаляет тип устройства по ID."""
    db_obj = await get_device_type(db, device_type_id=device_type_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj # Возвращаем удаленный объект или None, если не найден