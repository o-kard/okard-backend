"""rename_information_columns

Revision ID: 5fc35b065330
Revises: 1a554cd248a0
Create Date: 2026-03-18 22:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fc35b065330'
down_revision: Union[str, None] = '1a554cd248a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns in information table
    op.alter_column('information', 'campaign_header', new_column_name='information_header')
    op.alter_column('information', 'campaign_description', new_column_name='information_description')


def downgrade() -> None:
    # Revert column renames
    op.alter_column('information', 'information_header', new_column_name='campaign_header')
    op.alter_column('information', 'information_description', new_column_name='campaign_description')
