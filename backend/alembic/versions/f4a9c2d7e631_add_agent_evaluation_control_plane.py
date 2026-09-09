"""add agent evaluation control plane

Revision ID: f4a9c2d7e631
Revises: d8f2c6a91b40
Create Date: 2026-09-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4a9c2d7e631"
down_revision: Union[str, Sequence[str], None] = "d8f2c6a91b40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_eval_dataset",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("agent_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_eval_dataset_agent_id",
        "agent_eval_dataset",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_dataset_tenant_id",
        "agent_eval_dataset",
        ["tenant_id"],
        unique=False,
    )

    op.create_table(
        "agent_eval_case",
        sa.Column("dataset_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("expected_outcome", sa.Text(), nullable=False),
        sa.Column("expected_tools", sa.JSON(), nullable=False),
        sa.Column("forbidden_tools", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("source_agent_run_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["agent_eval_dataset.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_agent_run_id"],
            ["agent_run.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_eval_case_dataset_id",
        "agent_eval_case",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_case_source_agent_run_id",
        "agent_eval_case",
        ["source_agent_run_id"],
        unique=False,
    )

    op.create_table(
        "agent_eval_experiment",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("dataset_id", sa.UUID(), nullable=False),
        sa.Column("agent_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("judge_model", sa.String(length=255), nullable=True),
        sa.Column("pass_rate_threshold", sa.Float(), nullable=False),
        sa.Column("case_count", sa.Integer(), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("pass_rate", sa.Float(), nullable=True),
        sa.Column("outcome_correctness", sa.Float(), nullable=True),
        sa.Column("tool_correctness", sa.Float(), nullable=True),
        sa.Column("argument_correctness", sa.Float(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["agent_eval_dataset.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_eval_experiment_agent_id",
        "agent_eval_experiment",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_experiment_dataset_id",
        "agent_eval_experiment",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_experiment_tenant_id",
        "agent_eval_experiment",
        ["tenant_id"],
        unique=False,
    )

    op.create_table(
        "agent_eval_result",
        sa.Column("experiment_id", sa.UUID(), nullable=False),
        sa.Column("eval_case_id", sa.UUID(), nullable=False),
        sa.Column("agent_run_id", sa.UUID(), nullable=True),
        sa.Column("actual_answer", sa.Text(), nullable=True),
        sa.Column("tools_called", sa.JSON(), nullable=False),
        sa.Column("outcome_correctness", sa.Float(), nullable=True),
        sa.Column("tool_correctness", sa.Float(), nullable=True),
        sa.Column("argument_correctness", sa.Float(), nullable=True),
        sa.Column("forbidden_tool_violations", sa.JSON(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("judge_metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_run_id"],
            ["agent_run.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["eval_case_id"],
            ["agent_eval_case.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["agent_eval_experiment.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_eval_result_agent_run_id",
        "agent_eval_result",
        ["agent_run_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_result_eval_case_id",
        "agent_eval_result",
        ["eval_case_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_eval_result_experiment_id",
        "agent_eval_result",
        ["experiment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_eval_result_experiment_id",
        table_name="agent_eval_result",
    )
    op.drop_index(
        "ix_agent_eval_result_eval_case_id",
        table_name="agent_eval_result",
    )
    op.drop_index(
        "ix_agent_eval_result_agent_run_id",
        table_name="agent_eval_result",
    )
    op.drop_table("agent_eval_result")

    op.drop_index(
        "ix_agent_eval_experiment_tenant_id",
        table_name="agent_eval_experiment",
    )
    op.drop_index(
        "ix_agent_eval_experiment_dataset_id",
        table_name="agent_eval_experiment",
    )
    op.drop_index(
        "ix_agent_eval_experiment_agent_id",
        table_name="agent_eval_experiment",
    )
    op.drop_table("agent_eval_experiment")

    op.drop_index(
        "ix_agent_eval_case_source_agent_run_id",
        table_name="agent_eval_case",
    )
    op.drop_index(
        "ix_agent_eval_case_dataset_id",
        table_name="agent_eval_case",
    )
    op.drop_table("agent_eval_case")

    op.drop_index(
        "ix_agent_eval_dataset_tenant_id",
        table_name="agent_eval_dataset",
    )
    op.drop_index(
        "ix_agent_eval_dataset_agent_id",
        table_name="agent_eval_dataset",
    )
    op.drop_table("agent_eval_dataset")
