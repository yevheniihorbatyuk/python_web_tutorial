"""add user role

Revision ID: 002_add_user_role
Revises: 001_initial_schema
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_add_user_role"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50), nullable=False, server_default="user")
    )


def downgrade() -> None:
    op.drop_column("users", "role")
