# alembic_migrations/script.py.mako
"""Initial migration for core tables

Revision ID: d10040ec2cb7
Revises: 
Create Date: 2025-06-14 08:36:19.434958

"""
from typing import Sequence, Union

from alembic import op # type: ignore
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd10040ec2cb7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mod_example_table_one',
    sa.Column('name', sa.String(length=100), nullable=False, comment='Пример текстового поля'),
    sa.Column('description', sa.String(length=255), nullable=True, comment='Описание для примера'),
    sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_mod_example_table_one'))
    )
    op.create_index(op.f('ix_mod_example_table_one_id'), 'mod_example_table_one', ['id'], unique=False)
    op.create_table('mod_example_user_notes',
    sa.Column('user_telegram_id', sa.BigInteger(), nullable=False, comment='Telegram ID пользователя-владельца заметки'),
    sa.Column('note_text', sa.Text(), nullable=False, comment='Текст заметки'),
    sa.Column('is_done', sa.Boolean(), nullable=False, comment='Отмечена ли заметка как выполненная'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_mod_example_user_notes'))
    )
    op.create_index(op.f('ix_mod_example_user_notes_id'), 'mod_example_user_notes', ['id'], unique=False)
    op.create_index(op.f('ix_mod_example_user_notes_user_telegram_id'), 'mod_example_user_notes', ['user_telegram_id'], unique=False)
    op.create_table('sdb_permissions',
    sa.Column('name', sa.String(length=100), nullable=False, comment="Уникальное имя разрешения (например, 'view_users', 'manage_modules')"),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание разрешения'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_permissions'))
    )
    op.create_index(op.f('ix_sdb_permissions_id'), 'sdb_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_permissions_name'), 'sdb_permissions', ['name'], unique=True)
    op.create_table('sdb_roles',
    sa.Column('name', sa.String(length=50), nullable=False, comment='Уникальное имя роли'),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание роли'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_roles'))
    )
    op.create_index(op.f('ix_sdb_roles_id'), 'sdb_roles', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_roles_name'), 'sdb_roles', ['name'], unique=True)
    op.create_table('sdb_users',
    sa.Column('username_lower', sa.String(length=32), nullable=True, comment='Telegram username в нижнем регистре для поиска'),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False, comment='Уникальный Telegram ID пользователя'),
    sa.Column('username', sa.String(length=32), nullable=True, comment='Telegram username (оригинальный регистр)'),
    sa.Column('first_name', sa.String(length=255), nullable=True, comment='Имя пользователя'),
    sa.Column('last_name', sa.String(length=255), nullable=True, comment='Фамилия пользователя'),
    sa.Column('preferred_language_code', sa.String(length=10), nullable=True, comment='Код языка бота'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Активен ли пользователь'),
    sa.Column('is_bot_blocked', sa.Boolean(), nullable=False, comment='Заблокировал ли пользователь бота'),
    sa.Column('last_activity_at', sa.DateTime(), nullable=True, comment='Время последней активности'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_users'))
    )
    op.create_index(op.f('ix_sdb_users_id'), 'sdb_users', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_users_telegram_id'), 'sdb_users', ['telegram_id'], unique=True)
    op.create_index(op.f('ix_sdb_users_username'), 'sdb_users', ['username'], unique=False)
    op.create_index(op.f('ix_sdb_users_username_lower'), 'sdb_users', ['username_lower'], unique=False)
    op.create_table('mod_another_example_table',
    sa.Column('example_one_id', sa.Integer(), nullable=True),
    sa.Column('value', sa.String(length=200), nullable=False, comment='Пример строкового значения'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['example_one_id'], ['mod_example_table_one.id'], name=op.f('fk_mod_another_example_table_example_one_id_mod_example_table_one'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_mod_another_example_table'))
    )
    op.create_index(op.f('ix_mod_another_example_table_id'), 'mod_another_example_table', ['id'], unique=False)
    op.create_table('sdb_role_permissions',
    sa.Column('role_id', sa.Integer(), nullable=False, comment='ID роли'),
    sa.Column('permission_id', sa.Integer(), nullable=False, comment='ID разрешения'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['sdb_permissions.id'], name=op.f('fk_sdb_role_permissions_permission_id_sdb_permissions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['sdb_roles.id'], name=op.f('fk_sdb_role_permissions_role_id_sdb_roles'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_role_permissions')),
    sa.UniqueConstraint('role_id', 'permission_id', name='uq_sdb_role_permissions_role_id_permission_id')
    )
    op.create_index(op.f('ix_sdb_role_permissions_id'), 'sdb_role_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_role_permissions_permission_id'), 'sdb_role_permissions', ['permission_id'], unique=False)
    op.create_index(op.f('ix_sdb_role_permissions_role_id'), 'sdb_role_permissions', ['role_id'], unique=False)
    op.create_table('sdb_user_permissions',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='ID пользователя'),
    sa.Column('permission_id', sa.Integer(), nullable=False, comment='ID разрешения'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['sdb_permissions.id'], name=op.f('fk_sdb_user_permissions_permission_id_sdb_permissions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['sdb_users.id'], name=op.f('fk_sdb_user_permissions_user_id_sdb_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_user_permissions')),
    sa.UniqueConstraint('user_id', 'permission_id', name='uq_sdb_user_permissions_user_id_permission_id')
    )
    op.create_index(op.f('ix_sdb_user_permissions_id'), 'sdb_user_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_user_permissions_permission_id'), 'sdb_user_permissions', ['permission_id'], unique=False)
    op.create_index(op.f('ix_sdb_user_permissions_user_id'), 'sdb_user_permissions', ['user_id'], unique=False)
    op.create_table('sdb_user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='ID пользователя'),
    sa.Column('role_id', sa.Integer(), nullable=False, comment='ID роли'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['sdb_roles.id'], name=op.f('fk_sdb_user_roles_role_id_sdb_roles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['sdb_users.id'], name=op.f('fk_sdb_user_roles_user_id_sdb_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sdb_user_roles')),
    sa.UniqueConstraint('user_id', 'role_id', name='uq_sdb_user_roles_user_id_role_id')
    )
    op.create_index(op.f('ix_sdb_user_roles_id'), 'sdb_user_roles', ['id'], unique=False)
    op.create_index(op.f('ix_sdb_user_roles_role_id'), 'sdb_user_roles', ['role_id'], unique=False)
    op.create_index(op.f('ix_sdb_user_roles_user_id'), 'sdb_user_roles', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sdb_user_roles_user_id'), table_name='sdb_user_roles')
    op.drop_index(op.f('ix_sdb_user_roles_role_id'), table_name='sdb_user_roles')
    op.drop_index(op.f('ix_sdb_user_roles_id'), table_name='sdb_user_roles')
    op.drop_table('sdb_user_roles')
    op.drop_index(op.f('ix_sdb_user_permissions_user_id'), table_name='sdb_user_permissions')
    op.drop_index(op.f('ix_sdb_user_permissions_permission_id'), table_name='sdb_user_permissions')
    op.drop_index(op.f('ix_sdb_user_permissions_id'), table_name='sdb_user_permissions')
    op.drop_table('sdb_user_permissions')
    op.drop_index(op.f('ix_sdb_role_permissions_role_id'), table_name='sdb_role_permissions')
    op.drop_index(op.f('ix_sdb_role_permissions_permission_id'), table_name='sdb_role_permissions')
    op.drop_index(op.f('ix_sdb_role_permissions_id'), table_name='sdb_role_permissions')
    op.drop_table('sdb_role_permissions')
    op.drop_index(op.f('ix_mod_another_example_table_id'), table_name='mod_another_example_table')
    op.drop_table('mod_another_example_table')
    op.drop_index(op.f('ix_sdb_users_username_lower'), table_name='sdb_users')
    op.drop_index(op.f('ix_sdb_users_username'), table_name='sdb_users')
    op.drop_index(op.f('ix_sdb_users_telegram_id'), table_name='sdb_users')
    op.drop_index(op.f('ix_sdb_users_id'), table_name='sdb_users')
    op.drop_table('sdb_users')
    op.drop_index(op.f('ix_sdb_roles_name'), table_name='sdb_roles')
    op.drop_index(op.f('ix_sdb_roles_id'), table_name='sdb_roles')
    op.drop_table('sdb_roles')
    op.drop_index(op.f('ix_sdb_permissions_name'), table_name='sdb_permissions')
    op.drop_index(op.f('ix_sdb_permissions_id'), table_name='sdb_permissions')
    op.drop_table('sdb_permissions')
    op.drop_index(op.f('ix_mod_example_user_notes_user_telegram_id'), table_name='mod_example_user_notes')
    op.drop_index(op.f('ix_mod_example_user_notes_id'), table_name='mod_example_user_notes')
    op.drop_table('mod_example_user_notes')
    op.drop_index(op.f('ix_mod_example_table_one_id'), table_name='mod_example_table_one')
    op.drop_table('mod_example_table_one')
    # ### end Alembic commands ###