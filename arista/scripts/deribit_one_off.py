"""Starting today run back and fetch all deribit data."""

import asyncio
import logging
import time
from datetime import datetime, timedelta

import enlighten

from arista import models
from arista.api.deribit import DeribitAPI, Future

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger()


manager = enlighten.get_manager()

client = DeribitAPI()


async def fetch(symbol="ETH"):
    """Async function to fetch Deribit data for a given symbol."""

    global client
    start_date = datetime.strptime("2024-11-01", client.DATE_FORMAT)
    end_date = datetime.strptime("2024-12-08", client.DATE_FORMAT)
    dates = [
        start_date + timedelta(days=x) for x in range((end_date - start_date).days)
    ]

    for future in Future:
        pbar = manager.counter(total=len(dates), desc="Dates", unit="ticks")
        logger.info(f"Fetching data for {future}, {symbol}")

        data = []
        no_data = []
        failed = []

        counter = 0

        for date in dates:
            date_string = date.strftime(client.DATE_FORMAT)
            time.sleep(0.1)
            counter += 1

            try:
                instruments = await client.get_historical_instruments(
                    date=date, symbol=symbol
                )
                instrument_name = instruments[future][symbol]

                d = await client.get_future_data_from_instrument_name(
                    date=date,
                    future=future,
                    instrument_name=instrument_name,
                    symbol=symbol,
                )
                data.append(d)
                logger.info(
                    "Successfully obtained Deribit future data for"
                    f" {date_string}, future {future}, symbol {symbol}"
                )
            except ValueError as exc:
                logger.error(
                    f"No data for {date_string} for instrument "
                    f"{instrument_name}, {future}, symbol {symbol}"
                )
                no_data.append(
                    {
                        "date": date,
                        "instrument_name": instrument_name,
                        "future": future,
                        "symbol": symbol,
                        "exc": exc,
                    }
                )
            except KeyError as exc:
                logger.error(
                    f"Failed request {date_string} for instrument "
                    f"{instrument_name}, {future}, symbol {symbol}"
                )
                failed.append(
                    {
                        "date": date,
                        "instrument_name": instrument_name,
                        "future": future,
                        "symbol": symbol,
                        "exc": exc,
                    }
                )
            logger.info(f"Calls: {counter}")
            pbar.update()

        logger.info(f"Failed records: {len(failed)}")
        logger.info(f"No data records: {len(no_data)}")

        logger.info(
            f"Inserting {len(data)} records into the database {future}, {symbol}"
        )
        repository = models.DeribitFuturesRepository()
        repository.bulk_create(data)
        time.sleep(2)


asyncio.run(fetch())
