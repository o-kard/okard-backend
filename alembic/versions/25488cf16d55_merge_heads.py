"""merge heads

Revision ID: 25488cf16d55
Revises: fb35cda0ed2b
Create Date: 2026-01-28 23:59:48.760144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25488cf16d55'
down_revision: Union[str, Sequence[str], None] = 'fb35cda0ed2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
