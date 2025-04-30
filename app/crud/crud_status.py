# Файл: app/crud/crud_status.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app import models, schemas # Импортируем модели и схемы

async def get_status(db: AsyncSession, status_id: int) -> Optional[models.Status]:
    """Получает статус по его ID."""
    result = await db.execute(
        select(models.Status).filter(models.Status.status_id == status_id)
    )
    return result.scalars().first()

async def get_status_by_name(db: AsyncSession, name: str) -> Optional[models.Status]:
    """Получает статус по его имени."""
    result = await db.execute(
        select(models.Status).filter(models.Status.name == name)
    )
    return result.scalars().first()

async def get_statuses(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Status]:
    """Получает список статусов с пагинацией."""
    result = await db.execute(
        select(models.Status)
        .offset(skip)
        .limit(limit)
        .order_by(models.Status.display_order.asc().nulls_last(), models.Status.name) # Сортируем по порядку отображения, затем по имени
    )
    return result.scalars().all()

async def create_status(db: AsyncSession, *, obj_in: schemas.status.StatusCreate) -> models.Status:
    """Создает новый статус."""
    db_obj = models.Status(**obj_in.model_dump()) # Используем model_dump для Pydantic V2
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_status(
    db: AsyncSession, *, db_obj: models.Status, obj_in: schemas.status.StatusUpdate
) -> models.Status:
    """Обновляет существующий статус."""
    update_data = obj_in.model_dump(exclude_unset=True) # Используем model_dump для Pydantic V2
    if update_data:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def remove_status(db: AsyncSession, *, status_id: int) -> Optional[models.Status]:
    """Удаляет статус по ID."""
    db_obj = await get_status(db, status_id=status_id)
    if db_obj:
        # TODO: Добавить проверку, не используются ли заявки с этим статусом?
        await db.delete(db_obj)
        await db.commit()
    return db_obj # Возвращаем удаленный объект или None, если не найден