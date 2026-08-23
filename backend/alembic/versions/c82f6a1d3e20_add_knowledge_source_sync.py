"""add knowledge source sync

Revision ID: c82f6a1d3e20
Revises: b71d9e2a4f10
Create Date: 2026-08-21

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import (
    postgresql,
)


revision: str = (
    "c82f6a1d3e20"
)

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "b71d9e2a4f10"

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


sync_status = postgresql.ENUM(
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "COMPLETED_WITH_ERRORS",
    "FAILED",
    name=(
        "knowledgesourcesyncstatus"
    ),
    create_type=False,
)


def upgrade() -> None:

    sync_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "knowledge_source_sync",

        sa.Column(
            "knowledge_source_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "triggered_by",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sync_status,
            server_default="PENDING",
            nullable=False,
        ),

        sa.Column(
            "started_at",
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
            "items_discovered",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "items_new",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "items_changed",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "items_unchanged",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "items_missing",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "items_failed",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "provider_summary",
            sa.String(
                length=1000
            ),
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
                sa.text("now()")
            ),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=(
                sa.text("now()")
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            [
                "knowledge_source_id"
            ],
            [
                "knowledge_source.id"
            ],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["triggered_by"],
            ["app_user.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_knowledge_source_sync_source",
        "knowledge_source_sync",
        [
            "knowledge_source_id"
        ],
    )

    op.create_index(
        "ix_knowledge_source_sync_triggered_by",
        "knowledge_source_sync",
        [
            "triggered_by"
        ],
    )

    op.create_index(
        "ix_knowledge_source_sync_status",
        "knowledge_source_sync",
        ["status"],
    )

    op.create_index(
        "ix_knowledge_source_sync_history",
        "knowledge_source_sync",
        [
            "knowledge_source_id",
            "created_at",
        ],
    )

    op.create_index(
        "uq_knowledge_source_sync_active_source",
        "knowledge_source_sync",
        [
            "knowledge_source_id"
        ],
        unique=True,
        postgresql_where=(
            sa.text(
                "status IN "
                "('PENDING', 'RUNNING')"
            )
        ),
    )


def downgrade() -> None:

    op.drop_index(
        "uq_knowledge_source_sync_active_source",
        table_name=(
            "knowledge_source_sync"
        ),
    )

    op.drop_index(
        "ix_knowledge_source_sync_history",
        table_name=(
            "knowledge_source_sync"
        ),
    )

    op.drop_index(
        "ix_knowledge_source_sync_status",
        table_name=(
            "knowledge_source_sync"
        ),
    )

    op.drop_index(
        "ix_knowledge_source_sync_triggered_by",
        table_name=(
            "knowledge_source_sync"
        ),
    )

    op.drop_index(
        "ix_knowledge_source_sync_source",
        table_name=(
            "knowledge_source_sync"
        ),
    )

    op.drop_table(
        "knowledge_source_sync"
    )

    sync_status.drop(
        op.get_bind(),
        checkfirst=True,
    )