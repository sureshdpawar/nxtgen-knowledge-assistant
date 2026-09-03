"""add LangGraph agent checkpoint correlation and approval status

Revision ID: d7a6c8e91f42
Revises: b9a4c2d1e7f0
Create Date: 2026-09-03

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = "d7a6c8e91f42"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "b9a4c2d1e7f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Framework-owned LangGraph checkpoint tables are NOT
    # created here. AsyncPostgresSaver.setup() owns them.

    # PostgreSQL enum values must be committed before they can
    # be used by later statements/transactions.
    op.execute(
        "ALTER TYPE agentrunstatus "
        "ADD VALUE IF NOT EXISTS "
        "'WAITING_FOR_APPROVAL'"
    )

    op.add_column(
        "agent_run",
        sa.Column(
            "thread_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "agent_run",
        sa.Column(
            "checkpoint_id",
            sa.String(
                length=255,
            ),
            nullable=True,
        ),
    )

    op.create_index(
        op.f(
            "ix_agent_run_thread_id"
        ),
        "agent_run",
        [
            "thread_id",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_agent_run_thread_id"
        ),
        table_name=
            "agent_run",
    )

    op.drop_column(
        "agent_run",
        "checkpoint_id",
    )

    op.drop_column(
        "agent_run",
        "thread_id",
    )

    # PostgreSQL does not support a safe/simple DROP VALUE for
    # enums. Leaving the unused enum value is preferable to
    # rebuilding the enum type during downgrade.
