import logging
import os

import requests

from arista.models.open_interest import OpenInterest

logger = logging.getLogger(__name__)

RATE_LIMIT_EXCEEDED = "50001"


class CoinglassAPI:
    """Coinglass API client.

    Note: the Coinglass API returns data in format
    ```
    {
        "code": "0",
        "msg": "success",
        "data": [
            {
            "t": 1636588800,
            "o": "28087369127",
            "h": "28087369127",
            "l": "25321306769",
            "c": "25347636671"
            },
            ...
        ]
    }
    ```
    and also returns 'success' when no data is returned.
    """

    URL: str = "https://open-api-v3.coinglass.com/api"
    RATE_LIMIT_REQUESTS_PER_MIN: int = 30
    RESPONSE_LIMIT: int = 4500
    API_KEY = "COINGLASS_API_KEY"
    SOURCE: str = "coinglass"

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
            if r["msg"] == RATE_LIMIT_EXCEEDED:
                raise ValueError("Rate limit exceeded.")
            raise ValueError(r["msg"])
        if r["msg"] == "success" and len(r["data"]) == 0:
            raise ValueError(f"No data returned for {path} with params {params}.")
        return r["data"]

    def get_supported_coins(self) -> dict:
        """Get supported coins for futures trading."""
        path = "/futures/supported-coins"
        return self._get(path=path)

    def get_aggregated_open_interest_history(
        self,
        symbol: str,
        interval: str,
        response_limit: int = None,
        start_time: int = None,
        end_time: int = None,
    ) -> list[OpenInterest]:
        """Query futures/openInterest/ohlc-aggregated-history
        endpoint from Coinglass API."""
        path = "/futures/openInterest/ohlc-aggregated-history"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": response_limit or self.RESPONSE_LIMIT,
            "startTime": start_time,
            "endTime": end_time,
        }
        logger.info(f"Calling {path} with params {params}")
        data = self._get(path=path, params=params)

        return [
            OpenInterest(
                symbol=symbol,
                aggregated_open_interest=v["c"],
                unix_timestamp=v["t"],
            )
            for v in data
        ]

    def get_funding_rate_history(
        self,
        symbol: str,
        interval: str,
        response_limit: int = None,
        start_time: int = None,
        end_time: int = None,
    ) -> list[OpenInterest]:
        """Query futures/fundingRate/ohlc-aggregated-history
        endpoint from Coinglass API."""
        raise NotImplementedError("This method is not implemented yet.")

        # path = "/futures/fundingRate/ohlc-aggregated-history"
        # params = {
        #     "symbol": symbol,
        #     "interval": interval,
        #     "limit": response_limit or self.RESPONSE_LIMIT,
        #     "startTime": start_time,
        #     "endTime": end_time,
        # }
        # logger.info(f"Calling {path} with params {params}")
        # data = self._get(path=path, params=params)
        #
        # return [
        #     OpenInterest(
        #         symbol=symbol,
        #         aggregated_open_interest=v["c"],
        #         unix_timestamp=v["t"],
        #     )
        #     for v in data
        # ]
        #
