"""add knowledge base reranking override

Revision ID: b9a4c2d1e7f0
Revises: 3fce752f89d1
Create Date: 2026-09-02

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = (
    "b9a4c2d1e7f0"
)

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "3fce752f89d1"

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
            "reranking_enabled",
            sa.Boolean(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "knowledge_base",
        "reranking_enabled",
    )
