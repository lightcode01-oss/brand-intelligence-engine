"""Integration and Webhook tables

Revision ID: 0008_integration_tables
Revises: 0007_security_tables
Create Date: 2026-06-30 01:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0008_integration_tables'
down_revision: Union[str, None] = '0007_security_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Workspace Integrations
    op.create_table(
        'workspace_integrations',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('provider_slug', sa.String(50), nullable=False),
        sa.Column('settings_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Workspace Webhooks
    op.create_table(
        'workspace_webhooks',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('secret_key', sa.String(255), nullable=False),
        sa.Column('events_json', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_workspace_integrations_ws', 'workspace_integrations', ['workspace_id'])
    op.create_index('idx_workspace_webhooks_ws', 'workspace_webhooks', ['workspace_id'])

def downgrade() -> None:
    op.drop_index('idx_workspace_webhooks_ws', 'workspace_webhooks')
    op.drop_index('idx_workspace_integrations_ws', 'workspace_integrations')
    op.drop_table('workspace_webhooks')
    op.drop_table('workspace_integrations')
