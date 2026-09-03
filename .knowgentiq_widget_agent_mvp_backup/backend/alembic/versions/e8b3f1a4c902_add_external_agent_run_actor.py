"""add external actor identity to agent runs

Revision ID: e8b3f1a4c902
Revises: d7a6c8e91f42
Create Date: 2026-09-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e8b3f1a4c902"
down_revision: Union[str, Sequence[str], None] = "d7a6c8e91f42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "agent_run",
        "user_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    op.add_column(
        "agent_run",
        sa.Column("actor_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "agent_run",
        sa.Column("actor_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "agent_run",
        sa.Column("context_metadata", sa.JSON(), nullable=True),
    )

    op.execute(
        """
        UPDATE agent_run
        SET actor_type = 'USER',
            actor_id = user_id::text
        WHERE actor_type IS NULL
        """
    )

    op.alter_column(
        "agent_run",
        "actor_type",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default="USER",
    )
    op.alter_column(
        "agent_run",
        "actor_id",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.create_index(
        "ix_agent_run_actor_type",
        "agent_run",
        ["actor_type"],
        unique=False,
    )
    op.create_index(
        "ix_agent_run_actor_id",
        "agent_run",
        ["actor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_run_actor_id", table_name="agent_run")
    op.drop_index("ix_agent_run_actor_type", table_name="agent_run")
    op.drop_column("agent_run", "context_metadata")
    op.drop_column("agent_run", "actor_id")
    op.drop_column("agent_run", "actor_type")
    op.alter_column(
        "agent_run",
        "user_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
