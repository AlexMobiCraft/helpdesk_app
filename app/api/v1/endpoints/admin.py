# Файл: app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import io
import csv
from starlette.responses import StreamingResponse

from app.core.dependencies import get_current_admin_user 
from app.db.session import get_session
from app import crud, models, schemas

router = APIRouter()

# Здесь будут административные эндпоинты, например, создание заявки от имени пользователя

@router.post("/tickets", response_model=schemas.ticket.TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket_for_user(
    *, 
    db: AsyncSession = Depends(get_session),
    ticket_in: schemas.ticket.AdminTicketCreate, # Исправлено
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Создает новую заявку от имени указанного пользователя (только для администраторов).
    """
    # Проверяем, существует ли пользователь, от имени которого создается заявка
    target_user = await crud.user.get_user_by_id(db=db, user_id=ticket_in.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id {ticket_in.user_id} not found"
        )
        
    # Создаем заявку, передавая все данные из AdminTicketCreate
    # CRUD функция create_ticket ожидает схему TicketCreate, но мы передадим user_id явно
    # Создаем объект TicketCreate из AdminTicketCreate, исключая user_id
    ticket_create_obj = schemas.ticket.TicketCreate(**ticket_in.dict(exclude={'user_id'}))
    
    # Вызываем CRUD функцию для создания, передавая объект и user_id
    created_ticket = await crud.ticket.create_ticket(
        db=db, 
        obj_in=ticket_create_obj, 
        user_id=ticket_in.user_id
        # initial_status_id будет использован по умолчанию (1)
    )
    
    # Загружаем полную информацию о заявке, включая связи, чтобы соответствовать TicketRead
    full_ticket = await crud.ticket.get_ticket(db=db, ticket_id=created_ticket.ticket_id, with_related=True)
    if not full_ticket:
        # Этого не должно случиться, но на всякий случай
        raise HTTPException(status_code=500, detail="Failed to retrieve created ticket details after creation")

    return full_ticket

@router.get("/reports/tickets", response_class=StreamingResponse)
async def export_tickets_report(
    *, 
    db: AsyncSession = Depends(get_session),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Экспортирует отчет по заявкам в формате CSV с возможностью фильтрации.
    
    Доступно только администраторам.
    """
    
    # Получаем все заявки с учетом фильтров и загрузкой связанных данных
    tickets = await crud.ticket.get_tickets(
        db=db, 
        start_date=start_date, 
        end_date=end_date,
        status_id=status_id,
        priority_id=priority_id,
        user_id=user_id,
        device_id=device_id,
        with_related=True, 
        limit=10000 # Устанавливаем большой лимит для отчета
    )
    
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нет заявок, соответствующих критериям фильтрации")
        
    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовок CSV
    header = [
        "ID Заявки", "Дата Создания", "Дата Обновления", "Дата Закрытия", 
        "ID Пользователя", "Email Пользователя", "Имя Фамилия / Логин",
        "ID Устройства", "Имя Устройства", "Инв. Номер Устройства",
        "Описание", 
        "ID Приоритета", "Приоритет",
        "ID Статуса", "Статус",
        "Примечания к Решению"
    ]
    writer.writerow(header)
    
    # Записываем данные заявок
    for ticket in tickets:
        # Формируем имя пользователя
        user_display_name = ''
        if ticket.user:
            if ticket.user.first_name or ticket.user.last_name:
                user_display_name = f"{ticket.user.first_name or ''} {ticket.user.last_name or ''}".strip()
            else:
                user_display_name = ticket.user.username
            
        row = [
            ticket.ticket_id,
            ticket.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.created_at else '',
            ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.updated_at else '',
            ticket.closed_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.closed_at else '',
            ticket.user.user_id if ticket.user else '',
            ticket.user.email if ticket.user else '',
            user_display_name,
            ticket.device.device_id if ticket.device else '',
            ticket.device.name if ticket.device else '',
            ticket.device.inventory_number if ticket.device else '',
            ticket.description,
            ticket.priority.priority_id if ticket.priority else '',
            ticket.priority.name if ticket.priority else '',
            ticket.status.status_id if ticket.status else '',
            ticket.status.name if ticket.status else '',
            ticket.resolution_notes
        ]
        writer.writerow(row)
        
    output.seek(0)
    
    # Создаем имя файла с текущей датой
    filename = f"ticket_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    
    # Возвращаем StreamingResponse
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
