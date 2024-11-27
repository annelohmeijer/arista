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

    logger.info(f"Fetching latest coinmarketcap data")
    data = client.listing_latest()

    repository.bulk_create(data)


if __name__ == "__main__":
    main()
