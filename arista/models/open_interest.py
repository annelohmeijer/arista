from datetime import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint

from arista.db.repositories import BaseRepository


class OpenInterest(SQLModel):
    """Model for exchange aggregated open interest from Coinglass API."""

    symbol: str = Field()
    aggregated_open_interest: float = Field(description="Open Interest")
    timestamp: int = Field(description="Unix timestamp time in seconds")
    utc: datetime = Field(description="UTC time", default=None)
    source: str = Field(description="Source of data", default="coinglass")

    def model_post_init(self, __context):
        """Add UTC field after initialization."""
        self.utc = self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time)


class OpenInterestTable(OpenInterest, table=True):
    """Database model for aggregated open interest of Coinglass API."""

    __tablename__ = "open_interest"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "timestamp", "utc", name="oi_symbol_time_unique_constraint"
        ),
    )

    id: int = Field(default=None, primary_key=True)


class OpenInterestRepository(BaseRepository[OpenInterestTable]):
    """Repository to interact with open interest table."""

    _model = OpenInterestTable
    timestamp_col = "timestamp"
