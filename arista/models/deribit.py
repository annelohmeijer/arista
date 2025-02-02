from datetime import datetime

from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class DeribitFuture(SQLModel):
    asset: str = Field(description="BTC or ETH")
    instrument: str = Field(description="Deribit instrument name")
    future_reference: str = Field(description="future type")
    expiration: str | None = Field(description="Expiration date", default=None)
    price: float = Field(description="Close of the future at timestamp")

    unix_timestamp: int = Field(description="Timestamp of data extraction")
    datetime_: datetime = Field(
        description="Datetime of unix timestamp, for readability"
    )
    size: float | None = Field(description="Size of the future contract", default=None)


class DeribitFuturesTable(DeribitFuture, table=True):
    """Database model for Deribit Futures."""

    __tablename__ = "deribit_futures"

    id: int = Field(default=None, primary_key=True)


class DeribitFuturesRepository(BaseRepository[DeribitFuturesTable]):
    """Repository to interact with Deribit Futures table."""

    _model = DeribitFuturesTable
    timestamp_col = "unix_timestamp"
