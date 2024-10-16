from datetime import datetime

from sqlmodel import Field, SQLModel

from arista.db.repositories import BaseRepository


class OHLCHistory(SQLModel):
    """Model for OHLC history from Coinglass API.

    Note this model is future agnostic: all OLHC history futures
    returned by Coinglass are returned in the same format.
    """

    exchange: str = Field(description="Exchange name", default="Binance")
    symbol: str = Field()
    coinglass_future: str = Field(description="Name of future in Coinglass API")
    o: float = Field(description="Open")
    h: float = Field(description="High")
    l: float = Field(description="Low")
    c: float = Field(description="Close")
    t: int = Field(description="Unix timestamp time in seconds")
    interval: str = Field(description="Metric interval (e.g. 4h)")
    utc: datetime = Field(description="UTC time", default=None)

    def model_post_init(self, __context):
        """Add UTC field after initialization."""
        self.utc = self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time)


class OHLCHistoryTable(OHLCHistory, table=True):
    """Database model for OHLC history
    of multiple symbols, mutiple exchanges, multiple futures."""

    __tablename__ = "ohlc_history"

    id: int = Field(default=None, primary_key=True)


class OHLCHistoryRepository(BaseRepository[OHLCHistoryTable]):
    """Repository to interact with OHLC History table."""

    _model = OHLCHistoryTable
