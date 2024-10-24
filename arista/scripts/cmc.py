import logging

from arista import models
from arista.api.cmc import CoinMarketCapAPI

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
    dates = [
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
        "2024-09-23",
        "2024-09-24",
        "2024-09-25",
        "2024-09-26",
        "2024-09-27",
        "2024-09-28",
        "2024-09-29",
        "2024-09-30",
        "2024-10-01",
        "2024-10-02",
        "2024-10-03",
        "2024-10-04",
        "2024-10-05",
        "2024-10-06",
        "2024-10-07",
        "2024-10-08",
        "2024-10-09",
        "2024-10-10",
        "2024-10-11",
        "2024-10-12",
        "2024-10-13",
        "2024-10-14",
        "2024-10-15",
        "2024-10-16",
        "2024-10-17",
        "2024-10-18",
    ]

    for date in dates:
        logger.info(f"Fetching coinmarketcap data for: {date}")
        data = client.listing_historical(date=date)
        repository.bulk_create(data)
