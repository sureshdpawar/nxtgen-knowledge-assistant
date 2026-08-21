"""add document ingestion jobs

Revision ID: b71d9e2a4f10
Revises: 543c2c59fa94
Create Date: 2026-08-21 09:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b71d9e2a4f10"
down_revision: Union[str, Sequence[str], None] = "543c2c59fa94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


job_status = sa.Enum(
    "PENDING",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name="documentingestionjobstatus",
)


def upgrade() -> None:
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "document_ingestion_job",
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            job_status,
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
            ["document_id"],
            ["document.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_document_ingestion_job_document_id",
        "document_ingestion_job",
        ["document_id"],
    )
    op.create_index(
        "ix_document_ingestion_job_status",
        "document_ingestion_job",
        ["status"],
    )
    op.create_index(
        "ix_document_ingestion_job_available_at",
        "document_ingestion_job",
        ["available_at"],
    )
    op.create_index(
        "ix_document_ingestion_job_queue",
        "document_ingestion_job",
        ["status", "available_at", "created_at"],
    )
    op.create_index(
        "uq_document_ingestion_job_active_document",
        "document_ingestion_job",
        ["document_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'PROCESSING')"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_document_ingestion_job_active_document",
        table_name="document_ingestion_job",
    )
    op.drop_index("ix_document_ingestion_job_queue", table_name="document_ingestion_job")
    op.drop_index(
        "ix_document_ingestion_job_available_at",
        table_name="document_ingestion_job",
    )
    op.drop_index("ix_document_ingestion_job_status", table_name="document_ingestion_job")
    op.drop_index(
        "ix_document_ingestion_job_document_id",
        table_name="document_ingestion_job",
    )
    op.drop_table("document_ingestion_job")
    job_status.drop(op.get_bind(), checkfirst=True)
