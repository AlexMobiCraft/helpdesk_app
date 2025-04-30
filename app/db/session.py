# Файл: app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.core.config import settings # Импортируем настройки для получения DATABASE_URL

# Создаем асинхронный движок SQLAlchemy
# pool_pre_ping=True - проверяет соединение перед использованием
# echo=False - отключаем логирование SQL-запросов в продакшене (можно включить для отладки)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False # Установите True для отладки SQL запросов
)

# Создаем фабрику асинхронных сессий
# expire_on_commit=False - позволяет использовать объекты после коммита сессии
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии базы данных.

    Использует async_sessionmaker для создания сессии и гарантирует
    ее закрытие после завершения запроса.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

# Можно добавить функцию для инициализации БД (например, создание таблиц),
# если не используется Alembic или для тестов.
# async def init_db():
#     async with engine.begin() as conn:
#         # await conn.run_sync(Base.metadata.drop_all) # Осторожно: удаляет все таблицы!
#         await conn.run_sync(Base.metadata.create_all)