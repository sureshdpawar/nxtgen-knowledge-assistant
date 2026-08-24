"""add eval v1 tables

Revision ID: 05475f6036de
Revises: 356ed38fa516
Create Date: 2026-08-23 19:45:53.061357

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05475f6036de"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "356ed38fa516"
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
    """
    Create Eval v1 tables.

    This migration intentionally contains
    only evaluation-related schema changes.
    """

    op.create_table(
        "eval_dataset",
        sa.Column(
            "knowledge_base_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
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
            ["knowledge_base_id"],
            ["knowledge_base.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        op.f(
            "ix_eval_dataset_knowledge_base_id"
        ),
        "eval_dataset",
        ["knowledge_base_id"],
        unique=False,
    )

    op.create_table(
        "eval_experiment",
        sa.Column(
            "dataset_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "knowledge_base_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "eval_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "top_k",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "chunk_size",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "chunk_overlap",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "embedding_model",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "llm_model",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "hit_rate",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "mrr",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "metrics",
            sa.JSON(),
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
            ["dataset_id"],
            ["eval_dataset.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"],
            ["knowledge_base.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        op.f(
            "ix_eval_experiment_dataset_id"
        ),
        "eval_experiment",
        ["dataset_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_eval_experiment_knowledge_base_id"
        ),
        "eval_experiment",
        ["knowledge_base_id"],
        unique=False,
    )

    op.create_table(
        "eval_case",
        sa.Column(
            "dataset_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "question",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "expected_document_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "expected_chunk_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "expected_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "expected_answer",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "answerable",
            sa.Boolean(),
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
            ["dataset_id"],
            ["eval_dataset.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["expected_chunk_id"],
            ["document_chunk.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["expected_document_id"],
            ["document.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        op.f(
            "ix_eval_case_dataset_id"
        ),
        "eval_case",
        ["dataset_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_eval_case_expected_chunk_id"
        ),
        "eval_case",
        ["expected_chunk_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_eval_case_expected_document_id"
        ),
        "eval_case",
        ["expected_document_id"],
        unique=False,
    )

    op.create_table(
        "eval_result",
        sa.Column(
            "experiment_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "eval_case_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "retrieved_document_ids",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "retrieved_chunk_ids",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "retrieved_distances",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "retrieval_context",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "expected_rank",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "hit_at_k",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "reciprocal_rank",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "actual_answer",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "correctness_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "faithfulness_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "relevancy_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "refusal_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "passed",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "metrics",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "judge_metadata",
            sa.JSON(),
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
            ["eval_case_id"],
            ["eval_case.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["eval_experiment.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        op.f(
            "ix_eval_result_eval_case_id"
        ),
        "eval_result",
        ["eval_case_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_eval_result_experiment_id"
        ),
        "eval_result",
        ["experiment_id"],
        unique=False,
    )


def downgrade() -> None:
    """
    Remove Eval v1 tables only.
    """

    op.drop_index(
        op.f(
            "ix_eval_result_experiment_id"
        ),
        table_name="eval_result",
    )

    op.drop_index(
        op.f(
            "ix_eval_result_eval_case_id"
        ),
        table_name="eval_result",
    )

    op.drop_table(
        "eval_result"
    )

    op.drop_index(
        op.f(
            "ix_eval_case_expected_document_id"
        ),
        table_name="eval_case",
    )

    op.drop_index(
        op.f(
            "ix_eval_case_expected_chunk_id"
        ),
        table_name="eval_case",
    )

    op.drop_index(
        op.f(
            "ix_eval_case_dataset_id"
        ),
        table_name="eval_case",
    )

    op.drop_table(
        "eval_case"
    )

    op.drop_index(
        op.f(
            "ix_eval_experiment_knowledge_base_id"
        ),
        table_name="eval_experiment",
    )

    op.drop_index(
        op.f(
            "ix_eval_experiment_dataset_id"
        ),
        table_name="eval_experiment",
    )

    op.drop_table(
        "eval_experiment"
    )

    op.drop_index(
        op.f(
            "ix_eval_dataset_knowledge_base_id"
        ),
        table_name="eval_dataset",
    )

    op.drop_table(
        "eval_dataset"
    )