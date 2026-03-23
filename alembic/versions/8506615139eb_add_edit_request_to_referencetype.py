"""add edit_request to referencetype

Revision ID: 8506615139eb
Revises: 2065c6e6953b
Create Date: 2026-03-24 02:57:15.643108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8506615139eb'
down_revision: Union[str, Sequence[str], None] = '2065c6e6953b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("COMMIT")
    op.execute("ALTER TYPE referencetype ADD VALUE IF NOT EXISTS 'edit_request'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
