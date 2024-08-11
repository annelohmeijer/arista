import logging
from datetime import datetime

from arista.coinglass import CoinglassAPI
from arista.models.funding_rate import FundingRateRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


client = CoinglassAPI()
repository = FundingRateRepository()

TABLE = "funding_rates"


def sync_database(end_time: datetime, exchange: str, symbol: str, interval: str):
    """Sync database with funding rates from Coinglass API."""

    logger.info(f"Updating table {TABLE} for {symbol} until {end_time}")

    # get data from Coinglass API
    min_, max_ = repository.min_timestamp(symbol), repository.max_timestamp(symbol)
    logger.info(f"Current range in database for {symbol}: {min_} - {max_}")

    if max_ is not None and max_ > end_time:
        logger.info(f"Data in database for {symbol} is up to date until {end_time}")
        return

    # get data from Coinglass API
    funding_rates = client.get_funding_rate(
        symbol=symbol, end_time=int(end_time.timestamp())
    )
    data_min_t, data_max_t = (
        min(f.utc for f in funding_rates),
        max(f.utc for f in funding_rates),
    )

    logger.info(f"Data range from Coinglass API: {data_min_t} - {data_max_t}")

    # determine records that are not in the database
    if max_:
        funding_rates = [f for f in funding_rates if f.utc > max_]
    records = len(funding_rates)
    if records:
        records_min, records_max = (
            min(f.utc for f in funding_rates),
            max(f.utc for f in funding_rates),
        )
        logger.info(
            f"Inserting {len(funding_rates)} records into the database from range ({records_min} - {records_max})"
        )
        repository.bulk_create(funding_rates)
    else:
        logger.warning(f"Found {records} records to insert")


if __name__ == "__main__":
    """Sync script to fetch funding rates from
    Coinglass API and store them in the database."""

    # fill data per month starting in January
    months = list(range(3, 10))
    exchange = "Binance"
    symbols = ["ETHUSDT", "BTCUSDT", "LINKUSDT"]
    interval = "4h"

    for symbol in symbols:
        for month in months:
            end_time = datetime(2024, month, 1)

            sync_database(end_time, exchange, symbol, interval)
