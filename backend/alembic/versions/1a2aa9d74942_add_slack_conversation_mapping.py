"""add slack conversation mapping

Revision ID: 1a2aa9d74942
Revises: 5676e9639baa
Create Date: 2026-08-22 15:19:26.900263
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = (
    "1a2aa9d74942"
)

down_revision: Union[
    str,
    Sequence[str],
    None,
] = (
    "5676e9639baa"
)

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    op.create_table(
        "chat_channel_slack_conversation",

        sa.Column(
            "channel_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "conversation_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "slack_team_id",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "slack_channel_id",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "slack_thread_ts",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "slack_user_id",
            sa.String(
                length=64
            ),
            nullable=True,
        ),

        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text(
                "gen_random_uuid()"
            ),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            [
                "channel_id"
            ],
            [
                "chat_channel.id"
            ],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            [
                "conversation_id"
            ],
            [
                "conversation.id"
            ],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "conversation_id"
        ),

        sa.UniqueConstraint(
            "channel_id",
            "slack_team_id",
            "slack_channel_id",
            "slack_thread_ts",
            name=(
                "uq_slack_conversation_thread"
            ),
        ),
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_channel_id"
        ),
        "chat_channel_slack_conversation",
        [
            "channel_id"
        ],
        unique=False,
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_conversation_id"
        ),
        "chat_channel_slack_conversation",
        [
            "conversation_id"
        ],
        unique=True,
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_team_id"
        ),
        "chat_channel_slack_conversation",
        [
            "slack_team_id"
        ],
        unique=False,
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_channel_id"
        ),
        "chat_channel_slack_conversation",
        [
            "slack_channel_id"
        ],
        unique=False,
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_thread_ts"
        ),
        "chat_channel_slack_conversation",
        [
            "slack_thread_ts"
        ],
        unique=False,
    )


    op.create_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_user_id"
        ),
        "chat_channel_slack_conversation",
        [
            "slack_user_id"
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_user_id"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_thread_ts"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_channel_id"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_slack_team_id"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_conversation_id"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_index(
        op.f(
            "ix_chat_channel_slack_conversation_channel_id"
        ),
        table_name=(
            "chat_channel_slack_conversation"
        ),
    )

    op.drop_table(
        "chat_channel_slack_conversation"
    )