from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, text
from typing import List, Optional, Dict, Any, Union

from app.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate

async def get_user_role(db: AsyncSession, role_id: int) -> Optional[UserRole]:
    """
    Получает роль пользователя по ID.
    
    Args:
        db: Асинхронная сессия базы данных.
        role_id: ID роли для поиска.
        
    Returns:
        Объект UserRole, если найден, иначе None.
    """
    result = await db.execute(select(UserRole).where(UserRole.id == role_id))
    return result.scalars().first()

async def get_user_role_by_name(db: AsyncSession, name: str) -> Optional[UserRole]:
    """
    Получает роль пользователя по имени.
    
    Args:
        db: Асинхронная сессия базы данных.
        name: Имя роли для поиска.
        
    Returns:
        Объект UserRole, если найден, иначе None.
    """
    result = await db.execute(select(UserRole).where(UserRole.name == name))
    return result.scalars().first()

async def get_user_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[UserRole]:
    """
    Получает список ролей пользователей с пагинацией.
    
    Args:
        db: Асинхронная сессия базы данных.
        skip: Количество записей для пропуска.
        limit: Максимальное количество записей для возврата.
        
    Returns:
        Список объектов UserRole.
    """
    result = await db.execute(select(UserRole).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user_role(db: AsyncSession, *, obj_in: UserRoleCreate) -> UserRole:
    """
    Создает новую роль пользователя.
    
    Args:
        db: Асинхронная сессия базы данных.
        obj_in: Схема с данными для создания роли.
        
    Returns:
        Созданный объект UserRole.
        
    Raises:
        ValueError: Если роль с таким именем уже существует.
    """
    # Проверяем, существует ли роль с таким именем
    existing_role = await get_user_role_by_name(db, name=obj_in.name)
    if existing_role:
        raise ValueError(f"Роль с именем '{obj_in.name}' уже существует.")
    
    # Получаем максимальный существующий ID
    result = await db.execute(text("SELECT MAX(id) FROM user_roles"))
    max_id = result.scalar() or 0
    next_id = max_id + 1
    
    # Создаем объект роли с явным указанием ID
    db_obj = UserRole(id=next_id, **obj_in.model_dump())
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_user_role(
    db: AsyncSession, *, role_id: int, obj_in: Union[UserRoleUpdate, Dict[str, Any]]
) -> Optional[UserRole]:
    """
    Обновляет роль пользователя.
    
    Args:
        db: Асинхронная сессия базы данных.
        role_id: ID роли для обновления.
        obj_in: Схема или словарь с данными для обновления.
        
    Returns:
        Обновленный объект UserRole или None, если роль не найдена.
        
    Raises:
        ValueError: Если новое имя роли уже используется другой ролью.
    """
    db_obj = await get_user_role(db, role_id=role_id)
    if not db_obj:
        return None
    
    # Преобразуем схему в словарь, если это не словарь
    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    
    # Проверяем, есть ли другая роль с таким же именем, если имя меняется
    if "name" in update_data and update_data["name"] != db_obj.name:
        existing_role = await get_user_role_by_name(db, name=update_data["name"])
        if existing_role and existing_role.id != role_id:
            raise ValueError(f"Роль с именем '{update_data['name']}' уже существует.")
    
    # Обновляем поля объекта
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_user_role(db: AsyncSession, *, role_id: int) -> Optional[UserRole]:
    """
    Удаляет роль пользователя.
    
    Args:
        db: Асинхронная сессия базы данных.
        role_id: ID роли для удаления.
        
    Returns:
        Удаленный объект UserRole или None, если роль не найдена.
    """
    db_obj = await get_user_role(db, role_id=role_id)
    if not db_obj:
        return None
    
    await db.delete(db_obj)
    await db.commit()
    return db_obj
