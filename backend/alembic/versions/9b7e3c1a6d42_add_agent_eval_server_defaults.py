"""add agent eval server defaults

Revision ID: 9b7e3c1a6d42
Revises: f4a9c2d7e631
Create Date: 2026-09-10

The Agent Evaluation models inherit UUIDMixin and TimestampMixin, which
expect PostgreSQL to generate primary keys and timestamps. The original
Agent Evaluation migration created the columns as NOT NULL but omitted
those server defaults.

This additive migration brings the database schema into alignment with
the ORM models without recreating any tables or touching existing data.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b7e3c1a6d42"
down_revision: Union[str, Sequence[str], None] = "f4a9c2d7e631"
branch_labels = None
depends_on = None


_TABLES = (
    "agent_eval_dataset",
    "agent_eval_case",
    "agent_eval_experiment",
    "agent_eval_result",
)


def upgrade() -> None:
    for table_name in _TABLES:
        op.alter_column(
            table_name,
            "id",
            existing_type=sa.UUID(),
            existing_nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        )

        op.alter_column(
            table_name,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("now()"),
        )

        op.alter_column(
            table_name,
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("now()"),
        )


def downgrade() -> None:
    for table_name in reversed(_TABLES):
        op.alter_column(
            table_name,
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=None,
        )

        op.alter_column(
            table_name,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=None,
        )

        op.alter_column(
            table_name,
            "id",
            existing_type=sa.UUID(),
            existing_nullable=False,
            server_default=None,
        )
