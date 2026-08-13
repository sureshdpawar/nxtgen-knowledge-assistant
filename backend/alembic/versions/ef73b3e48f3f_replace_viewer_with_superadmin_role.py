"""replace viewer with superadmin role

Revision ID: ef73b3e48f3f
Revises: 63b9d99ddc95
Create Date: 2026-08-13 19:06:29.272945
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ef73b3e48f3f"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "63b9d99ddc95"

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
    Add SUPERADMIN to the PostgreSQL
    userrole enum.

    VIEWER is intentionally left in the
    database enum for now, but the
    application no longer uses it.
    """

    op.execute(
        """
        ALTER TYPE userrole
        ADD VALUE IF NOT EXISTS 'SUPERADMIN'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing
    an enum value directly with ALTER TYPE.

    Therefore this downgrade intentionally
    does nothing.
    """

    pass