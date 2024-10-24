import logging
from datetime import datetime

import yaml

from arista import models
from arista.api.coinglass import CoinglassAPI

INTERVAL = "4h"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

client = CoinglassAPI()


def sync_database(
    repository,
    end_time: datetime,
    symbol: str,
    interval: str,
):
    """Sync database with funding rates from Coinglass API."""

    logger.info(
        f"Updating {repository._model.__tablename__} for"
        f"symbol {symbol} until {end_time}"
    )

    filters = [("symbol", symbol)]
    min_, max_ = repository.min_timestamp(filters=filters), repository.max_timestamp(
        filters=filters
    )
    logger.info(f"Current range in database for {symbol}: {min_} - {max_}")

    if max_ is not None and max_ > end_time:
        logger.info(f"Data in database for {symbol} is up to date until {end_time}")
        return

    # get data from Coinglass API
    records = client.get_aggregated_open_interest_history(
        symbol=symbol,
        end_time=int(end_time.timestamp()),
        interval=interval,
    )
    import pdb

    pdb.set_trace()

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
            f"Inserting {len(records)} records into the database "
            f"from range ({records_min} - {records_max})"
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

    end_time = datetime.now()
    for future, symbols in conf.items():
        for symbol in symbols["symbols"]:
            sync_database(
                end_time=end_time,
                symbol=symbol,
                interval=INTERVAL,
                repository=models.OpenInterestRepository(),
            )


if __name__ == "__main__":
    main()
