import os
import logging
logging.basicConfig(level=int(os.getenv("LEVEL", 20)))
import time
from opentelemetry import metrics
from opentelemetry.metrics import Histogram
from pycoingecko import CoinGeckoAPI

def check_vars(**vars):
    for var_name, var_val in vars.items():
        if not var_val:
            logging.error(f"{var_name} required")
            exit(1)


API_KEY = os.getenv("COINGECKO_KEY")
TIMEOUT = int(os.getenv("TIMEOUT", 15))
CURRENCY = os.getenv("CURRENCY", "USD")
COINS = {
    "LTC": "litecoin",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
}

api = CoinGeckoAPI(api_key=API_KEY, retries=0)
meter = metrics.get_meter_provider().get_meter("cryptotelemetry")

histograms: dict[str, Histogram] = {}
for tag, name in COINS.items():
    histograms[name] = meter.create_histogram(name=tag, description=name, unit=CURRENCY)

while True:
    prices = api.get_price(ids=','.join(COINS.values()), vs_currencies=CURRENCY)
    logging.info(prices)
    for name, details in prices.items():
        name: str
        price: int = details.get(CURRENCY.lower())
        if histograms[name]:
            histograms[name].record(price)
        else:
            logging.debug(f"Unable to find {name} in histograms")
    time.sleep(TIMEOUT)
    

