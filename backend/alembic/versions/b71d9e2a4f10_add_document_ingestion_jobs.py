"""add document ingestion jobs

Revision ID: b71d9e2a4f10
Revises: 543c2c59fa94
Create Date: 2026-08-21 09:30:00

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b71d9e2a4f10"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "543c2c59fa94"

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


# ---------------------------------------------------------
# PostgreSQL enum
# ---------------------------------------------------------

job_status = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name=(
        "documentingestionjobstatus"
    ),
    create_type=False,
)


def upgrade() -> None:

    # -----------------------------------------------------
    # Create enum explicitly.
    #
    # create_type=False prevents SQLAlchemy from attempting
    # to create the enum again when the table is created.
    # -----------------------------------------------------

    job_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    # -----------------------------------------------------
    # Document ingestion job
    # -----------------------------------------------------

    op.create_table(
        "document_ingestion_job",

        sa.Column(
            "document_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                name=(
                    "documentingestionjobstatus"
                ),
                create_type=False,
            ),
            server_default=(
                "PENDING"
            ),
            nullable=False,
        ),

        sa.Column(
            "attempt_count",
            sa.Integer(),
            server_default=(
                "0"
            ),
            nullable=False,
        ),

        sa.Column(
            "max_attempts",
            sa.Integer(),
            server_default=(
                "3"
            ),
            nullable=False,
        ),

        sa.Column(
            "available_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=(
                sa.text(
                    "now()"
                )
            ),
            nullable=False,
        ),

        sa.Column(
            "claimed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "failed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "worker_id",
            sa.String(
                length=255
            ),
            nullable=True,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            server_default=(
                sa.text(
                    "gen_random_uuid()"
                )
            ),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=(
                sa.text(
                    "now()"
                )
            ),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=(
                sa.text(
                    "now()"
                )
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            [
                "document_id"
            ],
            [
                "document.id"
            ],
            ondelete=(
                "CASCADE"
            ),
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    op.create_index(
        (
            "ix_document_ingestion_job_"
            "document_id"
        ),
        "document_ingestion_job",
        [
            "document_id"
        ],
    )

    op.create_index(
        (
            "ix_document_ingestion_job_"
            "status"
        ),
        "document_ingestion_job",
        [
            "status"
        ],
    )

    op.create_index(
        (
            "ix_document_ingestion_job_"
            "available_at"
        ),
        "document_ingestion_job",
        [
            "available_at"
        ],
    )

    # -----------------------------------------------------
    # Worker queue index
    #
    # Optimizes:
    #
    # WHERE status = 'PENDING'
    # AND available_at <= now()
    # ORDER BY available_at, created_at
    # -----------------------------------------------------

    op.create_index(
        (
            "ix_document_ingestion_job_"
            "queue"
        ),
        "document_ingestion_job",
        [
            "status",
            "available_at",
            "created_at",
        ],
    )

    # -----------------------------------------------------
    # Only one active ingestion job per document.
    #
    # Completed/failed jobs remain as history while another
    # job may subsequently be queued for the same document.
    # -----------------------------------------------------

    op.create_index(
        (
            "uq_document_ingestion_job_"
            "active_document"
        ),
        "document_ingestion_job",
        [
            "document_id"
        ],
        unique=True,
        postgresql_where=(
            sa.text(
                "status IN "
                "('PENDING', 'PROCESSING')"
            )
        ),
    )


def downgrade() -> None:

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    op.drop_index(
        (
            "uq_document_ingestion_job_"
            "active_document"
        ),
        table_name=(
            "document_ingestion_job"
        ),
    )

    op.drop_index(
        (
            "ix_document_ingestion_job_"
            "queue"
        ),
        table_name=(
            "document_ingestion_job"
        ),
    )

    op.drop_index(
        (
            "ix_document_ingestion_job_"
            "available_at"
        ),
        table_name=(
            "document_ingestion_job"
        ),
    )

    op.drop_index(
        (
            "ix_document_ingestion_job_"
            "status"
        ),
        table_name=(
            "document_ingestion_job"
        ),
    )

    op.drop_index(
        (
            "ix_document_ingestion_job_"
            "document_id"
        ),
        table_name=(
            "document_ingestion_job"
        ),
    )

    # -----------------------------------------------------
    # Table
    # -----------------------------------------------------

    op.drop_table(
        "document_ingestion_job"
    )

    # -----------------------------------------------------
    # PostgreSQL enum
    # -----------------------------------------------------

    job_status.drop(
        op.get_bind(),
        checkfirst=True,
    )