"""Security tables: sessions, MFA, audit events, GDPR, SSO

Revision ID: 0007_security_tables
Revises: 0006_saved_reports_table
Create Date: 2026-06-29 20:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0007_security_tables'
down_revision: Union[str, None] = '0006_saved_reports_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. User Sessions (enhanced)
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('device_fingerprint', sa.String(255), nullable=True),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_user_sessions_token_hash', 'token_hash'),
    )

    # 2. MFA Devices
    op.create_table(
        'mfa_devices',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('method', sa.String(50), nullable=False, server_default='TOTP'),
        sa.Column('name', sa.String(100), nullable=False, server_default='Authenticator App'),
        sa.Column('secret_encrypted', sa.Text(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('backup_codes_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Recovery Codes
    op.create_table(
        'recovery_codes',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('mfa_device_id', sa.UUID(), nullable=False),
        sa.Column('code_hash', sa.String(255), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['mfa_device_id'], ['mfa_devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Security Events
    op.create_table(
        'security_events',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('actor', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('risk_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Security Policies
    op.create_table(
        'security_policies',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False, unique=True),
        sa.Column('mfa_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=False, server_default='480'),
        sa.Column('max_sessions_per_user', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('ip_allowlist', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('sso_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sso_provider', sa.String(50), nullable=True),
        sa.Column('password_min_length', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('password_require_special', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. SSO Providers
    op.create_table(
        'sso_providers',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('client_id', sa.String(255), nullable=False),
        sa.Column('client_secret_encrypted', sa.Text(), nullable=False),
        sa.Column('redirect_uri', sa.String(500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Data Export Requests
    op.create_table(
        'data_export_requests',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('download_url', sa.String(500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Data Deletion Requests
    op.create_table(
        'data_deletion_requests',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Consent Records
    op.create_table(
        'consent_records',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('consent_type', sa.String(100), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # Indexes
    op.create_index('idx_security_events_user_id', 'security_events', ['user_id'])
    op.create_index('idx_security_events_event_type', 'security_events', ['event_type'])
    op.create_index('idx_mfa_devices_user_id', 'mfa_devices', ['user_id'])
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])

def downgrade() -> None:
    op.drop_index('idx_user_sessions_user_id', 'user_sessions')
    op.drop_index('idx_mfa_devices_user_id', 'mfa_devices')
    op.drop_index('idx_security_events_event_type', 'security_events')
    op.drop_index('idx_security_events_user_id', 'security_events')
    op.drop_table('consent_records')
    op.drop_table('data_deletion_requests')
    op.drop_table('data_export_requests')
    op.drop_table('sso_providers')
    op.drop_table('security_policies')
    op.drop_table('security_events')
    op.drop_table('recovery_codes')
    op.drop_table('mfa_devices')
    op.drop_table('user_sessions')
