import logging

from arista import models
from arista.api.coinmarketcap import CoinMarketCapAPI

INTERVAL = "4h"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    # get data from Coinglass API
    client = CoinMarketCapAPI()
    repository = models.CoinMarketCapHistoryRepository()

    logger.info(f"Fetching latest coinmarketcap data for top 100 cryptocurrencies")
    data = client.listing_latest()

    if not data:
        raise ValueError("No data fetched from coinmarketcap")

    datetime = data[0].utc
    logger.info(f"Data fetched for {datetime}")
    logger.info(f"Fetched {len(data)} records")
    repository.bulk_create(data)


if __name__ == "__main__":
    main()
