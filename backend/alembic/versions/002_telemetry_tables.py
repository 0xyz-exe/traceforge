"""Add telemetry tables - logs, traces, spans

Revision ID: 002
Revises: 001
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # log_entries
    op.create_table(
        'log_entries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_id', UUID(as_uuid=True), sa.ForeignKey('services.id', ondelete='SET NULL')),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('trace_id', sa.String(32)),
        sa.Column('span_id', sa.String(16)),
        sa.Column('attributes', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_logs_workspace_time', 'log_entries', ['workspace_id', 'timestamp'])
    op.create_index('idx_logs_service', 'log_entries', ['service_id'])
    op.create_index('idx_logs_severity', 'log_entries', ['severity'])
    op.create_index('idx_logs_trace', 'log_entries', ['trace_id'])
    op.create_index('idx_logs_attributes_gin', 'log_entries', ['attributes'], postgresql_using='gin')
    
    # traces
    op.create_table(
        'traces',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trace_id', sa.String(32), nullable=False, unique=True),
        sa.Column('root_service_id', UUID(as_uuid=True), sa.ForeignKey('services.id', ondelete='SET NULL')),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('status', sa.String(20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_traces_workspace_time', 'traces', ['workspace_id', 'start_time'])
    op.create_index('idx_traces_trace_id', 'traces', ['trace_id'])
    
    # spans
    op.create_table(
        'spans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trace_id', sa.String(32), nullable=False),
        sa.Column('span_id', sa.String(16), nullable=False),
        sa.Column('parent_span_id', sa.String(16)),
        sa.Column('service_id', UUID(as_uuid=True), sa.ForeignKey('services.id', ondelete='SET NULL')),
        sa.Column('operation_name', sa.String(255), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('status', sa.String(20)),
        sa.Column('attributes', JSONB),
        sa.Column('events', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_unique_constraint('uq_span_trace_span', 'spans', ['trace_id', 'span_id'])
    op.create_index('idx_spans_trace', 'spans', ['trace_id'])
    op.create_index('idx_spans_parent', 'spans', ['parent_span_id'])
    op.create_index('idx_spans_workspace_time', 'spans', ['workspace_id', 'start_time'])
    op.create_index('idx_spans_service', 'spans', ['service_id'])


def downgrade() -> None:
    op.drop_table('spans')
    op.drop_table('traces')
    op.drop_table('log_entries')
