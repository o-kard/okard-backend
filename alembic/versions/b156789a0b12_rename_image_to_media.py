"""rename_image_to_media

Revision ID: b156789a0b12
Revises: a5f91d769e94
Create Date: 2026-02-18 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b156789a0b12'
down_revision: Union[str, Sequence[str], None] = 'ecd750c29342'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables
    op.rename_table('image', 'media')
    # Use 'imageHandler' - SQLAlchemy should handle quoting if needed for mixed case
    op.rename_table('imageHandler', 'media_handler')

    # Rename column image_id to media_id in media_handler (after table rename)
    op.alter_column('media_handler', 'image_id', new_column_name='media_id')
    
    # Postgres auto-updates FKs to point to the renamed table, 
    # but we might want to ensure the constraint names are clean in a perfect world.
    # However, guessing constraint names is risky. We rely on Postgres behavior.


def downgrade() -> None:
    op.alter_column('media_handler', 'media_id', new_column_name='image_id')
    op.rename_table('media_handler', 'imageHandler')
    op.rename_table('media', 'image')
