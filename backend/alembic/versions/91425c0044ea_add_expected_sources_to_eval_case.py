"""add expected sources to eval case

Revision ID: 91425c0044ea
Revises: 33e3a2796070
Create Date: 2026-08-25 19:39:19.610214

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91425c0044ea"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "33e3a2796070"

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
    Add portable expected source metadata
    to evaluation cases.

    Example value:

    [
        {
            "type": "url",
            "value":
                "https://nxtgeninnovate.com/"
                "ai-data-science-solutions.html"
        }
    ]

    Existing rows receive an empty list.
    """

    op.add_column(
        "eval_case",
        sa.Column(
            "expected_sources",
            sa.JSON(),
            nullable=False,
            server_default=sa.text(
                "'[]'::json"
            ),
        ),
    )


def downgrade() -> None:
    """
    Remove portable expected source metadata.
    """

    op.drop_column(
        "eval_case",
        "expected_sources",
    )