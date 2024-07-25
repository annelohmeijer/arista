from sqlmodel import Field, SQLModel


class FundingRate(SQLModel, table=True):
    """Database model for OHLC funding rate history
    of multiple symbols, mutiple exchanges."""

    exchange: str = Field()
    symbol: str = Field()
    o: float = Field(description="Open")
    h: float = Field(description="High")
    l: float = Field(description="Low")
    c: float = Field(description="Close")
    t: float = Field(description="Unix timestamp time in seconds")
