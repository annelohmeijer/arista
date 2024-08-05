from arista.coinglass import CoinglassAPI
from arista.models.funding_rate import FundingRate, FundingRateRepository

EXCHANGE = "Binance"
INTERVAL = "4h"

# get data from Coinglass API
client = CoinglassAPI()
exchange = "Binance"
symbol = "BTCUSDT"
interval = "4h"

funding_rates = client.get_funding_rate(
    exchange=exchange, symbol=symbol, interval=interval
)

rates_dict = [
    v | {"exchange": exchange, "symbol": symbol, "interval": interval}
    for v in funding_rate
]

rates = [FundingRate(**v) for v in rates_dict]

r = FundingRateRepository()
max_ = r.max_timestamp()


data_to_insert = [v for v in rates if v.t > max_]

r.bulk_create(rates_dict)
