"""support channel conversations

Revision ID: 6d48afd9e861
Revises: c7d39e32c6b5
Create Date: 2026-08-21 15:24:28.840810

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d48afd9e861"
down_revision: Union[str, Sequence[str], None] = "c7d39e32c6b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversation",
        sa.Column(
            "chat_channel_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.alter_column(
        "conversation",
        "user_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    op.create_index(
        "ix_conversation_chat_channel_id",
        "conversation",
        ["chat_channel_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_conversation_chat_channel_id",
        "conversation",
        "chat_channel",
        ["chat_channel_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_check_constraint(
        "ck_conversation_single_actor",
        "conversation",
        """
        (
            user_id IS NOT NULL
            AND chat_channel_id IS NULL
        )
        OR
        (
            user_id IS NULL
            AND chat_channel_id IS NOT NULL
        )
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_conversation_single_actor",
        "conversation",
        type_="check",
    )

    op.drop_constraint(
        "fk_conversation_chat_channel_id",
        "conversation",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_conversation_chat_channel_id",
        table_name="conversation",
    )

    op.alter_column(
        "conversation",
        "user_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    op.drop_column(
        "conversation",
        "chat_channel_id",
    )