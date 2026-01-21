import os
import logging
logging.basicConfig(level=int(os.getenv("LEVEL", 20)))
import time
from opentelemetry import metrics
from pycoingecko import CoinGeckoAPI

def check_vars(**vars):
    for var_name, var_val in vars.items():
        if not var_val:
            logging.error(f"{var_name} required")
            exit(1)

API_KEY = os.getenv("COINGECKO_KEY")
TIMEOUT = int(os.getenv("TIMEOUT", 15))
CURRENCY = os.getenv("CURRENCY", "USD")
COINS = {}

for name, val in os.environ.items():
    if not name.startswith("COIN_"):
        continue
    if not name.endswith("_ID"):
        continue
    tag = name.split("_")[1]
    COINS[tag] = val

logging.info(f"loaded {len(COINS)} coins")

if not COINS:
    logging.warning("No coins to check, exiting...")
    exit(0)

api = CoinGeckoAPI(api_key=API_KEY, retries=0)
meter = metrics.get_meter_provider().get_meter("cryptotelemetry")

histograms = {}
for tag, name in COINS.items():
    histograms[name] = meter.create_gauge(name=tag, description=name, unit=CURRENCY)

while True: 
    try:
        prices: dict[str, dict[str, float]] = api.get_price(ids=','.join(COINS.values()), vs_currencies=CURRENCY)
        logging.info(prices)
        for name, details in prices.items():
            price = details.get(CURRENCY.lower(), 0.0)
            if histograms[name]:
                histograms[name].set(price)
            else:
                logging.debug(f"Unable to find {name} in histograms")
    except Exception as e:
        logging.error(f"Exception in loop: {e}",)
        time.sleep(60)
    time.sleep(TIMEOUT)