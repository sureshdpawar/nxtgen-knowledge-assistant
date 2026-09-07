"""add agent context to conversations

Revision ID: d8f2c6a91b40
Revises: c4e8a1f7d230
Create Date: 2026-09-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8f2c6a91b40"
down_revision: Union[str, Sequence[str], None] = "c4e8a1f7d230"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "conversation",
        "knowledge_base_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    op.add_column(
        "conversation",
        sa.Column(
            "agent_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "conversation",
        sa.Column(
            "agent_thread_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_conversation_agent_id",
        "conversation",
        "agent",
        ["agent_id"],
        ["id"],
    )

    op.create_index(
        "ix_conversation_agent_id",
        "conversation",
        ["agent_id"],
        unique=False,
    )

    op.create_index(
        "ix_conversation_agent_thread_id",
        "conversation",
        ["agent_thread_id"],
        unique=False,
    )

    op.create_check_constraint(
        "ck_conversation_has_context",
        "conversation",
        "knowledge_base_id IS NOT NULL OR agent_id IS NOT NULL",
    )

    op.create_check_constraint(
        "ck_conversation_agent_thread_requires_agent",
        "conversation",
        "agent_thread_id IS NULL OR agent_id IS NOT NULL",
    )

    op.create_check_constraint(
        "ck_conversation_channel_uses_knowledge_base",
        "conversation",
        """
        chat_channel_id IS NULL
        OR (
            agent_id IS NULL
            AND agent_thread_id IS NULL
            AND knowledge_base_id IS NOT NULL
        )
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_conversation_channel_uses_knowledge_base",
        "conversation",
        type_="check",
    )
    op.drop_constraint(
        "ck_conversation_agent_thread_requires_agent",
        "conversation",
        type_="check",
    )
    op.drop_constraint(
        "ck_conversation_has_context",
        "conversation",
        type_="check",
    )
    op.drop_index(
        "ix_conversation_agent_thread_id",
        table_name="conversation",
    )
    op.drop_index(
        "ix_conversation_agent_id",
        table_name="conversation",
    )
    op.drop_constraint(
        "fk_conversation_agent_id",
        "conversation",
        type_="foreignkey",
    )
    op.drop_column(
        "conversation",
        "agent_thread_id",
    )
    op.drop_column(
        "conversation",
        "agent_id",
    )
    op.alter_column(
        "conversation",
        "knowledge_base_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
