"""change pk on user_campaign_view

Revision ID: 61f9be0df03b
Revises: 1118366a2464
Create Date: 2026-03-26 09:11:17.489881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61f9be0df03b'
down_revision: Union[str, Sequence[str], None] = '1118366a2464'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE user_campaign_view DROP CONSTRAINT IF EXISTS user_campaign_view_pkey')
    op.drop_column('user_campaign_view', 'id')
    op.create_primary_key(
        'user_campaign_view_pkey', 
        'user_campaign_view', 
        ['user_id', 'campaign_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('user_campaign_view_pkey', 'user_campaign_view', type_='primary')
    op.add_column('user_campaign_view', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.create_primary_key('user_campaign_view_pkey', 'user_campaign_view', ['id'])
