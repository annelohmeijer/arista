from datetime import datetime

from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class FundingRate(SQLModel):
    """Model for OHLC funding rate history from Coinglass API."""

    exchange: str = Field()
    symbol: str = Field()
    o: float = Field(description="Open")
    h: float = Field(description="High")
    l: float = Field(description="Low")
    c: float = Field(description="Close")
    t: float = Field(description="Unix timestamp time in seconds")

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time).strftime(format_)

    def to_list(self):
        # order matters here
        return [self.t, self.utc, self.o, self.h, self.l, self.c]


class FundingRateTable(FundingRate, table=True):
    """Database model for OHLC funding rate history
    of multiple symbols, mutiple exchanges."""

    __tablename__ = "funding_rates"

    id: int = Field(default=None, primary_key=True)


class FundingRateRepository(BaseRepository[FundingRate]):
    """Repository to interact with Child table."""

    _model = FundingRate
