"""rename post_header and post_description to campaign_header and campaign_description

Revision ID: 0f610d72ba04
Revises: b4e66bb90981
Create Date: 2026-03-16 21:19:49.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f610d72ba04'
down_revision: Union[str, None] = 'b4e66bb90981'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('campaign', 'post_header', new_column_name='campaign_header')
    op.alter_column('campaign', 'post_description', new_column_name='campaign_description')


def downgrade() -> None:
    op.alter_column('campaign', 'campaign_header', new_column_name='post_header')
    op.alter_column('campaign', 'campaign_description', new_column_name='post_description')
