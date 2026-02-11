"""merge head

Revision ID: 12cb81e09666
Revises: d4193a519629
Create Date: 2026-02-09 22:56:44.791518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12cb81e09666'
down_revision: Union[str, Sequence[str], None] = 'd4193a519629'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
