"""Fetch all data from one day ago to the present for a given symbol and Deribit future."""

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
resolution = 360


def get_nearest_resolution_time(current_time: datetime, resolution_minutes: int):
    # Convert current time to total minutes since the start of the day
    total_minutes = current_time.hour * 60 + current_time.minute
    # Find the nearest lower multiple of the resolution
    nearest_resolution_minutes = (
        total_minutes // resolution_minutes
    ) * resolution_minutes
    # Calculate the new time
    rounded_time = current_time.replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + timedelta(minutes=nearest_resolution_minutes)
    return rounded_time


async def fetch(symbol="BTC"):
    """Async function to fetch Deribit data for a given symbol."""

    global client
    global resolution

    date = get_nearest_resolution_time(datetime.now(), resolution)

    pbar = manager.counter(total=len(Future), desc=f"{symbol} futures", unit="ticks")

    data = []
    no_data = []
    failed = []

    counter = 0

    date_string = date.strftime("%Y-%m-%d %H:%M:%S")

    for future in Future:

        logger.info(f"Fetching data for {date_string}: {future}, {symbol}")
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
                resolution=resolution,
            )
            data.append(d)
            logger.info(
                "Successfully obtained Deribit future data for"
                f" {date_string}, future {future}, symbol {symbol}"
                f" with resolution : {resolution}"
            )
            logger.info(f"Data: {d}")
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

    logger.info(f"Inserting {len(data)} records into the database, {symbol}")
    repository = models.DeribitFuturesRepository()
    repository.bulk_create(data)


async def main_async():
    await fetch("BTC")
    await fetch("ETH")


def main():
    asyncio.run(main_async())
