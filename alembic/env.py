# Файл: alembic/env.py
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine # Используем AsyncEngine

from alembic import context

# --- Загрузка .env ---
from dotenv import load_dotenv
# Определяем путь к корневой папке проекта относительно env.py
project_root = os.path.join(os.path.dirname(__file__), '..')
# Загружаем переменные (без явной кодировки, UTF-8 обычно по умолчанию в Linux/WSL)
load_dotenv(os.path.join(project_root, '.env'))
# --- Конец ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Установка URL из .env ---
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL не установлена в .env файле")
# Устанавливаем URL для использования в engine_from_config и run_migrations_offline
config.set_main_option('sqlalchemy.url', db_url)
# --- Конец ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# --- Настройка target_metadata ---
from app.db.base_class import Base
# Импортируем все модели через app.db.base
from app.db.base import *
target_metadata = Base.metadata

# other values from the config...

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = db_url # Используем URL, полученный из .env
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# --- Вспомогательная функция для запуска миграций ---
def do_run_migrations(connection):
    """Выполняет миграции в переданном соединении."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# --- Асинхронная функция для online режима ---
async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (Асинхронная версия)."""

    # Создаем синхронный движок из конфигурации (для получения URL/диалекта)
    sync_engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool, # Не используем пул для миграций
    )

    # Создаем асинхронный connectable (движок)
    connectable = AsyncEngine(sync_engine)

    # Выполняем миграции асинхронно
    async with connectable.connect() as connection:
        # Используем run_sync для выполнения синхронной do_run_migrations
        await connection.run_sync(do_run_migrations)

    # Освобождаем ресурсы асинхронного движка
    await connectable.dispose()

# --- Выбор режима выполнения (в конце файла) ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаем асинхронную функцию через asyncio.run
    # Используется стандартная для Linux/WSL политика цикла событий
    asyncio.run(run_migrations_online())
# --- Конец ---