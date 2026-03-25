"""Add timestamps to tables

Revision ID: 88020d66694c
Revises:
Create Date: 2026-02-22 22:43:49.321126

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "88020d66694c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    inspector = inspect(conn)

    tables_to_update = [
        "category",
        "edition",
        "evaluation",
        "role",
        "sponsor",
        "team",
        "user",
    ]
    columns_to_add = ["created_at", "updated_at"]

    for table in tables_to_update:
        existing_columns = {c["name"] for c in inspector.get_columns(table)} # type: ignore

        for col_name in columns_to_add:
            if col_name not in existing_columns:
                op.add_column(
                    table,
                    sa.Column(
                        col_name,
                        sa.DateTime(),
                        nullable=False,
                        server_default=sa.func.now(),
                    ),
                )


def downgrade() -> None:
    connection = op.get_bind()
    inst = inspect(connection)

    tables_to_update = [
        "user",
        "team",
        "sponsor",
        "role",
        "evaluation",
        "edition",
        "category",
    ]
    columns_to_remove = ["updated_at", "created_at"]

    for table_name in tables_to_update:
        if table_name in inst.get_table_names(): # type: ignore
            existing_columns = [c["name"] for c in inst.get_columns(table_name)] # type: ignore
            for col_name in columns_to_remove:
                if col_name in existing_columns:
                    op.drop_column(table_name, col_name)
