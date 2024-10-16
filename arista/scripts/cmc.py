import logging

from arista import models
from arista.api.cmc import CoinMarketCapAPI

INTERVAL = "4h"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

client = CoinMarketCapAPI()


def main():
    # get data from Coinglass API
    repository = models.CoinMarketCapHistoryRepository()
    data = client.listing_latest()
    repository.bulk_create(data)
