# Файл: app/crud/crud_file.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete as sqlalchemy_delete
from typing import Optional

from app.models.file import File
from app.schemas.file import FileCreate

async def get_file(db: AsyncSession, file_id: int) -> Optional[File]:
    """
    Получает файл по ID.
    
    Args:
        db: Асинхронная сессия базы данных.
        file_id: ID файла для поиска.
        
    Returns:
        Объект File, если найден, иначе None.
    """
    result = await db.execute(select(File).where(File.file_id == file_id))
    return result.scalars().first()

async def create_file(db: AsyncSession, *, obj_in: FileCreate) -> File:
    """
    Создает новую запись о файле в базе данных.
    
    Args:
        db: Асинхронная сессия базы данных.
        obj_in: Схема с данными для создания записи о файле.
        
    Returns:
        Созданный объект File.
    """
    # Создаем объект модели SQLAlchemy
    db_obj = File(
        ticket_id=obj_in.ticket_id,
        file_name=obj_in.file_name,
        file_path=obj_in.file_path,
        file_type=obj_in.file_type,
        file_size=obj_in.file_size
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_file(db: AsyncSession, *, file_id: int) -> Optional[File]:
    """
    Удаляет запись о файле из базы данных.
    
    Args:
        db: Асинхронная сессия базы данных.
        file_id: ID файла для удаления.
        
    Returns:
        Удаленный объект File или None, если файл не найден.
    """
    db_obj = await get_file(db, file_id=file_id)
    if not db_obj:
        return None
        
    await db.delete(db_obj)
    await db.commit()
    return db_obj
