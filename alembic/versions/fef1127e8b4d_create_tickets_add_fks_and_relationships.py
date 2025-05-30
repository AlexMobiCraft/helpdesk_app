"""Create tickets, add FKs and relationships

Revision ID: fef1127e8b4d
Revises: 67f3b10a1b57
Create Date: 2025-04-10 20:31:12.356340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fef1127e8b4d'
down_revision: Union[str, None] = '67f3b10a1b57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tickets',
    sa.Column('ticket_id', sa.Integer(), autoincrement=True, nullable=False, comment='Уникальный идентификатор заявки (Автоинкремент)'),
    sa.Column('device_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID устройства'),
    sa.Column('user_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID пользователя-автора'),
    sa.Column('description', sa.Text(), nullable=False, comment='Описание проблемы'),
    sa.Column('priority_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID приоритета'),
    sa.Column('status_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID статуса'),
    sa.Column('resolution_notes', sa.Text(), nullable=True, comment='Примечание по решению (может быть NULL)'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Дата и время создания'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Дата и время последнего обновления'),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True, comment='Дата и время закрытия (может быть NULL)'),
    sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], name=op.f('fk_tickets_device_id_devices')),
    sa.ForeignKeyConstraint(['priority_id'], ['priorities.priority_id'], name=op.f('fk_tickets_priority_id_priorities')),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.status_id'], name=op.f('fk_tickets_status_id_statuses')),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name=op.f('fk_tickets_user_id_users')),
    sa.PrimaryKeyConstraint('ticket_id', name=op.f('pk_tickets'))
    )
    op.create_index('ix_tickets_device_id', 'tickets', ['device_id'], unique=False)
    op.create_index(op.f('ix_tickets_priority_id'), 'tickets', ['priority_id'], unique=False)
    op.create_index('ix_tickets_status_id', 'tickets', ['status_id'], unique=False)
    op.create_index(op.f('ix_tickets_user_id'), 'tickets', ['user_id'], unique=False)
    op.create_table('files',
    sa.Column('file_id', sa.Integer(), autoincrement=True, nullable=False, comment='Уникальный идентификатор файла (Автоинкремент)'),
    sa.Column('ticket_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID заявки, к которой прикреплен файл'),
    sa.Column('file_name', sa.String(length=255), nullable=False, comment='Оригинальное имя файла'),
    sa.Column('file_path', sa.Text(), nullable=False, comment='Путь к файлу в хранилище'),
    sa.Column('file_type', sa.String(length=100), nullable=False, comment='MIME-тип файла'),
    sa.Column('file_size', sa.BigInteger(), nullable=False, comment='Размер файла в байтах'),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Дата и время загрузки файла'),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.ticket_id'], name=op.f('fk_files_ticket_id_tickets')),
    sa.PrimaryKeyConstraint('file_id', name=op.f('pk_files'))
    )
    op.create_index(op.f('ix_files_ticket_id'), 'files', ['ticket_id'], unique=False)
    op.create_table('technician_assignments',
    sa.Column('assignment_id', sa.Integer(), autoincrement=True, nullable=False, comment='Уникальный идентификатор назначения (Автоинкремент)'),
    sa.Column('ticket_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID заявки'),
    sa.Column('technician_id', sa.Integer(), nullable=False, comment='Внешний ключ, ID техника (из таблицы users)'),
    sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Дата и время назначения техника на заявку'),
    sa.ForeignKeyConstraint(['technician_id'], ['users.user_id'], name=op.f('fk_technician_assignments_technician_id_users')),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.ticket_id'], name=op.f('fk_technician_assignments_ticket_id_tickets')),
    sa.PrimaryKeyConstraint('assignment_id', name=op.f('pk_technician_assignments')),
    sa.UniqueConstraint('ticket_id', 'technician_id', name='uq_ticket_technician')
    )
    op.create_index(op.f('ix_technician_assignments_technician_id'), 'technician_assignments', ['technician_id'], unique=False)
    op.create_index(op.f('ix_technician_assignments_ticket_id'), 'technician_assignments', ['ticket_id'], unique=False)
    op.drop_index('ix_devices_inventory_number', table_name='devices')
    op.create_index('ix_devices_inventory_number', 'devices', ['inventory_number'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_devices_inventory_number', table_name='devices')
    op.create_index('ix_devices_inventory_number', 'devices', ['inventory_number'], unique=True)
    op.drop_index(op.f('ix_technician_assignments_ticket_id'), table_name='technician_assignments')
    op.drop_index(op.f('ix_technician_assignments_technician_id'), table_name='technician_assignments')
    op.drop_table('technician_assignments')
    op.drop_index(op.f('ix_files_ticket_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_tickets_user_id'), table_name='tickets')
    op.drop_index('ix_tickets_status_id', table_name='tickets')
    op.drop_index(op.f('ix_tickets_priority_id'), table_name='tickets')
    op.drop_index('ix_tickets_device_id', table_name='tickets')
    op.drop_table('tickets')
    # ### end Alembic commands ###
