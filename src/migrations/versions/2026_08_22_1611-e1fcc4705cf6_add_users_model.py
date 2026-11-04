"""add users model

Revision ID: e1fcc4705cf6
Revises: 3fd7365cb8a1
Create Date: 2026-08-22 16:11:28.253661

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e1fcc4705cf6"
down_revision: str | Sequence[str] | None = "3fd7365cb8a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("hashed_password", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
