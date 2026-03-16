"""update_referencetype_enum_values

Revision ID: b4e66bb90981
Revises: ea55e0d1f267
Create Date: 2026-03-16 18:07:11.131244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4e66bb90981'
down_revision: Union[str, Sequence[str], None] = 'ea55e0d1f267'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Add 'information' to the native Enum 'referencetype'
    # PostgreSQL doesn't allow ALTER TYPE ... ADD VALUE in a transaction
    # Since Alembic runs in a transaction by default, we use this trick:
    op.execute("COMMIT")
    op.execute("ALTER TYPE referencetype ADD VALUE IF NOT EXISTS 'information'")
    
    # 1. First, rename existing 'campaign' references to 'information'
    op.execute("UPDATE media_handler SET type = 'information' WHERE type = 'campaign'")
    
    # 2. Then, rename existing 'post' references to 'campaign'
    op.execute("UPDATE media_handler SET type = 'campaign' WHERE type = 'post'")


def downgrade() -> None:
    # Reverse data renames
    op.execute("UPDATE media_handler SET type = 'post' WHERE type = 'campaign'")
    op.execute("UPDATE media_handler SET type = 'campaign' WHERE type = 'information'")
    # We generally don't remove values from enums in downgrades because it's hard in PG
