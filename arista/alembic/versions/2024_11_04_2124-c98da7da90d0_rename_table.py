"""Rename table

Revision ID: c98da7da90d0
Revises: a03a1e549978
Create Date: 2024-11-04 21:24:49.049283

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "c98da7da90d0"
down_revision: Union[str, None] = "a03a1e549978"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("coin_market_cap", "coinmarketcap")
    op.execute("ALTER SEQUENCE coin_market_cap_id_seq RENAME TO coinmarketcap_id_seq")
    op.execute("ALTER INDEX coin_market_cap_pkey RENAME TO coinmarketcap_pkey")
    pass


def downgrade():
    op.rename_table("coinmarketcap", "coin_market_cap")
    op.execute("ALTER SEQUENCE coinmarketcap_id_seq RENAME TO coin_market_cap_id_seq")
    op.execute("ALTER INDEX coinmarketcap_pkey RENAME TO coin_market_cap_pkey")
