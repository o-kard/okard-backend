"""rename_remaining_post_tables

Revision ID: ea55e0d1f267
Revises: 7953ffddddc7
Create Date: 2026-03-16 18:06:19.897437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea55e0d1f267'
down_revision: Union[str, Sequence[str], None] = '7953ffddddc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('post_embedding', 'campaign_embedding')
    op.rename_table('user_post_view', 'user_campaign_view')


def downgrade() -> None:
    op.rename_table('user_campaign_view', 'user_post_view')
    op.rename_table('campaign_embedding', 'post_embedding')
