"""Helper module to determine what futures exist for given date on deribit."""

import calendar
import time
from datetime import datetime, timedelta


def last_friday(year, month):
    # Find the last Friday of the given month and year
    last_day = calendar.monthrange(year, month)[1]
    last_friday_date = datetime(year, month, last_day)
    while last_friday_date.weekday() != calendar.FRIDAY:
        last_friday_date -= timedelta(days=1)
    return last_friday_date


def calculate_initial_expiration_dates(day):
    year, month = day.year, day.month
    expiration_dates = {}

    # Calculate "current_week" and "next_week" expiration dates
    current_week_friday = day + timedelta((calendar.FRIDAY - day.weekday()) % 7)
    next_week_friday = current_week_friday + timedelta(days=7)
    expiration_dates["current_week"] = current_week_friday
    expiration_dates["next_week"] = next_week_friday

    # Calculate "current_month" expiration date
    expiration_dates["current_month"] = last_friday(year, month)

    # Calculate "current_quarter" expiration date
    current_quarter = (month - 1) // 3 + 1
    quarter_end_month = current_quarter * 3
    expiration_dates["current_quarter"] = last_friday(year, quarter_end_month)

    # Calculate the first month of the next quarter
    first_month_next_quarter = quarter_end_month + 1 if quarter_end_month < 12 else 1
    next_quarter_year = year + 1 if first_month_next_quarter == 1 else year
    expiration_dates["first_month_next_quarter"] = last_friday(
        next_quarter_year, first_month_next_quarter
    )

    # Calculate "next_quarter", "second_next_quarter", and "third_next_quarter"
    for i in range(1, 4):
        quarter_month = (current_quarter + i) * 3
        quarter_year = year + (quarter_month - 1) // 12
        quarter_month = (quarter_month - 1) % 12 + 1
        expiration_dates[f"quarter_{i}"] = last_friday(quarter_year, quarter_month)

    return expiration_dates


def roll_over_expiration_dates(expiration_dates, current_date):
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
                next_month_year = expiration_date.year + (1 if next_month == 1 else 0)
                rolled_expirations[key] = last_friday(next_month_year, next_month)
            # If it's a quarterly expiration, move to the next quarter's last Friday
            elif key == "current_quarter":
                next_quarter_month = (expiration_date.month + 2) // 3 * 3 + 3
                next_quarter_year = expiration_date.year + (
                    1 if next_quarter_month > 12 else 0
                )
                next_quarter_month = next_quarter_month % 12 or 12
                rolled_expirations[key] = last_friday(
                    next_quarter_year, next_quarter_month
                )
            else:
                rolled_expirations[key] = expiration_date
        else:
            rolled_expirations[key] = expiration_date
    return rolled_expirations


def format_instrument_names(expiration_dates, symbols=["BTC", "ETH"]):
    instruments = {}
    for period, date in expiration_dates.items():
        # Use `%-d` for day without leading zero, `%b` for abbreviated month, and `%y` for two-digit year
        instrument_names = {
            symbol: f"{symbol}-{date.strftime('%-d%b%y').upper()}" for symbol in symbols
        }
        instruments[period] = instrument_names

    # Add perpetual futures for BTC and ETH
    instruments["perpetual"] = {symbol: f"{symbol}-PERPETUAL" for symbol in symbols}

    return instruments
