"""Add datetiem

Revision ID: 1e7b3533c80b
Revises: 6de998d43fe0
Create Date: 2024-08-11 11:50:02.186838

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "1e7b3533c80b"
down_revision: Union[str, None] = "6de998d43fe0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("funding_rates", sa.Column("utc", sa.DateTime(), nullable=False))
    op.alter_column(
        "funding_rates",
        "t",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "funding_rates",
        "t",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.drop_column("funding_rates", "utc")
    # ### end Alembic commands ###
