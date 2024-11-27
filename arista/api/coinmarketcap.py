import logging
import os
from datetime import datetime

import requests

from arista.models.coinmarketcap import CoinMarketCapHistory

logger = logging.getLogger(__name__)


class CoinMarketCapAPI:
    """CoinMarketCap API client."""

    URL: str = "https://pro-api.coinmarketcap.com/v1/cryptocurrency"
    API_KEY = "COINMARKETCAP_API_KEY"

    def __init__(self):
        """Instantiate CoinMarketCapAPI."""
        logger.info("Initializing CoinMarketCapAPI")
        self._api_key = os.environ.get(self.API_KEY)

        if self._api_key is None:
            raise ValueError(f"{self.API_KEY} not set.")
        self.base_url = self.URL

    def _get_headers(self):
        return {"accept": "application/json", "X-CMC_PRO_API_KEY": self._api_key}

    def _get(self, path: str, params=None):
        """Make a GET request to Coinglass API."""
        url = f"{self.base_url}{path}"
        r = requests.get(url, params=params, headers=self._get_headers())
        r.raise_for_status()
        r = r.json()
        return r["data"]

    def listing_latest(self) -> list:
        """Get latest CoinMarketCap listing
        https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest
        """
        path = "/listings/latest"
        data = self._get(path)

        values = [self._json_to_model(d) for d in data]
        return values

    def listing_historical(self, date: str = None, datetime_: datetime = None) -> list:
        """Timestamp: ISO timestamp e.g. '2019-10-20'"""
        path = "/listings/historical"

        if datetime_:
            date = datetime_.isoformat().split("T")[0]
        if not date and not datetime_:
            raise ValueError(
                "Either date or dateteime_ should be passed as function argument."
            )

        data = self._get(path, params={"date": date})
        values = [self._json_to_model(d, date) for d in data]
        return values

    def _json_to_model(self, d: dict, date: str = None):
        timestamp_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        date = (
            date
            or datetime.strptime(d["last_updated"], timestamp_fmt)
            .isoformat()
            .split("T")[0]
        )
        return CoinMarketCapHistory(
            cmc_rank=d["cmc_rank"],
            cmc_id=d["id"],
            name=d["name"],
            symbol=d["symbol"],
            market_cap_by_total_supply=d["quote"]["USD"]["price"]
            * d["total_supply"],  # Calculated market cap by total supply
            circulating_supply=d["circulating_supply"],
            total_supply=d["total_supply"],
            # max_supply=d["max_supply"],
            price=d["quote"]["USD"]["price"],
            volume_24h=d["quote"]["USD"]["volume_24h"],
            # volume_change_24h=d["quote"]["USD"]["volume_change_24h"],
            market_cap=d["quote"]["USD"]["market_cap"],
            # fully_diluted_market_cap=d["quote"]["USD"]["fully_diluted_market_cap"],
            utc=datetime.strptime(d["last_updated"], timestamp_fmt),
            iso_date=date,
        )
