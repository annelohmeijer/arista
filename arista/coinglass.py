import os
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class FundingRate:
    """Dataclass object for FundingRate that is returned by Coinglass API."""

    t: int
    o: float
    h: float
    l: float
    c: float

    def __post_init__(self):
        """Add utc field to Rate object from timestamp."""
        self.utc = self._timestamp_to_utc(self.t)

    def _timestamp_to_utc(
        self, unix_time, str_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Convert unix timestamp to UTC time."""
        return datetime.utcfromtimestamp(unix_time).strftime(str_format)

    def to_list(self) -> list:
        """Convert Rate object to list, suitable for writing to Google Sheets."""
        return [self.t, self.utc, self.o, self.h, self.l, self.c]


class CoinglassAPI:
    """Coinglass API client."""

    URL: str = "https://open-api-v3.coinglass.com/api"
    RATE_LIMIT_REQUESTS_PER_MIN: int = 30
    API_KEY = "COINGLASS_API_KEY"

    def __init__(self):
        self._api_key = os.environ.get(self.API_KEY)
        if self._api_key is None:
            raise ValueError(f"{self.API_KEY} not set.")
        self.base_url = self.URL

    def _get_headers(self):
        return {"accept": "application/json", "CG-API-KEY": self._api_key}

    def get(self, path: str, params=None):
        """Make a GET request to Coinglass API."""
        url = f"{self.base_url}{path}"
        r = requests.get(url, params=params, headers=self._get_headers())
        r.raise_for_status()
        r = r.json()
        if int(r["code"]) != 0:
            raise ValueError(r["msg"])
        return r["data"]

    def post(self, path: str, data):
        return requests.post(self.url + path, data)

    def get_supported_coins(self) -> dict:
        """Get supported coins for futures trading."""
        path = "/futures/supported-coins"
        return self.get(path=path)

    def get_funding_rate(
        self, exchange: str = "Binance", symbol: str = "BTCUSDT", interval: str = "8h"
    ) -> list[Rate]:
        """Get funding rate for futures trading on exchange. On this endpoint
        the number of historical prices is limited to 1000, regardless of the interval.
        """
        path = "/futures/fundingRate/ohlc-history"
        params = {"exchange": exchange, "symbol": symbol, "interval": interval}
        data = self.get(path=path, params=params)
        rates = [FundingRate(**d) for d in data]
        return rates
