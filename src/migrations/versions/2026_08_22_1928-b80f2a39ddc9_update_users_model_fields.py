"""update users model fields

Revision ID: b80f2a39ddc9
Revises: 5550e71007a1
Create Date: 2026-08-22 19:28:00.022676

"""

from collections.abc import Sequence

from alembic import op

revision: str = "b80f2a39ddc9"
down_revision: str | Sequence[str] | None = "5550e71007a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("users_hashed_password_key"), "users", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        op.f("users_hashed_password_key"),
        "users",
        ["hashed_password"],
        postgresql_nulls_not_distinct=False,
    )
