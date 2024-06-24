import requests
from datetime import datetime
import os


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
    ) -> dict:
        """Get funding rate for futures trading on exchange. On this endpoint
        the number of historical prices is limited to 1000, regardless of the interval."""
        path = "/futures/fundingRate/ohlc-history"
        params = {"exchange": exchange, "symbol": symbol, "interval": interval}
        data = self.get(path=path, params=params)
        for d in data:
            d["utc"] = self.unix_to_utc(d["t"])
        return data

    def unix_to_utc(self, unix_time: int) -> str:
        return datetime.utcfromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")
