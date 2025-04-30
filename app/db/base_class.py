# Файл: app/db/base_class.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# Соглашение об именовании индексов и ключей для PostgreSQL.
# Это помогает Alembic генерировать консистентные имена для ограничений БД.
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    
    # Базовый класс для всех моделей SQLAlchemy.
    # Использует соглашение об именовании для PostgreSQL.
  
    # Применяем соглашение об именовании к метаданным
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
    # Здесь можно будет добавлять общие поля или методы для всех моделей
    pass