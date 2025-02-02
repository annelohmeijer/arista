"""Allow null value

Revision ID: 6304f155141a
Revises: c2c23aa49fc5
Create Date: 2024-10-16 21:25:43.291562

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "6304f155141a"
down_revision: Union[str, None] = "c2c23aa49fc5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "coin_market_cap",
        "max_supply",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        nullable=True,
    )
    op.drop_column("coin_market_cap", "timestamp")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "coin_market_cap",
        sa.Column("timestamp", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.alter_column(
        "coin_market_cap",
        "max_supply",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        nullable=False,
    )
    # ### end Alembic commands ###
