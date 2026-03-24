"""Add deleted status to team request enum

Revision ID: 4b7f2e1a8d9c
Revises: 88020d66694c
Create Date: 2026-03-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4b7f2e1a8d9c"
down_revision: Union[str, None] = "88020d66694c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE teamrequeststatus ADD VALUE IF NOT EXISTS 'DELETED'")


def downgrade() -> None:
    pass
