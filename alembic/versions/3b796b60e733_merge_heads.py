"""merge heads

Revision ID: 3b796b60e733
Revises: 1151ec6e56b1, 4cfac35350f2, e0e74576ac35
Create Date: 2026-02-09 22:15:42.852176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b796b60e733'
down_revision: Union[str, Sequence[str], None] = ('1151ec6e56b1', '4cfac35350f2', 'e0e74576ac35')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
