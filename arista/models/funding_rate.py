from datetime import datetime

from pydantic import computed_field
from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class FundingRate(SQLModel):
    """Model for OHLC funding rate history from Coinglass API."""

    exchange: str = Field(description="Exchange name", default="Binance")
    symbol: str = Field()
    o: float = Field(description="Open")
    h: float = Field(description="High")
    l: float = Field(description="Low")
    c: float = Field(description="Close")
    t: int = Field(description="Unix timestamp time in seconds")
    interval: str = Field(description="Metric interval (e.g. 4h)")

    @computed_field
    @property
    def utc(self) -> datetime:
        return self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time)

    def to_list(self):
        # order matters here
        return [self.t, self.utc, self.o, self.h, self.l, self.c]


class FundingRateTable(FundingRate, table=True):
    """Database model for OHLC funding rate history
    of multiple symbols, mutiple exchanges."""

    __tablename__ = "funding_rates"

    id: int = Field(default=None, primary_key=True)


class FundingRateRepository(BaseRepository[FundingRateTable]):
    """Repository to interact with Child table."""

    _model = FundingRateTable
