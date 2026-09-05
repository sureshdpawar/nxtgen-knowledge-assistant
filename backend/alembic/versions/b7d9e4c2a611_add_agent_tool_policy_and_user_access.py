"""add agent tool policy and user access

Revision ID: b7d9e4c2a611
Revises: f2c4a6b8d901
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7d9e4c2a611"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "f2c4a6b8d901"
branch_labels = None
depends_on = None


POLICY_ENUM_NAME = "toolexecutionpolicy"


def upgrade() -> None:
    policy_enum = postgresql.ENUM(
        "AUTO",
        "HUMAN_APPROVAL",
        name=POLICY_ENUM_NAME,
    )

    policy_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "agent_tool",
        sa.Column(
            "execution_policy",
            postgresql.ENUM(
                "AUTO",
                "HUMAN_APPROVAL",
                name=POLICY_ENUM_NAME,
                create_type=False,
            ),
            server_default="HUMAN_APPROVAL",
            nullable=False,
        ),
    )

    op.create_table(
        "user_agent_access",
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.UUID(),
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
            ["user_id"],
            ["app_user.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "user_id",
            "agent_id",
            name="uq_user_agent_access",
        ),
    )

    op.create_index(
        "ix_user_agent_access_user_id",
        "user_agent_access",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_user_agent_access_agent_id",
        "user_agent_access",
        ["agent_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_agent_access_agent_id",
        table_name="user_agent_access",
    )

    op.drop_index(
        "ix_user_agent_access_user_id",
        table_name="user_agent_access",
    )

    op.drop_table(
        "user_agent_access"
    )

    op.drop_column(
        "agent_tool",
        "execution_policy",
    )

    postgresql.ENUM(
        name=POLICY_ENUM_NAME,
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
