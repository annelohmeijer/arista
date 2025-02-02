"""Add FundingRate table

Revision ID: 9235dd11c33c
Revises: b336c35ee74b
Create Date: 2024-07-27 11:27:22.975448

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9235dd11c33c"
down_revision: Union[str, None] = "b336c35ee74b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "fundingrate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exchange", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("symbol", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("o", sa.Float(), nullable=False),
        sa.Column("h", sa.Float(), nullable=False),
        sa.Column("l", sa.Float(), nullable=False),
        sa.Column("c", sa.Float(), nullable=False),
        sa.Column("t", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("fundingrate")
    # ### end Alembic commands ###
