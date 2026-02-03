"""merge_heads

Revision ID: 524a55ee7744
Revises: 1151ec6e56b1, 4cfac35350f2
Create Date: 2026-02-17 08:42:19.746038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '524a55ee7744'
down_revision: Union[str, Sequence[str], None] = ('1151ec6e56b1', '4cfac35350f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
