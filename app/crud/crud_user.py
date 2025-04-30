from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any
from sqlalchemy import update as sqlalchemy_update # Импортируем update

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate # Импортируем схемы
from app.core.security import get_password_hash # Импортируем функцию хэширования

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Получает пользователя из базы данных по имени пользователя.

    Args:
        db: Асинхронная сессия базы данных.
        username: Имя пользователя для поиска.

    Returns:
        Объект User, если найден, иначе None.
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получает пользователя из базы данных по его ID.

    Args:
        db: Асинхронная сессия базы данных.
        user_id: ID пользователя для поиска.

    Returns:
        Объект User, если найден, иначе None.
    """
    result = await db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Получает список пользователей с пагинацией.
    """
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.user_id)
    )
    return result.scalars().all()

async def create_user(db: AsyncSession, *, obj_in: UserCreate) -> User:
    """
    Создает нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким username
    existing_user = await get_user_by_username(db, username=obj_in.username)
    if existing_user:
        raise ValueError(f"Username '{obj_in.username}' is already registered.")

    # TODO: Проверить существование email, если он станет обязательным в модели

    # Создаем объект пользователя, хэшируя пароль
    hashed_password = get_password_hash(obj_in.password)
    # Используем model_dump с exclude, чтобы не передавать пароль напрямую в модель
    create_data = obj_in.model_dump(exclude={"password"})
    db_obj = User(**create_data, password_hash=hashed_password)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_user(
    db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | Dict[str, Any]
) -> User:
    """
    Обновляет данные пользователя.
    Пароль не обновляется этой функцией.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        # Используем model_dump с exclude_unset=True, чтобы обновлять только переданные поля
        update_data = obj_in.model_dump(exclude_unset=True)

    # Не позволяем обновлять пароль через этот метод
    update_data.pop("password", None)
    update_data.pop("password_hash", None)

    # Игнорируем нулевое значение role_id
    if "role_id" in update_data and (update_data["role_id"] is None or update_data["role_id"] == 0):
        update_data.pop("role_id")

    if update_data:
        # Проверяем уникальность username, если он меняется
        if "username" in update_data and update_data["username"] != db_obj.username:
             existing_user = await get_user_by_username(db, username=update_data["username"])
             if existing_user:
                 raise ValueError(f"Username '{update_data['username']}' is already registered.")

        # TODO: Проверить уникальность email, если он станет обязательным и будет меняться

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def remove_user(db: AsyncSession, *, user_id: int) -> Optional[User]:
    """
    Удаляет пользователя по ID.
    """
    db_obj = await get_user_by_id(db, user_id=user_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj # Возвращаем удаленный объект или None
# Другие CRUD функции для пользователя (create, update, delete) будут добавлены позже.