"""add users model

Revision ID: e1fcc4705cf6
Revises: 3fd7365cb8a1
Create Date: 2026-08-22 16:11:28.253661

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e1fcc4705cf6"
down_revision: Union[str, Sequence[str], None] = "3fd7365cb8a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
