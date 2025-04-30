# -*- coding: utf-8 -*-
"""seed initial data for priorities, statuses and admin user

Revision ID: <твой_уникальный_ID_ревизии>
Revises: <ID_предыдущей_ревизии_со_схемой>
Create Date: <дата_создания>

"""
from typing import Sequence, Union
import datetime

from alembic import op
import sqlalchemy as sa

# !!! Адаптируй путь импорта к твоей структуре проекта !!!
# Например, если твои модели в app/models/models.py
# from app.models.models import Priorities, Statuses, Users # или как они у тебя называются
# Либо определи таблицы здесь для bulk_insert
from app.core.security import get_password_hash # Убедись, что путь верный

# Определяем структуры таблиц (если не хочешь импортировать модели целиком)
# Это полезно, чтобы миграции не зависели напрямую от кода моделей,
# который может меняться. Имена таблиц должны совпадать с реальными.
priorities_table = sa.table(
    "priorities",
    sa.column("priority_id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("display_order", sa.Integer)
)

statuses_table = sa.table(
    "statuses",
    sa.column("status_id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("display_order", sa.Integer)
)

users_table = sa.table(
    "users",
    sa.column("user_id", sa.Integer),
    sa.column("username", sa.String),
    sa.column("password_hash", sa.String),
    sa.column("full_name", sa.String),
    sa.column("role", sa.String),
    sa.column("department", sa.String),
    sa.column("created_at", sa.TIMESTAMP),
    sa.column("updated_at", sa.TIMESTAMP)
    # Добавь другие обязательные колонки, если они есть и не имеют DEFAULT
)

# --- Начальные данные ---
DEFAULT_PRIORITIES = [
    {'priority_id': 1, 'name': 'Низкий', 'display_order': 3},
    {'priority_id': 2, 'name': 'Средний', 'display_order': 2},
    {'priority_id': 3, 'name': 'Высокий', 'display_order': 1},
    {'priority_id': 4, 'name': 'Критический', 'display_order': 0},
]

DEFAULT_STATUSES = [
    {'status_id': 1, 'name': 'Новая', 'display_order': 1},
    {'status_id': 2, 'name': 'Ожидает решения', 'display_order': 2},
    {'status_id': 3, 'name': 'В работе', 'display_order': 3},
    {'status_id': 4, 'name': 'Закрыта', 'display_order': 4},
]

# --- Данные администратора ---
# !!! ВАЖНО: Выбери надежный пароль и храни его безопасно в реальном проекте !!!
# Не оставляй пароль в открытом виде в коде для продакшена.
# Используй переменные окружения или другие безопасные методы.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Don.72.don" # !!! ИЗМЕНИ ЭТОТ ПАРОЛЬ !!!
ADMIN_FULL_NAME = "Администратор Системы"
ADMIN_ROLE = "admin"
ADMIN_DEPARTMENT = "Администрация"

# revision identifiers, used by Alembic.
revision: str = '9896214bcfff' # Оставь ID, который сгенерировал Alembic
down_revision: Union[str, None] = 'fef1127e8b4d' # Оставь ID, который сгенерировал Alembic
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    print("Seeding initial data for priorities...")
    op.bulk_insert(priorities_table, DEFAULT_PRIORITIES)
    print("Priorities seeded.")

    print("Seeding initial data for statuses...")
    op.bulk_insert(statuses_table, DEFAULT_STATUSES)
    print("Statuses seeded.")

    print("Creating initial admin user...")
    hashed_password = get_password_hash(ADMIN_PASSWORD)
    # now = datetime.datetime.now(datetime.timezone.utc) # Используем UTC
    now = datetime.datetime.utcnow() # Получаем текущее время UTC как naive datetime

    op.bulk_insert(
        users_table,
        [
            {
                # user_id должен быть автоинкрементным, не указываем его здесь, если так настроено
                'username': ADMIN_USERNAME,
                'password_hash': hashed_password,
                'full_name': ADMIN_FULL_NAME,
                'role': ADMIN_ROLE,
                'department': ADMIN_DEPARTMENT,
                'created_at': now,
                'updated_at': now
                # Добавь NULL или значения по умолчанию для других полей, если нужно
            }
        ]
    )
    print(f"Admin user '{ADMIN_USERNAME}' created.")


def downgrade() -> None:
    # ВАЖНО: Удаление данных может быть опасным.
    # Мы удаляем только те данные, которые точно создали в upgrade().
    # Используем bind для выполнения запросов удаления.
    bind = op.get_bind()

    print("Deleting initial admin user...")
    # Удаляем конкретного пользователя
    bind.execute(
        sa.delete(users_table).where(users_table.c.username == sa.text(f"'{ADMIN_USERNAME}'"))
    )
    print("Admin user deleted.")

    print("Deleting initial statuses...")
    # Удаляем статусы по их ID
    status_ids = [s['status_id'] for s in DEFAULT_STATUSES]
    bind.execute(
        sa.delete(statuses_table).where(statuses_table.c.status_id.in_(status_ids))
    )
    print("Statuses deleted.")

    print("Deleting initial priorities...")
    # Удаляем приоритеты по их ID
    priority_ids = [p['priority_id'] for p in DEFAULT_PRIORITIES]
    bind.execute(
        sa.delete(priorities_table).where(priorities_table.c.priority_id.in_(priority_ids))
    )
    print("Priorities deleted.")