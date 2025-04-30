"""split_fullname_to_firstname_lastname

Revision ID: 78b6e5beb0f8
Revises: 5c28c582472f
Create Date: 2025-04-13 12:34:20.582298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '78b6e5beb0f8'
down_revision: Union[str, None] = '5c28c582472f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем новые колонки first_name и last_name (оба необязательные)
    op.add_column('users', sa.Column('first_name', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(255), nullable=True))
    
    # Заполняем first_name и last_name данными из full_name
    # Подход через Python для работы с данными, чтобы избежать проблем совместимости SQL
    conn = op.get_bind()
    result = conn.execute(text("SELECT user_id, full_name FROM users WHERE full_name IS NOT NULL"))
    
    for row in result:
        user_id = row[0]
        full_name = row[1]
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        conn.execute(
            text("UPDATE users SET first_name = :first_name, last_name = :last_name WHERE user_id = :user_id"),
            {"first_name": first_name, "last_name": last_name, "user_id": user_id}
        )
    
    # Удаляем колонку full_name
    op.drop_column('users', 'full_name')


def downgrade() -> None:
    """Downgrade schema."""
    # Добавляем обратно колонку full_name
    op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))
    
    # Заполняем full_name данными из first_name и last_name
    conn = op.get_bind()
    result = conn.execute(text("SELECT user_id, first_name, last_name FROM users"))
    
    for row in result:
        user_id = row[0]
        first_name = row[1] or ''
        last_name = row[2] or ''
        full_name = f"{first_name} {last_name}".strip()
        
        conn.execute(
            text("UPDATE users SET full_name = :full_name WHERE user_id = :user_id"),
            {"full_name": full_name, "user_id": user_id}
        )
    
    # Устанавливаем NOT NULL для full_name
    op.alter_column('users', 'full_name', nullable=False)
    
    # Удаляем колонки first_name и last_name
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
