"""merge heads

Revision ID: 29d560e369e4
Revises: 24177bdb8b7b, 3b796b60e733
Create Date: 2026-02-15 14:31:05.965516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29d560e369e4'
down_revision: Union[str, Sequence[str], None] = ('24177bdb8b7b', '3b796b60e733')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
