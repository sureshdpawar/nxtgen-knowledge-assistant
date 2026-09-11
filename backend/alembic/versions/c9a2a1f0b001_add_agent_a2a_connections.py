"""add agent a2a connections

Revision ID: c9a2a1f0b001
Revises: a7d4c8e2f901
Create Date: 2026-09-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9a2a1f0b001"
down_revision: Union[str, Sequence[str], None] = "a7d4c8e2f901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_a2a_connection",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("source_agent_id", sa.UUID(), nullable=False),
        sa.Column("target_agent_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["app_user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_agent_id",
            "target_agent_id",
            name="uq_agent_a2a_connection_source_target",
        ),
    )
    op.create_index(
        op.f("ix_agent_a2a_connection_tenant_id"),
        "agent_a2a_connection",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_a2a_connection_source_agent_id"),
        "agent_a2a_connection",
        ["source_agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_a2a_connection_target_agent_id"),
        "agent_a2a_connection",
        ["target_agent_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_agent_a2a_connection_target_agent_id"),
        table_name="agent_a2a_connection",
    )
    op.drop_index(
        op.f("ix_agent_a2a_connection_source_agent_id"),
        table_name="agent_a2a_connection",
    )
    op.drop_index(
        op.f("ix_agent_a2a_connection_tenant_id"),
        table_name="agent_a2a_connection",
    )
    op.drop_table("agent_a2a_connection")
