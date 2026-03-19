"""add minio to storage provider

Revision ID: 38c04c49b0e5
Revises: 5fc35b065330
Create Date: 2026-03-19 22:04:23.490316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38c04c49b0e5'
down_revision: Union[str, Sequence[str], None] = '5fc35b065330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE storageprovider ADD VALUE 'minio'")


def downgrade() -> None:
    pass
