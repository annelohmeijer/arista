import logging
from datetime import datetime, timedelta

import yaml

from arista import models
from arista.api.deribit import DeribitAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

client = DeribitAPI()

currency_instruments = client.get_instruments(currency="BTC")

instruments = [i["instrument_name"] for i in currency_instruments]

for instrument in instruments:
    data = client.get_instrument(instrument_name=instrument)

    import pdb; pdb.set_trace()

    logger.info(data)


    repository = models.DeribitFuturesRepository()
    repository.bulk_create(data)





