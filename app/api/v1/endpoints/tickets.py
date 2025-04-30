# Файл: app/api/v1/endpoints/tickets.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Response
from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
import uuid
from pathlib import Path

from app import models, schemas, crud
from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.core.config import settings # Импорт настроек
from app.schemas.file import FileCreate

router = APIRouter()

# --- Эндпоинты для работы с заявками ---

@router.post(
    "", 
    response_model=schemas.ticket.TicketRead, 
    status_code=status.HTTP_201_CREATED,
    tags=["Tickets"]
)
async def create_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_in: schemas.ticket.TicketCreate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Создает новую заявку.
    
    - Автоматически проставляет user_id из токена аутентификации
    - Автоматически устанавливает статус "Новая" (или другой начальный статус)
    """
    # Получение ID начального статуса (по умолчанию 1 - "Новая")
    initial_status_id = 1  # В продакшене можно получать из конфигурации или БД
    
    # Проверяем существование устройства перед созданием заявки
    device = await crud.device.get_device(db=db, device_id=ticket_in.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Устройство с ID {ticket_in.device_id} не найдено"
        )
    
    ticket = await crud.ticket.create_ticket(
        db=db, 
        obj_in=ticket_in, 
        user_id=current_user.user_id, 
        initial_status_id=initial_status_id
    )
    
    # Загружаем связанные файлы для ответа
    await db.refresh(ticket, ['files'])
    
    return ticket

@router.get(
    "", 
    response_model=List[schemas.ticket.TicketDetailRead],
    tags=["Tickets"]
)
async def read_tickets(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=100, description="Максимальное количество записей для возврата"),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    status_id: Optional[int] = Query(None, description="Фильтр по ID статуса"),
    priority_id: Optional[int] = Query(None, description="Фильтр по ID приоритета"),
    device_id: Optional[int] = Query(None, description="Фильтр по ID устройства"),
    search: Optional[str] = Query(None, description="Поиск по описанию заявки"),
    sort_by: str = Query("created_at", description="Поле для сортировки"),
    sort_desc: bool = Query(True, description="Сортировка по убыванию")
) -> Any:
    """
    Получает список всех заявок с возможностью фильтрации, сортировки и пагинации.
    """
    # Проверяем роль пользователя для определения ограничений
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Получаем заявки с учетом фильтров
    tickets = await crud.ticket.get_tickets(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        status_id=status_id,
        priority_id=priority_id,
        device_id=device_id,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
        with_related=True
    )
    
    return tickets

@router.get(
    "/{ticket_id}", 
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def read_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Получает детальную информацию о заявке по её ID.
    Все пользователи могут просматривать любую заявку.
    """
    # Получаем заявку с загрузкой связанных объектов
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return ticket

@router.patch(
    "/{ticket_id}",
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def update_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    ticket_in: schemas.ticket.TicketUpdate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Частично обновляет заявку по её ID.
    
    Права доступа:
    - Обычные пользователи могут обновлять только свои заявки и только определенные поля
    - Техники могут обновлять поля заявок, назначенных им
    - Администраторы могут обновлять любые поля любых заявок
    """
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    
    # Проверяем права доступа
    if user_role == "user" and ticket.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления этой заявки"
        )
    
    # Проверяем, закрыта ли заявка
    if ticket.closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя редактировать закрытую заявку. Используйте специальный эндпоинт для редактирования закрытых заявок."
        )
    
    # Ограничиваем поля, которые может изменять обычный пользователь
    if user_role == "user":
        allowed_fields = {"description", "device_id"}
        update_data = {}
        for field, value in ticket_in.model_dump(exclude_unset=True).items():
            if field in allowed_fields:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет полей, доступных для обновления"
            )
        
        # Проверяем существование устройства, если оно изменяется
        if "device_id" in update_data:
            device = await crud.device.get_device(db=db, device_id=update_data["device_id"])
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Устройство с ID {update_data['device_id']} не найдено"
                )
        
        # Обновляем заявку с ограниченными полями
        updated_ticket = await crud.ticket.update_ticket(
            db=db,
            db_obj=ticket,
            obj_in=update_data
        )
    else:
        # Техники и администраторы могут изменять все поля
        # Проверяем существование устройства, если оно изменяется
        update_data = ticket_in.model_dump(exclude_unset=True)
        if "device_id" in update_data:
            device = await crud.device.get_device(db=db, device_id=update_data["device_id"])
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Устройство с ID {update_data['device_id']} не найдено"
                )
        
        updated_ticket = await crud.ticket.update_ticket(
            db=db,
            db_obj=ticket,
            obj_in=update_data
        )
    
    # Загружаем связанные объекты для ответа
    # await db.refresh(updated_ticket, ['user', 'device', 'priority', 'status', 'assignments', 'files'])
    # Теперь get_ticket с with_related=True сам подгружает все, включая файлы
    full_updated_ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    if not full_updated_ticket:
        # Этого не должно произойти, если update_ticket прошел успешно
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена после обновления")
    
    return full_updated_ticket

@router.post(
    "/{ticket_id}/status",
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def update_ticket_status(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    status_update: schemas.ticket.TicketStatusUpdate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Обновляет статус заявки.
    
    Права доступа:
    - Обычные пользователи не могут менять статус заявок
    - Техники могут менять статус заявок, назначенных им
    - Администраторы могут менять статус любых заявок
    
    При установке финального статуса автоматически проставляется дата закрытия.
    """
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Обычные пользователи не могут менять статус
    if user_role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обычные пользователи не могут изменять статус заявок"
        )
    
    # Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    
    # Получаем новый статус из базы для проверки
    new_status = await crud.status.get_status(db=db, status_id=status_update.status_id)
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Статус с ID {status_update.status_id} не найден"
        )
    
    # Проверяем, является ли новый статус закрывающим
    is_closing = new_status.is_final
    
    # Проверяем требование указания resolution_notes при закрытии
    if is_closing and not status_update.resolution_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="При закрытии заявки необходимо указать примечания по решению"
        )
    
    # Обновляем статус заявки
    updated_ticket = await crud.ticket.update_ticket_status(
        db=db,
        db_obj=ticket,
        status_id=status_update.status_id,
        resolution_notes=status_update.resolution_notes,
        is_closing=is_closing
    )
    
    # Загружаем связанные объекты для ответа
    await db.refresh(updated_ticket, ['user', 'device', 'priority', 'status', 'assignments', 'files'])
    
    return updated_ticket

@router.post(
    "/{ticket_id}/edit-closed",
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def edit_closed_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    ticket_in: schemas.ticket.TicketUpdate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Специальный эндпоинт для редактирования закрытых заявок.
    
    Только администраторы могут редактировать закрытые заявки.
    """
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Только администраторы могут редактировать закрытые заявки
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут редактировать закрытые заявки"
        )
    
    # Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    
    # Проверяем, действительно ли заявка закрыта
    if ticket.closed_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка не закрыта. Используйте обычный эндпоинт обновления."
        )
    
    # Проверяем существование устройства, если оно изменяется
    update_data = ticket_in.model_dump(exclude_unset=True)
    if "device_id" in update_data:
        device = await crud.device.get_device(db=db, device_id=update_data["device_id"])
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Устройство с ID {update_data['device_id']} не найдено"
            )
    
    # Обновляем заявку
    updated_ticket = await crud.ticket.update_ticket(
        db=db,
        db_obj=ticket,
        obj_in=update_data
    )
    
    # Загружаем связанные объекты для ответа
    await db.refresh(updated_ticket, ['user', 'device', 'priority', 'status', 'assignments', 'files'])
    
    return updated_ticket

@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tickets"]
)
async def delete_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаляет заявку по ID. Администраторы могут удалять любые, пользователи — только свои.
    """
    # Получаем роль пользователя и заявку
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    if user_role != "admin" and ticket.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для удаления этой заявки")
    # Удаляем заявку
    await crud.ticket.delete_ticket(db=db, ticket_id=ticket_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Эндпоинты для работы с назначением техников ---

@router.post(
    "/{ticket_id}/assign",
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def assign_technician_to_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    technician_data: schemas.technician_assignment.TechnicianAssignmentCreate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Назначает техника на заявку.
    
    Права доступа:
    - Обычные пользователи не могут назначать техников
    - Техники могут назначать только себя на заявки
    - Администраторы могут назначать любых техников на любые заявки
    """
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Обычные пользователи не могут назначать техников
    if user_role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обычные пользователи не могут назначать техников на заявки"
        )
    
    # Техники могут назначать только себя
    if user_role == "tech" and technician_data.technician_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Техники могут назначать только себя на заявки"
        )
    
    # Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    
    # Проверяем, что техник существует и имеет роль "technician"
    technician = await crud.user.get_user_by_id(db=db, user_id=technician_data.technician_id)
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {technician_data.technician_id} не найден"
        )
    
    await db.refresh(technician, ['role'])
    if not technician.role or technician.role.name != "technician":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с ID {technician_data.technician_id} не является техником"
        )
    
    # Проверяем, не закрыта ли заявка
    if ticket.closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя назначать техников на закрытые заявки"
        )
    
    # Проверяем, не назначен ли уже этот техник на данную заявку
    is_assigned = await crud.technician_assignment.is_technician_assigned(
        db=db, ticket_id=ticket_id, technician_id=technician_data.technician_id
    )
    if is_assigned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Техник с ID {technician_data.technician_id} уже назначен на эту заявку"
        )
    
    # Назначаем техника на заявку
    await crud.technician_assignment.assign_technician(
        db=db, ticket_id=ticket_id, technician_id=technician_data.technician_id
    )
    
    # Получаем обновленные данные о заявке для ответа
    updated_ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    return updated_ticket

@router.delete(
    "/{ticket_id}/unassign/{technician_id}",
    response_model=schemas.ticket.TicketDetailRead,
    tags=["Tickets"]
)
async def remove_technician_from_ticket(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    technician_id: int,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Снимает техника с заявки.
    
    Права доступа:
    - Обычные пользователи не могут снимать техников
    - Техники могут снимать только себя с заявок
    - Администраторы могут снимать любых техников с любых заявок
    """
    # Получаем роль пользователя
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    
    # Обычные пользователи не могут снимать техников
    if user_role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обычные пользователи не могут снимать техников с заявок"
        )
    
    # Техники могут снимать только себя
    if user_role == "technician" and technician_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Техники могут снимать только себя с заявок"
        )
    
    # Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    
    # Проверяем, не закрыта ли заявка
    if ticket.closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя снимать техников с закрытых заявок"
        )
    
    # Проверяем, назначен ли этот техник на данную заявку
    is_assigned = await crud.technician_assignment.is_technician_assigned(
        db=db, ticket_id=ticket_id, technician_id=technician_id
    )
    if not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Техник с ID {technician_id} не назначен на эту заявку"
        )
    
    # Снимаем техника с заявки
    await crud.technician_assignment.remove_technician(
        db=db, ticket_id=ticket_id, technician_id=technician_id
    )
    
    # Получаем обновленные данные о заявке для ответа
    updated_ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    
    return updated_ticket

# --- Эндпоинты для работы с файлами --- #

@router.post(
    "/{ticket_id}/files", 
    response_model=List[schemas.file.FileRead], 
    status_code=status.HTTP_201_CREATED,
    tags=["Files"], # Группируем в категорию Files
    summary="Загрузить файл к заявке"
)
async def upload_ticket_files(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Загружает файлы к заявке.
    """
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    if ticket.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет права загружать файлы для этой заявки")
    saved_files = []
    upload_dir = Path(settings.UPLOAD_DIRECTORY)
    upload_dir.mkdir(parents=True, exist_ok=True)
    for upload in files:
        ext = Path(upload.filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = upload_dir / unique_name
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        file_obj = await crud.file.create_file(
            db=db,
            obj_in=FileCreate(
                ticket_id=ticket_id,
                file_name=upload.filename,
                file_path=unique_name, # Сохраняем только имя файла
                file_type=upload.content_type,
                file_size=os.path.getsize(dest_path)
            )
        )
        saved_files.append(file_obj)
    return saved_files

@router.post(
    "/{ticket_id}/files", 
    response_model=schemas.file.FileRead, 
    status_code=status.HTTP_201_CREATED,
    tags=["Files"], # Группируем в категорию Files
    summary="Загрузить файл к заявке"
)
async def upload_ticket_file(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Загружает файл и прикрепляет его к указанной заявке.

    Права доступа:
    - Автор заявки
    - Назначенный техник
    - Администратор
    """
    # 1. Получаем заявку
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id, with_related=True)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")

    # 2. Проверяем права доступа
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    is_owner = ticket.user_id == current_user.user_id
    # Проверяем, является ли текущий пользователь назначенным техником
    assigned_technician_ids = {assign.technician_id for assign in ticket.assignments}
    is_assigned_technician = current_user.user_id in assigned_technician_ids

    if not (is_owner or is_assigned_technician or user_role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для загрузки файла к этой заявке"
        )

    # 3. Обработка файла
    upload_dir = Path(settings.UPLOAD_DIRECTORY) / f"ticket_{ticket_id}"
    upload_dir.mkdir(parents=True, exist_ok=True) # Создаем директорию, если не существует

    # Генерируем безопасное имя файла
    file_extension = Path(file.filename).suffix
    # TODO: Добавить проверку на допустимые расширения и MIME-типы, если нужно
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / safe_filename
    relative_path = f"ticket_{ticket_id}/{safe_filename}" # Сохраняем относительный путь

    # Сохраняем файл
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # TODO: Улучшить обработку ошибок сохранения файла
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при сохранении файла: {e}")
    finally:
        await file.close()

    # 4. Создаем запись в БД
    file_size = file_path.stat().st_size
    file_in = schemas.file.FileCreate(
        file_name=file.filename, # Сохраняем оригинальное имя
        file_path=relative_path, # Сохраняем относительный путь с папкой ticket_{ticket_id}
        file_type=file.content_type,
        file_size=file_size,
        ticket_id=ticket_id
    )
    db_file = await crud.file.create_file(db=db, obj_in=file_in)

    return db_file

@router.delete(
    "/{ticket_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Files"],
    summary="Удалить файл из заявки"
)
async def delete_ticket_file(
    *,
    db: AsyncSession = Depends(get_session),
    ticket_id: int,
    file_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаляет файл, прикрепленный к заявке.

    Удаляет как запись из БД, так и сам файл с диска.

    Права доступа:
    - Автор заявки
    - Назначенный техник
    - Администратор
    """
    # 1. Получаем информацию о файле из БД
    file_record = await crud.file.get_file(db=db, file_id=file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    # 2. Проверяем, принадлежит ли файл указанной заявке
    if file_record.ticket_id != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не принадлежит указанной заявке"
        )

    # 3. Получаем заявку для проверки прав
    # Можно не загружать все связанные данные, если они не нужны для проверки прав
    ticket = await crud.ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        # Эта ситуация маловероятна, если file_record найден, но для надежности
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Связанная заявка не найдена")

    # 4. Проверяем права доступа
    await db.refresh(current_user, ['role'])
    user_role = current_user.role.name if current_user.role else "user"
    is_owner = ticket.user_id == current_user.user_id
    # Проверяем, является ли текущий пользователь назначенным техником
    # Для удаления может потребоваться загрузка назначений
    await db.refresh(ticket, ['assignments'])
    assigned_technician_ids = {assign.technician_id for assign in ticket.assignments}
    is_assigned_technician = current_user.user_id in assigned_technician_ids

    if not (is_owner or is_assigned_technician or user_role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления этого файла"
        )

    # 5. Удаляем файл с диска
    full_file_path = Path(settings.UPLOAD_DIRECTORY) / file_record.file_path
    if full_file_path.is_file():
        try:
            os.remove(full_file_path)
        except OSError as e:
            # TODO: Логировать ошибку удаления файла
            # Не прерываем процесс, если файл уже удален, но удаляем запись из БД
            print(f"Ошибка удаления файла {full_file_path}: {e}")
            pass # Можно продолжить и удалить запись из БД
    else:
        # TODO: Логировать, что файл не найден на диске
        print(f"Файл не найден на диске: {full_file_path}")
        pass # Файла нет, но запись в БД удаляем

    # 6. Удаляем запись из БД
    deleted_file = await crud.file.delete_file(db=db, file_id=file_id)
    if not deleted_file: # Дополнительная проверка, хотя get_file уже был
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ошибка при удалении записи о файле из БД")

    return # Возвращаем 204 No Content
