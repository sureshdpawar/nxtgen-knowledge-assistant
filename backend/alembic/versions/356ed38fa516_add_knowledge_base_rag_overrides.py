"""add knowledge base rag overrides

Revision ID: 356ed38fa516
Revises: 1a2aa9d74942
Create Date: 2026-08-23 16:32:56.601216

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = (
    "356ed38fa516"
)

down_revision: Union[
    str,
    Sequence[str],
    None,
] = (
    "1a2aa9d74942"
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

    op.add_column(
        "knowledge_base",
        sa.Column(
            "chunk_size",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "knowledge_base",
        sa.Column(
            "chunk_overlap",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "knowledge_base",
        sa.Column(
            "top_k",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "knowledge_base",
        "top_k",
    )

    op.drop_column(
        "knowledge_base",
        "chunk_overlap",
    )

    op.drop_column(
        "knowledge_base",
        "chunk_size",
    )