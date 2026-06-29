"""Collaboration and real-time workspaces tables setup

Revision ID: 0005_collaboration_tables
Revises: 0003_saas_billing_and_api_keys
Create Date: 2026-06-29 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0005_collaboration_tables'
down_revision: Union[str, None] = '0003_saas_billing_and_api_keys'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create Comment Threads Table
    op.create_table(
        'comment_threads',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_by', sa.UUID(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create Comments Table
    op.create_table(
        'comments',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('thread_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['thread_id'], ['comment_threads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create Favorites Table
    op.create_table(
        'favorites',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create Collections Table
    op.create_table(
        'collections',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Create Collection Items Table
    op.create_table(
        'collection_items',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('collection_id', sa.UUID(), nullable=False),
        sa.Column('name_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version_id', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['name_id'], ['generated_names.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Create Activity Events Table
    op.create_table(
        'activity_events',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Create Mentions Table
    op.create_table(
        'mentions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('comment_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Create Search Histories Table
    op.create_table(
        'search_histories',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('query', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Modify notifications table (add category, data_json, sender_id columns)
    op.add_column('notifications', sa.Column('category', sa.String(length=50), nullable=True, server_default='project_update'))
    op.add_column('notifications', sa.Column('data_json', sa.JSON(), nullable=True, server_default='{}'))
    op.add_column('notifications', sa.Column('sender_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_notifications_sender_id', 'notifications', 'users', ['sender_id'], ['id'], ondelete='SET NULL')

    # 10. Modify audit_logs table (add project_id, request_id columns)
    op.add_column('audit_logs', sa.Column('project_id', sa.UUID(), nullable=True))
    op.add_column('audit_logs', sa.Column('request_id', sa.String(length=100), nullable=True))
    op.create_foreign_key('fk_audit_logs_project_id', 'audit_logs', 'projects', ['project_id'], ['id'], ondelete='SET NULL')

    # 11. Create Indexes
    op.create_index('idx_comment_threads_workspace_id', 'comment_threads', ['workspace_id'])
    op.create_index('idx_comments_thread_id', 'comments', ['thread_id'])
    op.create_index('idx_favorites_workspace_id', 'favorites', ['workspace_id'])
    op.create_index('idx_collections_workspace_id', 'collections', ['workspace_id'])
    op.create_index('idx_activity_events_workspace_id', 'activity_events', ['workspace_id'])

def downgrade() -> None:
    # Drop Indexes
    op.drop_index('idx_activity_events_workspace_id', 'activity_events')
    op.drop_index('idx_collections_workspace_id', 'collections')
    op.drop_index('idx_favorites_workspace_id', 'favorites')
    op.drop_index('idx_comments_thread_id', 'comments')
    op.drop_index('idx_comment_threads_workspace_id', 'comment_threads')

    # Revert notifications extensions
    op.drop_constraint('fk_notifications_sender_id', 'notifications', type_='foreignkey')
    op.drop_column('notifications', 'sender_id')
    op.drop_column('notifications', 'data_json')
    op.drop_column('notifications', 'category')

    # Revert audit_logs extensions
    op.drop_constraint('fk_audit_logs_project_id', 'audit_logs', type_='foreignkey')
    op.drop_column('audit_logs', 'request_id')
    op.drop_column('audit_logs', 'project_id')

    # Drop Tables
    op.drop_table('search_histories')
    op.drop_table('mentions')
    op.drop_table('activity_events')
    op.drop_table('collection_items')
    op.drop_table('collections')
    op.drop_table('favorites')
    op.drop_table('comments')
    op.drop_table('comment_threads')
