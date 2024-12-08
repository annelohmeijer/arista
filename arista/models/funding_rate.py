from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class FundingRate(SQLModel, table=True):
    """Database model for OHLC funding rate history
    of multiple symbols, mutiple exchanges."""

    __tablename__ = "funding_rate"
    id: int = Field(default=None, primary_key=True)
    symbol: str = Field()
    o: float = Field(description="Open")
    h: float = Field(description="High")
    l: float = Field(description="Low")
    c: float = Field(description="Close")
    t: float = Field(description="Unix timestamp time in seconds")


class FundingRateRepository(BaseRepository[FundingRate]):
    """Repository to interact with Child table."""

    _model = FundingRate
    timestamp_col = "t"
