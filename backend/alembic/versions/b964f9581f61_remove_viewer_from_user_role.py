"""remove viewer from user role

Revision ID: b964f9581f61
Revises: ef73b3e48f3f
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b964f9581f61"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "ef73b3e48f3f"

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
    Remove VIEWER from the PostgreSQL
    userrole enum.

    This assumes there are no existing
    app_user rows with role = 'VIEWER'.
    """

    op.execute(
        """
        ALTER TABLE app_user
        ALTER COLUMN role
        TYPE VARCHAR
        USING role::text
        """
    )

    op.execute(
        """
        DROP TYPE userrole
        """
    )

    op.execute(
        """
        CREATE TYPE userrole AS ENUM (
            'ADMIN',
            'USER',
            'SUPERADMIN'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE app_user
        ALTER COLUMN role
        TYPE userrole
        USING role::userrole
        """
    )


def downgrade() -> None:
    """
    Restore VIEWER to the PostgreSQL
    userrole enum.
    """

    op.execute(
        """
        ALTER TABLE app_user
        ALTER COLUMN role
        TYPE VARCHAR
        USING role::text
        """
    )

    op.execute(
        """
        DROP TYPE userrole
        """
    )

    op.execute(
        """
        CREATE TYPE userrole AS ENUM (
            'ADMIN',
            'USER',
            'VIEWER',
            'SUPERADMIN'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE app_user
        ALTER COLUMN role
        TYPE userrole
        USING role::userrole
        """
    )