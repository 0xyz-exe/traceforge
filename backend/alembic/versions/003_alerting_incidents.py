"""Add alerting and incident tables

Revision ID: 003
Revises: 002
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # alert_rules
    op.create_table(
        'alert_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('service', sa.String(255)),
        sa.Column('condition_type', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(255)),
        sa.Column('threshold', sa.Float),
        sa.Column('comparison', sa.String(10)),
        sa.Column('aggregation', sa.String(50)),
        sa.Column('window_seconds', sa.Integer, default=300),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('enabled', sa.Boolean, default=True),
        sa.Column('cooldown_seconds', sa.Integer, default=300),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )
    op.create_index('idx_alert_rules_workspace', 'alert_rules', ['workspace_id'])
    
    # alert_events
    op.create_table(
        'alert_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alert_rule_id', UUID(as_uuid=True), sa.ForeignKey('alert_rules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('state', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('details', JSONB),
        sa.Column('fired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_alert_events_workspace_time', 'alert_events', ['workspace_id', 'fired_at'])
    op.create_index('idx_alert_events_rule', 'alert_events', ['alert_rule_id'])
    op.create_index('idx_alert_events_state', 'alert_events', ['state'])
    
    # incidents
    op.create_table(
        'incidents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='open'),
        sa.Column('assigned_to', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )
    op.create_index('idx_incidents_workspace_time', 'incidents', ['workspace_id', 'started_at'])
    op.create_index('idx_incidents_status', 'incidents', ['status'])
    op.create_index('idx_incidents_severity', 'incidents', ['severity'])
    
    # incident_timeline
    op.create_table(
        'incident_timeline',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('idx_timeline_incident', 'incident_timeline', ['incident_id'])


def downgrade() -> None:
    op.drop_table('incident_timeline')
    op.drop_table('incidents')
    op.drop_table('alert_events')
    op.drop_table('alert_rules')
