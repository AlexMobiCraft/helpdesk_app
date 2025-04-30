# Файл: app/crud/crud_technician_assignment.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, and_
from typing import List, Optional, Dict, Any, Tuple

from app import models, schemas

async def assign_technician(
    db: AsyncSession, 
    *, 
    ticket_id: int, 
    technician_id: int
) -> Optional[models.TechnicianAssignment]:
    """
    Назначает техника на заявку.
    
    Args:
        db: Асинхронная сессия базы данных.
        ticket_id: ID заявки.
        technician_id: ID техника (пользователя с ролью tech).
        
    Returns:
        Созданное назначение или None, если уже существует.
    """
    # Проверяем, существует ли уже такое назначение
    result = await db.execute(
        select(models.TechnicianAssignment)
        .where(
            and_(
                models.TechnicianAssignment.ticket_id == ticket_id,
                models.TechnicianAssignment.technician_id == technician_id
            )
        )
    )
    existing_assignment = result.scalars().first()
    
    # Если назначение уже существует, возвращаем None
    if existing_assignment:
        return None
    
    # Создаем новое назначение
    db_obj = models.TechnicianAssignment(
        ticket_id=ticket_id,
        technician_id=technician_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_technician(
    db: AsyncSession, 
    *, 
    ticket_id: int, 
    technician_id: int
) -> bool:
    """
    Снимает техника с заявки.
    
    Args:
        db: Асинхронная сессия базы данных.
        ticket_id: ID заявки.
        technician_id: ID техника (пользователя с ролью tech).
        
    Returns:
        True, если назначение было удалено, иначе False.
    """
    # Находим и удаляем назначение
    result = await db.execute(
        delete(models.TechnicianAssignment)
        .where(
            and_(
                models.TechnicianAssignment.ticket_id == ticket_id,
                models.TechnicianAssignment.technician_id == technician_id
            )
        )
        .returning(models.TechnicianAssignment.assignment_id)
    )
    deleted_row = result.scalar_one_or_none()
    
    # Если была удалена хотя бы одна строка
    if deleted_row:
        await db.commit()
        return True
    return False

async def get_ticket_technicians(
    db: AsyncSession, 
    *, 
    ticket_id: int
) -> List[Tuple[models.TechnicianAssignment, models.User]]:
    """
    Получает список техников, назначенных на заявку.
    
    Args:
        db: Асинхронная сессия базы данных.
        ticket_id: ID заявки.
        
    Returns:
        Список кортежей (назначение, техник).
    """
    result = await db.execute(
        select(models.TechnicianAssignment, models.User)
        .join(models.User, models.TechnicianAssignment.technician_id == models.User.user_id)
        .where(models.TechnicianAssignment.ticket_id == ticket_id)
        .order_by(models.TechnicianAssignment.assigned_at)
    )
    return list(result.tuples().all())

async def get_technician_tickets(
    db: AsyncSession, 
    *, 
    technician_id: int
) -> List[int]:
    """
    Получает список ID заявок, назначенных на техника.
    
    Args:
        db: Асинхронная сессия базы данных.
        technician_id: ID техника.
        
    Returns:
        Список ID заявок.
    """
    result = await db.execute(
        select(models.TechnicianAssignment.ticket_id)
        .where(models.TechnicianAssignment.technician_id == technician_id)
        .order_by(models.TechnicianAssignment.assigned_at.desc())
    )
    return list(result.scalars().all())

async def is_technician_assigned(
    db: AsyncSession, 
    *, 
    ticket_id: int, 
    technician_id: int
) -> bool:
    """
    Проверяет, назначен ли техник на заявку.
    
    Args:
        db: Асинхронная сессия базы данных.
        ticket_id: ID заявки.
        technician_id: ID техника.
        
    Returns:
        True, если техник назначен на заявку, иначе False.
    """
    result = await db.execute(
        select(models.TechnicianAssignment)
        .where(
            and_(
                models.TechnicianAssignment.ticket_id == ticket_id,
                models.TechnicianAssignment.technician_id == technician_id
            )
        )
    )
    return result.scalar_one_or_none() is not None
