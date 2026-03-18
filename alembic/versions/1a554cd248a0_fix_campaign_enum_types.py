"""fix_campaign_enum_types

Revision ID: 1a554cd248a0
Revises: 0f610d72ba04
Create Date: 2026-03-18 22:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a554cd248a0'
down_revision: Union[str, None] = '0f610d72ba04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change campaign.state column from poststate to campaignstate
    op.execute(
        "ALTER TABLE campaign "
        "ALTER COLUMN state TYPE campaignstate "
        "USING state::text::campaignstate"
    )

    # Change campaign.category column from postcategory to campaigncategory
    op.execute(
        "ALTER TABLE campaign "
        "ALTER COLUMN category TYPE campaigncategory "
        "USING category::text::campaigncategory"
    )

    # Drop old unused enum types
    op.execute("DROP TYPE IF EXISTS poststate")
    op.execute("DROP TYPE IF EXISTS postcategory")
    op.execute("DROP TYPE IF EXISTS poststatus")


def downgrade() -> None:
    # Recreate old enum types
    op.execute("CREATE TYPE poststate AS ENUM ('draft', 'published', 'fail', 'success', 'suspend')")
    op.execute("CREATE TYPE postcategory AS ENUM ('art', 'comics', 'crafts', 'dance', 'design', 'fashion', 'filmVideo', 'food', 'games', 'journalism', 'music', 'photography', 'publishing', 'technology', 'theater', 'tech', 'education', 'health', 'other')")

    # Revert column types
    op.execute(
        "ALTER TABLE campaign "
        "ALTER COLUMN state TYPE poststate "
        "USING state::text::poststate"
    )
    op.execute(
        "ALTER TABLE campaign "
        "ALTER COLUMN category TYPE postcategory "
        "USING category::text::postcategory"
    )
