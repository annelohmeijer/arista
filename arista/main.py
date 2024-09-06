import logging
from datetime import datetime
from enum import Enum

import yaml

from arista.coinglass import CoinglassAPI
from arista import models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

INTERVAL = "4h"


client = CoinglassAPI()

class Repositories(str, Enum):
    """Utility class to store all repositories,
    such that can be easily accessed by table name."""
    funding_rate = models.FundingRateRepository()
    open_interest = models.OpenInterestRepository()


def sync_database(table: str, end_time: datetime, exchange: str, symbol: str, interval: str):
    """Sync database with funding rates from Coinglass API."""

    logger.info(f"Updating table {table} for {symbol} until {end_time}")

    # get data from Coinglass API
    repository = Repositories.get(table)
    min_, max_ = repository.min_timestamp(symbol), repository.max_timestamp(symbol)
    logger.info(f"Current range in database for {symbol}: {min_} - {max_}")

    if max_ is not None and max_ > end_time:
        logger.info(f"Data in database for {symbol} is up to date until {end_time}")
        return

    # get data from Coinglass API
    records = client.get_ohlc_history(
        symbol=symbol, end_time=int(end_time.timestamp(), future=repository.coinglass_future)
    )
    data_min_t, data_max_t = (
        min(f.utc for f in records),
        max(f.utc for f in records),
    )

    logger.info(f"Data range from Coinglass API: {data_min_t} - {data_max_t}")

    # determine records that are not in the database
    if max_:
        records = [f for f in records if f.utc > max_]
    record_count = len(records)
    if record_count:
        records_min, records_max = (
            min(f.utc for f in records),
            max(f.utc for f in records),
        )
        logger.info(
            f"Inserting {len(records)} records into the database from range ({records_min} - {records_max})"
        )
        repository.bulk_create(records)
    else:
        logger.warning(f"Found {records} records to insert")


def get_config(path: str):
    """Get configuration from a file."""
    with open(path) as file:
        return yaml.safe_load(file)


def main():
    """Sync script to fetch funding rates from
    Coinglass API and store them in the database."""

    conf = get_config("config/exchanges.yml")

    # fill data per month starting in January
    end_time = datetime.now()
    for table, exchange in conf.items():
        for symbol in exchange["symbols"]:
            sync_database(end_time, exchange, symbol, interval=INTERVAL, table=table)

if __name__ == "__main__":
    main()

