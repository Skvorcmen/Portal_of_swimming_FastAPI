"""add_competition_subscriptions_table

Revision ID: c46b653bd3d7
Revises: 14a338ee9e6a
Create Date: 2026-04-22 12:51:53.715653

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c46b653bd3d7"
down_revision: Union[str, Sequence[str], None] = "14a338ee9e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
