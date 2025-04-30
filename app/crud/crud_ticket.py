# Файл: app/crud/crud_ticket.py
from typing import Any, Dict, Optional, List, Union
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.ticket import Ticket
from app.models.technician_assignment import TechnicianAssignment
from app.schemas.ticket import TicketCreate, TicketUpdate
from datetime import datetime

async def create_ticket(
    db: AsyncSession, 
    *, 
    obj_in: TicketCreate, 
    user_id: int, 
    initial_status_id: int = 1  # По умолчанию "Новая"
) -> Ticket:
    """
    Создает новую заявку.
    
    Args:
        db: Асинхронная сессия базы данных.
        obj_in: Данные для создания заявки.
        user_id: ID пользователя, создающего заявку.
        initial_status_id: Начальный статус заявки (по умолчанию 1 - "Новая").
        
    Returns:
        Созданная заявка.
    """
    create_data = obj_in.model_dump()
    db_obj = Ticket(
        **create_data,
        user_id=user_id,
        status_id=initial_status_id
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_ticket(
    db: AsyncSession, 
    *, 
    ticket_id: int, 
    with_related: bool = False
) -> Optional[Ticket]:
    """
    Получает заявку по ID.
    
    Args:
        db: Асинхронная сессия базы данных.
        ticket_id: ID заявки для получения.
        with_related: Загружать ли связанные объекты.
        
    Returns:
        Заявка или None, если не найдена.
    """
    if with_related:
        query = select(Ticket).where(Ticket.ticket_id == ticket_id).options(
            selectinload(Ticket.user),
            selectinload(Ticket.device),
            selectinload(Ticket.priority),
            selectinload(Ticket.status),
            selectinload(Ticket.files),
            selectinload(Ticket.assignments).selectinload(TechnicianAssignment.technician)
        )
    else:
        query = select(Ticket).where(Ticket.ticket_id == ticket_id)
    
    result = await db.execute(query)
    return result.scalars().first()

async def get_tickets(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    device_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    with_related: bool = False
) -> List[Ticket]:
    """
    Получает список заявок с фильтрацией, сортировкой и пагинацией.
    
    Args:
        db: Асинхронная сессия базы данных.
        skip: Сколько записей пропустить (для пагинации).
        limit: Максимальное количество возвращаемых записей.
        user_id: Фильтрация по ID пользователя.
        status_id: Фильтрация по ID статуса.
        priority_id: Фильтрация по ID приоритета.
        device_id: Фильтрация по ID устройства.
        search: Поиск в описании заявки.
        sort_by: Поле для сортировки.
        sort_desc: Сортировка по убыванию.
        start_date: Начальная дата (created_at >= start_date).
        end_date: Конечная дата (created_at <= end_date).
        with_related: Загружать ли связанные объекты (user, device, status, priority).
        
    Returns:
        Список заявок.
    """
    query = select(Ticket)
    filters = []
    
    if user_id is not None:
        filters.append(Ticket.user_id == user_id)
    if status_id is not None:
        filters.append(Ticket.status_id == status_id)
    if priority_id is not None:
        filters.append(Ticket.priority_id == priority_id)
    if device_id is not None:
        filters.append(Ticket.device_id == device_id)
    if start_date is not None:
        filters.append(Ticket.created_at >= start_date)
    if end_date is not None:
        filters.append(Ticket.created_at <= end_date)
        
    if search:
        filters.append(Ticket.description.ilike(f"%{search}%"))
    
    if filters:
        query = query.where(and_(*filters))
        
    if with_related:
        query = query.options(
            selectinload(Ticket.user),
            selectinload(Ticket.device),
            selectinload(Ticket.status),
            selectinload(Ticket.priority),
            selectinload(Ticket.files),
            selectinload(Ticket.assignments).selectinload(TechnicianAssignment.technician)
        )

    order_column = getattr(Ticket, sort_by, Ticket.created_at)
    if sort_desc:
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

async def update_ticket(
    db: AsyncSession,
    *,
    db_obj: Ticket,
    obj_in: Union[TicketUpdate, Dict[str, Any]]
) -> Ticket:
    """
    Обновляет существующую заявку.
    
    Args:
        db: Асинхронная сессия базы данных.
        db_obj: Существующая заявка для обновления.
        obj_in: Данные для обновления.
        
    Returns:
        Обновленная заявка.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_ticket_status(
    db: AsyncSession,
    *,
    db_obj: Ticket,
    status_id: int,
    resolution_notes: Optional[str] = None,
    is_closing: bool = False
) -> Ticket:
    """
    Обновляет статус заявки.
    
    Args:
        db: Асинхронная сессия базы данных.
        db_obj: Существующая заявка для обновления.
        status_id: Новый ID статуса.
        resolution_notes: Примечания по решению (при закрытии).
        is_closing: Отмечает, является ли новый статус закрывающим.
        
    Returns:
        Обновленная заявка.
    """
    db_obj.status_id = status_id
    
    if resolution_notes is not None:
        db_obj.resolution_notes = resolution_notes
    
    if is_closing:
        from datetime import datetime
        db_obj.closed_at = datetime.now()
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_ticket_count(
    db: AsyncSession,
    *,
    user_id: Optional[int] = None,
    status_id: Optional[int] = None
) -> int:
    """
    Получает количество заявок с учетом фильтров.
    
    Args:
        db: Асинхронная сессия базы данных.
        user_id: Фильтрация по ID пользователя.
        status_id: Фильтрация по ID статуса.
        
    Returns:
        Количество заявок.
    """
    from sqlalchemy import func
    
    query = select(func.count()).select_from(Ticket)
    
    filters = []
    if user_id is not None:
        filters.append(Ticket.user_id == user_id)
    if status_id is not None:
        filters.append(Ticket.status_id == status_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    return result.scalar() or 0

async def delete_ticket(db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
    """Удаляет заявку из базы данных по ID."""
    result = await db.execute(
        select(Ticket).where(Ticket.ticket_id == ticket_id)
    )
    db_ticket = result.scalars().first()
    if db_ticket:
        await db.delete(db_ticket)
        await db.commit()
    return db_ticket

# === Функции для работы с файлами ===
