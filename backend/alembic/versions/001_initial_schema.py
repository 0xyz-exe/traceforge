"""Initial schema - workspaces, users, services

Revision ID: 001
Revises: 
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    op.create_index('idx_workspaces_slug', 'workspaces', ['slug'])
    
    # users
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    op.create_index('idx_users_workspace', 'users', ['workspace_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    
    # services
    op.create_table(
        'services',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('environment', sa.String(100), default='production'),
        sa.Column('version', sa.String(100)),
        sa.Column('last_telemetry_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    op.create_index('idx_services_workspace', 'services', ['workspace_id'])
    op.create_index('idx_services_last_telemetry', 'services', ['last_telemetry_at'])
    op.create_unique_constraint('uq_service_workspace_name_env', 'services', ['workspace_id', 'name', 'environment'])


def downgrade() -> None:
    op.drop_table('services')
    op.drop_table('users')
    op.drop_table('workspaces')
