from datetime import datetime

from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class CoinMarketCapHistory(SQLModel):
    """Model for general Coinmarketcap data."""

    # general coin info
    cmc_rank: int = Field(description="Coinmarketcap rank")
    cmc_id: int = Field(description="Coinmarketcap ID")
    name: str = Field(description="Name")
    symbol: str = Field(description="Symbol")
    market_cap_by_total_supply: float = Field(description="Market cap by total supply")
    circulating_supply: float = Field(description="Circulating supply")
    total_supply: float = Field(description="Total supply")
    max_supply: float | None = Field(description="Max supply", default=None)

    # price info
    price: float = Field(description="Price")
    volume_24h: float = Field(description="24h volume")
    volume_change_24h: float | None = Field(
        description="24h volume change", default=None
    )
    market_cap: float = Field(description="Market cap")
    fully_diluted_market_cap: float | None = Field(
        description="Fully diluted market cap", default=None
    )
    utc: datetime = Field(description="UTC time", default=None)
    iso_date: str = Field(description="ISO time", default=None)


class CoinMarketCapHistoryTable(CoinMarketCapHistory, table=True):
    """Database model for Coinmarketcap history."""

    __tablename__ = "coinmarketcap"

    id: int = Field(default=None, primary_key=True)


class CoinMarketCapHistoryRepository(BaseRepository[CoinMarketCapHistoryTable]):
    """Repository to interact with CoinMarketCap history table."""

    _model = CoinMarketCapHistoryTable
    timestamp_col = "utc"
