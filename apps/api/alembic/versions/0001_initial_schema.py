"""Initial Schema Setup

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-06-28 22:54:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Enable PostgreSQL Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # 2. Create Custom ENUM Types
    sa.Enum("GUEST", "FREE_USER", "PRO_USER", "ADMIN", name="user_role").create(op.get_bind())
    sa.Enum("PENDING_ACTIVATION", "ACTIVE", "SUSPENDED", name="user_status").create(op.get_bind())
    sa.Enum("SUGGESTED", "SAVED", "DEPRECATED", "ARCHIVED", name="name_lifecycle").create(op.get_bind())
    sa.Enum("CLEAR", "WARNING", "CONFLICT", name="trademark_risk").create(op.get_bind())
    sa.Enum("FREE", "PRO", "ENTERPRISE", name="subscription_tier").create(op.get_bind())
    sa.Enum("ACTIVE", "PAST_DUE", "CANCELED", name="subscription_status").create(op.get_bind())
    sa.Enum("PENDING", "RUNNING", "SUCCESS", "FAILED", name="job_status").create(op.get_bind())

    # 3. Create Users & Workspaces (Primary Tables)
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum("GUEST", "FREE_USER", "PRO_USER", "ADMIN", name="user_role"), nullable=False),
        sa.Column('status', sa.Enum("PENDING_ACTIVATION", "ACTIVE", "SUSPENDED", name="user_status"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'workspaces',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create Secondary Relational Tables
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('tier', sa.Enum("FREE", "PRO", "ENTERPRISE", name="subscription_tier"), nullable=False),
        sa.Column('status', sa.Enum("ACTIVE", "PAST_DUE", "CANCELED", name="subscription_status"), nullable=False),
        sa.Column('limit_reset_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('monthly_query_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'workspace_members',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('prompt', sa.String(length=500), nullable=False),
        sa.Column('target_syllables', sa.Integer(), nullable=True),
        sa.Column('selected_tlds', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('actor', sa.String(length=255), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('entity_name', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'feature_flags',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Create Name Candidate & Verification Tables
    op.create_table(
        'generated_names',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('name_string', sa.String(length=18), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=False),
        sa.Column('lifecycle_state', sa.Enum("SUGGESTED", "SAVED", "DEPRECATED", "ARCHIVED", name="name_lifecycle"), nullable=False, server_default='SUGGESTED'),
        sa.Column('model_name', sa.String(length=50), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('generation_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'brand_scores',
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('bsi_overall', sa.Integer(), nullable=False),
        sa.Column('length_score', sa.Float(), nullable=False),
        sa.Column('pronounceability_score', sa.Float(), nullable=False),
        sa.Column('domain_score', sa.Float(), nullable=False),
        sa.Column('trademark_score', sa.Float(), nullable=False),
        sa.Column('semantic_score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('name_id')
    )

    op.create_table(
        'logo_suggestions',
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('primary_hue', sa.Integer(), nullable=False),
        sa.Column('secondary_hue', sa.Integer(), nullable=False),
        sa.Column('heading_font', sa.String(length=50), nullable=False),
        sa.Column('body_font', sa.String(length=50), nullable=False),
        sa.Column('layout_style', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('name_id')
    )

    op.create_table(
        'domain_checks',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('domain_name', sa.String(length=255), nullable=False),
        sa.Column('tld', sa.String(length=20), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'trademark_checks',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('jurisdiction', sa.String(length=10), nullable=False),
        sa.Column('risk_status', sa.Enum("CLEAR", "WARNING", "CONFLICT", name="trademark_risk"), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('mark_text', sa.String(length=255), nullable=False),
        sa.Column('filing_date', sa.DateTime(), nullable=True),
        sa.Column('registration_date', sa.DateTime(), nullable=True),
        sa.Column('class_code', sa.String(length=10), nullable=True),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'social_handle_checks',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'exports',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('package_url', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'generation_jobs',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum("PENDING", "RUNNING", "SUCCESS", "FAILED", name="job_status"), nullable=False, server_default='PENDING'),
        sa.Column('model_name', sa.String(length=50), nullable=False),
        sa.Column('engine_version', sa.String(length=50), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('token_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Generate Standard Indexes
    op.create_index('idx_sub_user_id', 'subscriptions', ['user_id'])
    op.create_index('idx_members_workspace_id', 'workspace_members', ['workspace_id'])
    op.create_index('idx_members_user_id', 'workspace_members', ['user_id'])
    op.create_index('idx_proj_workspace_id', 'projects', ['workspace_id'])
    op.create_index('idx_names_proj_id', 'generated_names', ['project_id'])
    op.create_index('idx_domain_name_id', 'domain_checks', ['name_id'])
    op.create_index('idx_tm_name_id', 'trademark_checks', ['name_id'])
    op.create_index('idx_social_name_id', 'social_handle_checks', ['name_id'])
    op.create_index('idx_export_user_id', 'exports', ['user_id'])
    op.create_index('idx_export_name_id', 'exports', ['name_id'])
    op.create_index('idx_audit_logs_workspace_id', 'audit_logs', ['workspace_id'])
    op.create_index('idx_gen_job_project_id', 'generation_jobs', ['project_id'])

    # 7. Generate Partial Unique Indexes
    op.execute('CREATE UNIQUE INDEX idx_user_email_active ON users(email) WHERE deleted_at IS NULL')
    op.execute('CREATE UNIQUE INDEX idx_workspace_slug_active ON workspaces(slug) WHERE deleted_at IS NULL')
    op.execute('CREATE UNIQUE INDEX idx_member_unique_active ON workspace_members(workspace_id, user_id) WHERE deleted_at IS NULL')

def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('generation_jobs')
    op.drop_table('exports')
    op.drop_table('social_handle_checks')
    op.drop_table('trademark_checks')
    op.drop_table('domain_checks')
    op.drop_table('logo_suggestions')
    op.drop_table('brand_scores')
    op.drop_table('generated_names')
    op.drop_table('feature_flags')
    op.drop_table('audit_logs')
    op.drop_table('projects')
    op.drop_table('workspace_members')
    op.drop_table('subscriptions')
    op.drop_table('workspaces')
    op.drop_table('users')

    # Drop custom ENUM types
    sa.Enum(name="user_role").drop(op.get_bind())
    sa.Enum(name="user_status").drop(op.get_bind())
    sa.Enum(name="name_lifecycle").drop(op.get_bind())
    sa.Enum(name="trademark_risk").drop(op.get_bind())
    sa.Enum(name="subscription_tier").drop(op.get_bind())
    sa.Enum(name="subscription_status").drop(op.get_bind())
    sa.Enum(name="job_status").drop(op.get_bind())
