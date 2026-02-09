"""merge heads

Revision ID: 304dbe1fd5f7
Revises: 784b842f2dd7, fb35cda0ed2b
Create Date: 2026-01-28 23:29:07.547814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '304dbe1fd5f7'
down_revision: Union[str, Sequence[str], None] = ('784b842f2dd7', 'fb35cda0ed2b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
