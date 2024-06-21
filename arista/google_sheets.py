import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetAPI:
    URL: str = "https://sheets.googleapis.com"
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
        if r["code"] != 0:
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
        return self.get(path=path, params=params)


def get_values(spreadsheet_id, range_name):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds, _ = google.auth.default()
    # pylint: disable=maybe-no-member
    try:
        service = build("sheets", "v4", credentials=creds)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == "__main__":
    # Pass: spreadsheet_id, and range_name
    get_values("1UX91fvcKfvy7hGlUDzfqSEzsfMZMO9pkRDAzhhBOx0E", "A1:C2")
