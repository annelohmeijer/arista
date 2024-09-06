import logging
import os

import requests

from arista.models.ohlc_history import OHLCHistory

logger = logging.getLogger(__name__)


class CoinglassAPI:
    """Coinglass API client."""

    URL: str = "https://open-api-v3.coinglass.com/api"
    RATE_LIMIT_REQUESTS_PER_MIN: int = 30
    RESPONSE_LIMIT: int = 4500
    API_KEY = "COINGLASS_API_KEY"

    def __init__(self):
        """Instantiate CoinglassAPI."""
        logger.info("Initializing CoinglassAPI")
        self._api_key = os.environ.get(self.API_KEY)
        if self._api_key is None:
            raise ValueError(f"{self.API_KEY} not set.")
        self.base_url = self.URL

    def _get_headers(self):
        return {"accept": "application/json", "CG-API-KEY": self._api_key}

    def _get(self, path: str, params=None):
        """Make a GET request to Coinglass API."""
        url = f"{self.base_url}{path}"
        r = requests.get(url, params=params, headers=self._get_headers())
        r.raise_for_status()
        r = r.json()
        if int(r["code"]) != 0:
            raise ValueError(r["msg"])
        return r["data"]

    def get_supported_coins(self) -> dict:
        """Get supported coins for futures trading."""
        path = "/futures/supported-coins"
        return self._get(path=path)

    def get_olhc_history(
        self,
        symbol: str,
        future: str,
        exchange: str,
        interval: str,
        response_limit: int = None,
        start_time: int = None,
        end_time: int = None,
    ) -> list[OHLCHistory]:
        """Get OHLC history for futures trading on exchange. On this endpoint
        the number of historical prices is limited to 1000, regardless of the interval.
        """
        path = f"/futures/{future}/ohlc-history"
        params = {
            "exchange": exchange,
            "symbol": symbol,
            "interval": interval,
            "limit": response_limit or self.RESPONSE_LIMIT,
            "startTime": start_time,
            "endTime": end_time,
        }
        logger.info(f"Calling {path} with params {params}")
        data = self._get(path=path, params=params)

        return [
            OHLCHistory(exchange=exchange, symbol=symbol, interval=interval, **v)
            for v in data
        ]
