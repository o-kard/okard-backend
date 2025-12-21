"""fix enum category

Revision ID: 46983538594f
Revises: 81851fd0c910
Create Date: 2026-01-13 22:50:04.975126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '46983538594f'
down_revision: Union[str, Sequence[str], None] = '81851fd0c910'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'art'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'comics'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'crafts'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'dance'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'design'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'fashion'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'filmVideo'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'food'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'games'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'journalism'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'music'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'photography'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'publishing'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'technology'")
    op.execute("ALTER TYPE postcategory ADD VALUE IF NOT EXISTS 'theater'")

def downgrade():
    # PostgreSQL enum cannot remove values
    pass
