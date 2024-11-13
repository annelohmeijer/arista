import calendar
import logging
import time
from datetime import datetime, timedelta
from enum import Enum

import httpx
from pydantic import BaseModel, Field

# from arista.models.deribit import DeribitFuture

logger = logging.getLogger(__name__)


class DeribitFuture(BaseModel):

    asset: str = Field(description="BTC or ETH")

    instrument: str = Field(description="Deribit instrument name")
    future_reference: str = Field(description="future type")
    expiration: str | None = Field(description="Expiration date", default=None)
    price: float = Field(description="Close of the future at timestamp")

    unix_timestamp: int = Field(description="Timestamp of data extraction")
    datetime_: datetime = Field(
        description="Datetime of unix timestamp, for readability"
    )


class Future(str, Enum):
    """Different type of futures."""

    current_week = "current_week"
    next_week = "next_week"
    current_month = "current_month"
    current_quarter = "current_quarter"
    first_month_next_quarter = "first_month_next_quarter"
    quarter_1 = "quarter_1"
    quarter_2 = "quarter_2"
    quarter_3 = "quarter_3"
    perperpetual = "perpetual"


class DeribitAPI:
    """Async Deribit API client."""

    URL: str = "https://test.deribit.com/api/v2/public"
    request_timeout = 20
    max_request_connections: int = 50
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self):
        """Instantiate CoinMarketCapAPI."""
        self.base_url = self.URL
        timeout = httpx.Timeout(self.request_timeout)
        limits = httpx.Limits(
            max_keepalive_connections=self.max_request_connections,
            max_connections=self.max_request_connections,
        )
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits)

    async def _get(self, path: str, params=None):
        """Make a GET request to Deribit API."""
        url = f"{self.base_url}{path}"
        r = await self.client.get(url, params=params)
        return r.json()

    async def get_instruments(self, currency: str) -> list[dict]:
        path = "/get_instruments"
        params = {"currency": currency, "kind": "future", "expired": "false"}
        response = await self._get(path=path, params=params)
        data = response["result"]
        return data

    async def get_instrument(self, instrument_name: str) -> list[dict]:
        path = "/get_instrument"
        params = {"instrument_name": instrument_name}
        response = await self._get(path=path, params=params)
        data = response["result"]
        return data

    async def get_tradingview_data(self, params: dict) -> dict:
        path = "/get_tradingview_chart_data"
        response = await self._get(path=path, params=params)
        return response

    async def get_future_data(
        self, date: str, future: Future, symbol: str = "BTC"
    ) -> DeribitFuture:
        """Get Future data for any date in the past."""
        datetime_ = datetime.strptime(date, self.DATE_FORMAT)

        # determine min and max timestamp for current date (i.e 00:00 and 24:00 of any given day)
        start_timestamp = int(time.mktime(datetime_.timetuple()))
        end_timestamp = int(
            time.mktime((datetime_ + timedelta(days=1, seconds=-1)).timetuple())
        )

        expiration_dates = self.compute_initial_expiration_dates(datetime_)

        # Roll over expiration dates if necessary
        expiration_dates = self.roll_over_expiration_dates(
            expiration_dates, current_date
        )

        # Format instrument names
        futures = self.format_instrument_names(expiration_dates, symbols=[symbol])

        instrument_name = futures[future][symbol]

        data = await self.get_tradingview_data(
            params={
                "start_timestamp": start_timestamp * 1000,
                "end_timestamp": end_timestamp * 1000,
                "instrument_name": instrument_name,
                "resolution": "1D",
            }
        )

        if data["result"]["status"] == "no_data":
            logger.warning(
                f"Deribit API returned no data for {date}, future {future}: {instrument_name}"
            )

        record = DeribitFuture(
            asset=symbol,
            instrument=instrument_name,
            future_reference=future,
            expiration=None,
            price=data["result"]["close"][0],
            unix_timestamp=start_timestamp,
            datetime_=datetime.fromtimestamp(start_timestamp),
        )
        return record

    def last_friday(self, year, month):
        # Find the last Friday of the given month and year
        last_day = calendar.monthrange(year, month)[1]
        last_friday_date = datetime(year, month, last_day)
        while last_friday_date.weekday() != calendar.FRIDAY:
            last_friday_date -= timedelta(days=1)
        return last_friday_date

    def compute_initial_expiration_dates(self, day):
        year, month = day.year, day.month
        expiration_dates = {}

        # Calculate "current_week" and "next_week" expiration dates
        current_week_friday = day + timedelta((calendar.FRIDAY - day.weekday()) % 7)
        next_week_friday = current_week_friday + timedelta(days=7)
        expiration_dates["current_week"] = current_week_friday
        expiration_dates["next_week"] = next_week_friday

        # Calculate "current_month" expiration date
        expiration_dates["current_month"] = self.last_friday(year, month)

        # Calculate "current_quarter" expiration date
        current_quarter = (month - 1) // 3 + 1
        quarter_end_month = current_quarter * 3
        expiration_dates["current_quarter"] = self.last_friday(year, quarter_end_month)

        # Calculate the first month of the next quarter
        first_month_next_quarter = (
            quarter_end_month + 1 if quarter_end_month < 12 else 1
        )
        next_quarter_year = year + 1 if first_month_next_quarter == 1 else year
        expiration_dates["first_month_next_quarter"] = self.last_friday(
            next_quarter_year, first_month_next_quarter
        )

        # Calculate "next_quarter", "second_next_quarter", and "third_next_quarter"
        for i in range(1, 4):
            quarter_month = (current_quarter + i) * 3
            quarter_year = year + (quarter_month - 1) // 12
            quarter_month = (quarter_month - 1) % 12 + 1
            expiration_dates[f"quarter_{i}"] = self.last_friday(
                quarter_year, quarter_month
            )

        return expiration_dates

    def roll_over_expiration_dates(self, expiration_dates, current_date):
        # Roll over expiration dates if they are reached
        rolled_expirations = {}
        for key, expiration_date in expiration_dates.items():
            if current_date >= expiration_date:
                # If it's a weekly expiration, move to next week
                if key == "current_week":
                    rolled_expirations[key] = expiration_date + timedelta(days=7)
                # If it's a monthly expiration, move to next month's last Friday
                elif key == "current_month":
                    next_month = expiration_date.month % 12 + 1
                    next_month_year = expiration_date.year + (
                        1 if next_month == 1 else 0
                    )
                    rolled_expirations[key] = self.last_friday(
                        next_month_year, next_month
                    )
                # If it's a quarterly expiration, move to the next quarter's last Friday
                elif key == "current_quarter":
                    next_quarter_month = (expiration_date.month + 2) // 3 * 3 + 3
                    next_quarter_year = expiration_date.year + (
                        1 if next_quarter_month > 12 else 0
                    )
                    next_quarter_month = next_quarter_month % 12 or 12
                    rolled_expirations[key] = self.last_friday(
                        next_quarter_year, next_quarter_month
                    )
                else:
                    rolled_expirations[key] = expiration_date
            else:
                rolled_expirations[key] = expiration_date
        return rolled_expirations

    def format_instrument_names(self, expiration_dates, symbols=["BTC", "ETH"]):
        instruments = {}
        for period, date in expiration_dates.items():
            # Use `%-d` for day without leading zero, `%b` for abbreviated month, and `%y` for two-digit year
            instrument_names = {
                symbol: f"{symbol}-{date.strftime('%-d%b%y').upper()}"
                for symbol in symbols
            }
            instruments[period] = instrument_names

        # Add perpetual futures for BTC and ETH
        instruments["perpetual"] = {symbol: f"{symbol}-PERPETUAL" for symbol in symbols}

        return instruments
