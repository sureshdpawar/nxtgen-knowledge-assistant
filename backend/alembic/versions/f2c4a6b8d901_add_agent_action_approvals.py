"""add agent action approvals

Revision ID: f2c4a6b8d901
Revises: e8b3f1a4c902
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2c4a6b8d901"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "e8b3f1a4c902"
branch_labels = None
depends_on = None


approval_status_enum = sa.Enum(
    "PENDING",
    "APPROVED",
    "REJECTED",
    name="agentactionapprovalstatus",
)


def upgrade() -> None:
    op.create_table(
        "agent_action_approval",
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
            "checkpoint_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "actions",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "status",
            approval_status_enum,
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "decided_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "decided_by_user_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "decision_reason",
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
            sa.DateTime(
                timezone=True,
            ),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True,
            ),
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
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"],
            ["app_user.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "agent_run_id",
            "checkpoint_id",
            name=(
                "uq_agent_action_approval_"
                "run_checkpoint"
            ),
        ),
    )

    op.create_index(
        "ix_agent_action_approval_tenant_id",
        "agent_action_approval",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        "ix_agent_action_approval_agent_id",
        "agent_action_approval",
        ["agent_id"],
        unique=False,
    )

    op.create_index(
        "ix_agent_action_approval_agent_run_id",
        "agent_action_approval",
        ["agent_run_id"],
        unique=False,
    )

    op.create_index(
        "ix_agent_action_approval_status",
        "agent_action_approval",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_agent_action_approval_requested_at",
        "agent_action_approval",
        ["requested_at"],
        unique=False,
    )

    op.create_index(
        (
            "ix_agent_action_approval_"
            "decided_by_user_id"
        ),
        "agent_action_approval",
        ["decided_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        (
            "ix_agent_action_approval_"
            "decided_by_user_id"
        ),
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_index(
        "ix_agent_action_approval_requested_at",
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_index(
        "ix_agent_action_approval_status",
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_index(
        "ix_agent_action_approval_agent_run_id",
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_index(
        "ix_agent_action_approval_agent_id",
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_index(
        "ix_agent_action_approval_tenant_id",
        table_name=(
            "agent_action_approval"
        ),
    )

    op.drop_table(
        "agent_action_approval"
    )

    approval_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )