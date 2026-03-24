"""seed_country_data

Revision ID: 1118366a2464
Revises: 057acac65000
Create Date: 2026-03-25 00:04:49.828818

"""
import csv
import os
import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column


# revision identifiers, used by Alembic.
revision: str = '1118366a2464'
down_revision: Union[str, Sequence[str], None] = '057acac65000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

country_table = table(
    'country',
    column('id', sa.UUID),
    column('name', sa.String),
    column('en_name', sa.String),
    column('alpha2', sa.String),
    column('alpha3', sa.String),
    column('numeric', sa.String),
    column('iso3166_2', sa.String),
    column('enabled', sa.Boolean),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime)
)
def upgrade() -> None:
    """Upgrade schema."""
    csv_file_path = os.path.join(os.path.dirname(__file__), "../country.csv")
    
    data_to_insert = []
    now = datetime.now(timezone.utc)
    
    with open(csv_file_path, newline='', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            numeric_code = str(row['numeric']).strip().zfill(3)
            
            data_to_insert.append({
                "id": uuid.uuid4(),
                "name": row["name"].strip(),
                "en_name": row["en_name"].strip(),
                "alpha2": row["alpha2"].strip(),
                "alpha3": row["alpha3"].strip(),
                "numeric": numeric_code,
                "iso3166_2": row["iso3166_2"].strip() if row.get("iso3166_2") else None,
                "enabled": True,
                "created_at": now,
                "updated_at": now
            })
            
    if data_to_insert:
        op.bulk_insert(country_table, data_to_insert)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("TRUNCATE TABLE country CASCADE;")
