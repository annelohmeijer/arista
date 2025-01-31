import logging
import time
from datetime import datetime, timedelta

from arista import models
from arista.api.coinglass import CoinglassAPI
from arista.api.coinmarketcap import CoinMarketCapAPI

INTERVAL = "12h"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

client = CoinglassAPI()


def sync_database(
    repository,
    start_time: datetime,
    end_time: datetime,
    symbol: str,
    interval: str,
):
    """Sync database with funding rates from Coinglass API."""

    logger.info(
        f"Updating {repository._model.__tablename__} for "
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
        start_time=int(start_time.timestamp()),
        end_time=int(end_time.timestamp()),
        interval=interval,
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
            f"Inserting {len(records)} records into the database "
            f"from range ({records_min} - {records_max})"
        )
        repository.bulk_create(records)
    else:
        logger.warning(f"Found {records} records to insert")


def main():
    """Sync script to fetch funding rates from
    Coinglass API and store them in the database."""

    logger.info(f"Fetching latest top 100 coins from CoinMarketCap")
    cmc_client = CoinMarketCapAPI()
    data = cmc_client.listing_latest()
    top100_symbols = [d.symbol for d in data]
    logger.info(f"Top 100 symbols: {top100_symbols}")

    symbols = client.get_supported_coins()
    logger.info(f"Supported symbols on Coinglass: {len(symbols)}")

    logger.info(f"Filtering out unsupported symbols")
    symbols = [s for s in symbols if s in top100_symbols]
    logger.info(f"Filtered symbols: {len(symbols)}")

    start_time = datetime.now() - timedelta(days=350)
    end_time = datetime.now()

    # TODO: Add Funding Rate after pipeline is fixed
    # repositories = [models.FundingRateRepository(), models.OpenInterestRepository()]
    for repository in [models.OpenInterestRepository()]:
        for symbol in symbols:
            time.sleep(2)
            sync_database(
                repository=repository,
                start_time=start_time,
                end_time=end_time,
                symbol=symbol,
                interval=INTERVAL,
            )


if __name__ == "__main__":
    main()
