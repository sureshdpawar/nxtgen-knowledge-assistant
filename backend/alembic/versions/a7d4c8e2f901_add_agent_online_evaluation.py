"""add agent online evaluation

Revision ID: a7d4c8e2f901
Revises: 9b7e3c1a6d42
Create Date: 2026-09-10
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = "a7d4c8e2f901"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "9b7e3c1a6d42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_online_eval_result",
        sa.Column(
            "tenant_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "agent_run_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "sample_reason",
            sa.String(length=100),
            server_default="manual",
            nullable=False,
        ),
        sa.Column(
            "question",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "actual_answer",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "tools_used",
            sa.JSON(),
            server_default=sa.text(
                "'[]'::json"
            ),
            nullable=False,
        ),
        sa.Column(
            "task_quality_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "execution_health_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "overall_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "passed",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "metrics",
            sa.JSON(),
            server_default=sa.text(
                "'{}'::json"
            ),
            nullable=False,
        ),
        sa.Column(
            "evaluation_metadata",
            sa.JSON(),
            server_default=sa.text(
                "'{}'::json"
            ),
            nullable=False,
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
            sa.DateTime(timezone=True),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agent_run_id"],
            ["agent_run.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "agent_run_id",
            name=(
                "uq_agent_online_eval_result_"
                "agent_run_id"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "tenant_id"
        ),
        "agent_online_eval_result",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "agent_id"
        ),
        "agent_online_eval_result",
        ["agent_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "agent_run_id"
        ),
        "agent_online_eval_result",
        ["agent_run_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "status"
        ),
        "agent_online_eval_result",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "sample_reason"
        ),
        "agent_online_eval_result",
        ["sample_reason"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_agent_online_eval_result_"
            "passed"
        ),
        "agent_online_eval_result",
        ["passed"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "passed"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "sample_reason"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "status"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "agent_run_id"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "agent_id"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_index(
        op.f(
            "ix_agent_online_eval_result_"
            "tenant_id"
        ),
        table_name="agent_online_eval_result",
    )

    op.drop_table(
        "agent_online_eval_result"
    )
