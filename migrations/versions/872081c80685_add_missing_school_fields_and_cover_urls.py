"""add_missing_school_fields_and_cover_urls

Revision ID: 872081c80685
Revises: 17b323517e48
Create Date: 2026-04-22 09:43:55.151733

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "872081c80685"
down_revision: Union[str, Sequence[str], None] = "17b323517e48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
