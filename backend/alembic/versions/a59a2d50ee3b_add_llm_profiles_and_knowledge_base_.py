"""add llm profiles and knowledge base override

Revision ID: a59a2d50ee3b
Revises: a2554bdfba69
Create Date: 2026-08-14 13:51:30.211246

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a59a2d50ee3b"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "a2554bdfba69"

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
    """Upgrade schema."""

    # Add profile name to existing
    # tenant LLM configurations.
    op.add_column(
        "tenant_llm_configuration",
        sa.Column(
            "name",
            sa.String(
                length=255,
            ),
            nullable=True,
        ),
    )

    # Add default profile flag.
    op.add_column(
        "tenant_llm_configuration",
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=
                sa.text("false"),
        ),
    )

    # Existing LLM configurations
    # become named profiles.
    op.execute(
        """
        UPDATE tenant_llm_configuration
        SET name = 'Default'
        WHERE name IS NULL
        """
    )

    # Name is now required.
    op.alter_column(
        "tenant_llm_configuration",
        "name",
        existing_type=
            sa.String(
                length=255,
            ),
        nullable=False,
    )

    # Select one configuration per tenant
    # as the tenant's default profile.
    #
    # Prefer active configurations first,
    # then the oldest configuration.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                tenant_id,
                ROW_NUMBER() OVER (
                    PARTITION BY tenant_id
                    ORDER BY
                        is_active DESC,
                        created_at ASC,
                        id ASC
                ) AS row_number
            FROM tenant_llm_configuration
        )
        UPDATE tenant_llm_configuration
        AS configuration
        SET is_default = true
        FROM ranked
        WHERE
            configuration.id = ranked.id
            AND ranked.row_number = 1
        """
    )

    # PostgreSQL partial unique index:
    # a tenant can have only one
    # default LLM profile.
    op.create_index(
        "uq_tenant_llm_configuration_default",
        "tenant_llm_configuration",
        [
            "tenant_id",
        ],
        unique=True,
        postgresql_where=
            sa.text(
                "is_default = true"
            ),
    )

    # Optional KB-level LLM profile.
    #
    # NULL means:
    # use tenant default profile.
    op.add_column(
        "knowledge_base",
        sa.Column(
            "llm_configuration_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_knowledge_base_llm_configuration_id",
        "knowledge_base",
        [
            "llm_configuration_id",
        ],
        unique=False,
    )

    # If a non-default profile gets deleted,
    # affected KBs fall back to the
    # tenant default automatically.
    op.create_foreign_key(
        "fk_knowledge_base_llm_configuration",
        "knowledge_base",
        "tenant_llm_configuration",
        [
            "llm_configuration_id",
        ],
        [
            "id",
        ],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_knowledge_base_llm_configuration",
        "knowledge_base",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_knowledge_base_llm_configuration_id",
        table_name=
            "knowledge_base",
    )

    op.drop_column(
        "knowledge_base",
        "llm_configuration_id",
    )

    op.drop_index(
        "uq_tenant_llm_configuration_default",
        table_name=
            "tenant_llm_configuration",
    )

    op.drop_column(
        "tenant_llm_configuration",
        "is_default",
    )

    op.drop_column(
        "tenant_llm_configuration",
        "name",
    )