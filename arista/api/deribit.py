import logging
import os
from datetime import datetime

import requests

from arista.models.deribit import DeribitFutures 

logger = logging.getLogger(__name__)


class DeribitAPI:

    URL: str = "https://test.deribit.com/api/v2/public"
    API_KEY = "DERIBIT_API_KEY"

    def __init__(self):
        """Instantiate CoinMarketCapAPI."""
        logger.info("Initializing CoinMarketCapAPI")
        self._api_key = os.environ.get(self.API_KEY)

        # if self._api_key is None:
        #     raise ValueError(f"{self.API_KEY} not set.")
        self.base_url = self.URL

    def _get_headers(self):
        return {"accept": "application/json", "X-CMC_PRO_API_KEY": self._api_key}

    def _get(self, path: str, params=None):
        """Make a GET request to Deribit API.""" 
        url = f"{self.base_url}{path}"
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def get_instruments(self, currency: str) -> list[dict]:
        path = "/get_instruments"
        params = {"currency": currency, "kind": "future", "expired": "false"}
        response = self._get(path=path, params=params)
        data = response["result"]
        return data

    def get_instrument(self, instrument_name: str) -> list[dict]:
        path = "/get_instrument"
        params = {"instrument_name": instrument_name}
        response = self._get(path=path, params=params)
        data = response["result"]
        return data


