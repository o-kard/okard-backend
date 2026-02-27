"""merge heads

Revision ID: 245a8575dda9
Revises: 29d560e369e4, b156789a0b12
Create Date: 2026-02-26 20:30:02.655950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '245a8575dda9'
down_revision: Union[str, Sequence[str], None] = ('29d560e369e4', 'b156789a0b12')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
