"""add_thumbnail_path_to_image

Revision ID: ecd750c29342
Revises: 524a55ee7744
Create Date: 2026-02-17 08:42:40.845868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecd750c29342'
down_revision: Union[str, Sequence[str], None] = '524a55ee7744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('image', sa.Column('thumbnail_path', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('image', 'thumbnail_path')
