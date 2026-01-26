"""merge heads

Revision ID: fb35cda0ed2b
Revises: b31af9ce7cf1, b3645574259e, e0ea7daa3ca7
Create Date: 2026-01-26 21:59:06.776790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb35cda0ed2b'
down_revision: Union[str, Sequence[str], None] = ('b31af9ce7cf1', 'b3645574259e', 'e0ea7daa3ca7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
