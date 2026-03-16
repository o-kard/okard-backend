"""rename_post_to_campaign_and_campaign_to_information

Revision ID: 7953ffddddc7
Revises: 28e0a0d32bf0
Create Date: 2026-03-16 18:05:08.918412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7953ffddddc7'
down_revision: Union[str, Sequence[str], None] = '28e0a0d32bf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename 'campaign' table to 'information'
    op.rename_table('campaign', 'information')
    
    # 2. Rename 'post' table to 'campaign'
    op.rename_table('post', 'campaign')

    # 3. Rename 'post_id' columns to 'campaign_id' in all referring tables
    # Note: 'information' table (formerly 'campaign') also has a 'post_id'
    tables_to_update = [
        'post_embedding', 'information', 'reward', 'comment', 
        'model', 'progress', 'contributor', 'bookmark', 
        'payment', 'user_post_view', 'report', 'edit_request',
        'notification'
    ]
    
    for table in tables_to_update:
        op.alter_column(table, 'post_id', new_column_name='campaign_id')

    # Update constraints if they have 'post' in their name (optional but good for consistency)
    # UniqueConstraint in contributor table
    op.execute("ALTER TABLE contributor RENAME CONSTRAINT uq_contributor_user_post TO uq_contributor_user_campaign")


def downgrade() -> None:
    # Reverse the unique constraint rename
    op.execute("ALTER TABLE contributor RENAME CONSTRAINT uq_contributor_user_campaign TO uq_contributor_user_post")

    # Reverse column renames
    tables_to_update = [
        'post_embedding', 'information', 'reward', 'comment', 
        'model', 'progress', 'contributor', 'bookmark', 
        'payment', 'user_post_view', 'report', 'edit_request',
        'notification'
    ]
    for table in tables_to_update:
        op.alter_column(table, 'campaign_id', new_column_name='post_id')

    # Reverse table renames
    op.rename_table('campaign', 'post')
    op.rename_table('information', 'campaign')
