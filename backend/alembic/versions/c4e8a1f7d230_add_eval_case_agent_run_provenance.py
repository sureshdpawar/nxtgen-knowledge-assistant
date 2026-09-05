"""add eval case agent run provenance

Revision ID: c4e8a1f7d230
Revises: b7d9e4c2a611
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8a1f7d230"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "b7d9e4c2a611"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "eval_case",
        sa.Column(
            "source_agent_run_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "eval_case",
        sa.Column(
            "source_metadata",
            sa.JSON(),
            server_default=sa.text(
                "'{}'::json"
            ),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_eval_case_source_agent_run_id",
        "eval_case",
        "agent_run",
        ["source_agent_run_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_eval_case_source_agent_run_id",
        "eval_case",
        ["source_agent_run_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_eval_case_source_agent_run_id",
        table_name="eval_case",
    )

    op.drop_constraint(
        "fk_eval_case_source_agent_run_id",
        "eval_case",
        type_="foreignkey",
    )

    op.drop_column(
        "eval_case",
        "source_metadata",
    )

    op.drop_column(
        "eval_case",
        "source_agent_run_id",
    )
