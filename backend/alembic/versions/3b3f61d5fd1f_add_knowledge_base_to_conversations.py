"""add knowledge base to conversations

Revision ID: 3b3f61d5fd1f
Revises: 9aaa41060ed2
Create Date: 2026-08-13 16:12:22.641613
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers

revision: str = "3b3f61d5fd1f"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "9aaa41060ed2"

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

    #
    # Existing conversations were created
    # before knowledge_base_id was stored.
    #
    # We cannot reliably determine which KB
    # those historical conversations belonged to.
    #
    # Remove development conversation history
    # before adding the required column.
    #

    op.execute(
        "DELETE FROM conversation_message"
    )

    op.execute(
        "DELETE FROM conversation"
    )

    #
    # Add knowledge_base_id
    #

    op.add_column(
        "conversation",
        sa.Column(
            "knowledge_base_id",
            sa.UUID(),
            nullable=False,
        ),
    )

    #
    # Add index
    #

    op.create_index(
        op.f(
            "ix_conversation_knowledge_base_id"
        ),
        "conversation",
        [
            "knowledge_base_id",
        ],
        unique=False,
    )

    #
    # Add FK
    #

    op.create_foreign_key(
        "fk_conversation_knowledge_base_id",
        "conversation",
        "knowledge_base",
        [
            "knowledge_base_id",
        ],
        [
            "id",
        ],
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_conversation_knowledge_base_id",
        "conversation",
        type_="foreignkey",
    )

    op.drop_index(
        op.f(
            "ix_conversation_knowledge_base_id"
        ),
        table_name="conversation",
    )

    op.drop_column(
        "conversation",
        "knowledge_base_id",
    )