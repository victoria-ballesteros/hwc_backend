"""Add first business data

Revision ID: dc3acaf42c6b
Revises: 4918095df72e
Create Date: 2026-03-22 19:36:00.665075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc3acaf42c6b'
down_revision: Union[str, None] = '4918095df72e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role_table = sa.table(
        "role",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_super_user", sa.Boolean),
        sa.column("internal_code", sa.String),
    )

    roles_to_insert = [
        {
            "name": "Common User",
            "description": "Standard user with basic access",
            "is_super_user": False,
            "internal_code": "common_user",
        },
        {
            "name": "Administrator",
            "description": "Admin user with management capabilities",
            "is_super_user": False,
            "internal_code": "admin",
        },
        {
            "name": "Super Administrator",
            "description": "Unrestricted access to the entire system",
            "is_super_user": True,
            "internal_code": "superadmin",
        },
    ]

    conn = op.get_bind()

    for role in roles_to_insert:
        check_query = sa.text("SELECT 1 FROM role WHERE internal_code = :code")
        exists = conn.execute(check_query, {"code": role["internal_code"]}).fetchone()

        if not exists:
            op.bulk_insert(role_table, [role])


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM role WHERE internal_code IN ('common_user', 'admin', 'superadmin')"
        )
    )
