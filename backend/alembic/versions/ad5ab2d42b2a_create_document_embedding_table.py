"""create document_embedding table

Revision ID: ad5ab2d42b2a
Revises: c135352be5e1
Create Date: 2026-08-11 10:40:39.934096

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "ad5ab2d42b2a"
down_revision: Union[str, Sequence[str], None] = "c135352be5e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Enable PostgreSQL pgvector extension before creating
    # any columns that use the VECTOR type.
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )

    op.create_table(
        "document_embedding",
        sa.Column(
            "chunk_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "embedding_model",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "embedding",
            Vector(384),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
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
            ["chunk_id"],
            ["document_chunk.id"],
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        op.f(
            "ix_document_embedding_chunk_id"
        ),
        "document_embedding",
        ["chunk_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f(
            "ix_document_embedding_chunk_id"
        ),
        table_name="document_embedding",
    )

    op.drop_table(
        "document_embedding"
    )