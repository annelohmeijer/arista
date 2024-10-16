from arista.db.repositories import BaseRepository
from datetime import datetime

from sqlmodel import Field, SQLModel


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
    max_supply: float = Field(description="Max supply")

    # price info
    price: float = Field(description="Price")
    volume_24h: float = Field(description="24h volume")
    volume_change_24h: float = Field(description="24h volume change")
    market_cap: float = Field(description="Market cap")
    fully_diluted_market_cap: float = Field(description="Fully diluted market cap")
    timestamp: int = Field(description="Unix timestamp time in seconds")
    utc: datetime = Field(description="UTC time", default=None)

    def model_post_init(self, __context):
        """Add UTC field after initialization."""
        self.utc = self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time)

class CoinMarketCapHistoryTable(CoinMarketCapHistory, table=True):
    """Database model for Coinmarketcap history."""

    __tablename__ = "coin_market_cap"

    id: int = Field(default=None, primary_key=True)


class CoinMarketCapHistoryRepository(BaseRepository[CoinMarketCapHistoryTable]):
    """Repository to interact with CoinMarketCap history table."""

    _model = CoinMarketCapHistoryTable
