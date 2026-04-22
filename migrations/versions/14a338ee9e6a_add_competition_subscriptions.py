"""add_competition_subscriptions

Revision ID: 14a338ee9e6a
Revises: 872081c80685
Create Date: 2026-04-22 12:41:58.820976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "14a338ee9e6a"
down_revision: Union[str, Sequence[str], None] = "872081c80685"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
