"""update users model fields

Revision ID: 5550e71007a1
Revises: e1fcc4705cf6
Create Date: 2026-08-22 19:08:52.796775

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5550e71007a1"
down_revision: str | Sequence[str] | None = "e1fcc4705cf6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=40), nullable=False))
    op.add_column("users", sa.Column("last_name", sa.String(length=40), nullable=False))
    op.create_unique_constraint(None, "users", ["hashed_password"])
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
