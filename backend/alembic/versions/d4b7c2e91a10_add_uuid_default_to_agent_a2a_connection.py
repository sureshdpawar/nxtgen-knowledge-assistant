"""add uuid default to agent a2a connection

Revision ID: d4b7c2e91a10
Revises: c9a2a1f0b001
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4b7c2e91a10"
down_revision = "c9a2a1f0b001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "agent_a2a_connection",
        "id",
        server_default=sa.text("gen_random_uuid()"),
    )


def downgrade() -> None:
    op.alter_column(
        "agent_a2a_connection",
        "id",
        server_default=None,
    )
