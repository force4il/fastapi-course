"""update users model fields

Revision ID: b80f2a39ddc9
Revises: 5550e71007a1
Create Date: 2026-08-22 19:28:00.022676

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b80f2a39ddc9"
down_revision: Union[str, Sequence[str], None] = "5550e71007a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(op.f("users_hashed_password_key"), "users", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        op.f("users_hashed_password_key"),
        "users",
        ["hashed_password"],
        postgresql_nulls_not_distinct=False,
    )
