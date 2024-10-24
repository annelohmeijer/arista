from datetime import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint

from arista.db.repositories import BaseRepository


class FundingRate(SQLModel):
    """Model for exchange aggregated open interest from Coinglass API."""

    symbol: str = Field()
    aggregated_funding_rate: float = Field(description="Aggregated funding rate")
    timestamp: int = Field(description="Unix timestamp time in seconds")
    utc: datetime = Field(description="UTC time", default=None)
    source: str = Field(description="Source of data", default="coinglass")

    def model_post_init(self, __context):
        """Add UTC field after initialization."""
        self.utc = self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(self, unix_time, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.utcfromtimestamp(unix_time)


class FundingRateTable(FundingRate, table=True):
    """Database model for aggregated funding rate of Coinglass API."""

    __tablename__ = "funding_rate"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "timestamp", "utc", name="fr_symbol_time_unique_constraint"
        ),
    )

    id: int = Field(default=None, primary_key=True)

class FundingRateRepository(BaseRepository[FundingRateTable]):
    """Repository to interact with funding rate table."""

    _model = FundingRateTable
