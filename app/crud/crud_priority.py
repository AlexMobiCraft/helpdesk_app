# Файл: app/crud/crud_priority.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app import models, schemas # Импортируем модели и схемы

async def get_priority(db: AsyncSession, priority_id: int) -> Optional[models.Priority]:
    """Получает приоритет по его ID."""
    result = await db.execute(
        select(models.Priority).filter(models.Priority.priority_id == priority_id)
    )
    return result.scalars().first()

async def get_priority_by_name(db: AsyncSession, name: str) -> Optional[models.Priority]:
    """Получает приоритет по его имени."""
    result = await db.execute(
        select(models.Priority).filter(models.Priority.name == name)
    )
    return result.scalars().first()

async def get_priorities(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Priority]:
    """Получает список приоритетов с пагинацией."""
    result = await db.execute(
        select(models.Priority)
        .offset(skip)
        .limit(limit)
        .order_by(models.Priority.display_order.asc().nulls_last(), models.Priority.name) # Сортируем по порядку отображения, затем по имени
    )
    return result.scalars().all()

async def create_priority(db: AsyncSession, *, obj_in: schemas.priority.PriorityCreate) -> models.Priority:
    """Создает новый приоритет."""
    db_obj = models.Priority(**obj_in.model_dump()) # Используем model_dump для Pydantic V2
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_priority(
    db: AsyncSession, *, db_obj: models.Priority, obj_in: schemas.priority.PriorityUpdate
) -> models.Priority:
    """Обновляет существующий приоритет."""
    update_data = obj_in.model_dump(exclude_unset=True) # Используем model_dump для Pydantic V2
    if update_data:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def remove_priority(db: AsyncSession, *, priority_id: int) -> Optional[models.Priority]:
    """Удаляет приоритет по ID."""
    db_obj = await get_priority(db, priority_id=priority_id)
    if db_obj:
        # TODO: Добавить проверку, не используются ли заявки с этим приоритетом?
        await db.delete(db_obj)
        await db.commit()
    return db_obj # Возвращаем удаленный объект или None, если не найден