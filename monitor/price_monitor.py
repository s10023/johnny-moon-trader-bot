import time
import os
import json
from binance.client import Client
from dotenv import load_dotenv
from tabulate import tabulate

# Load .env for API keys
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Load coins from config
with open("config/coins.json") as f:
    COINS = list(json.load(f).keys())  # just the symbol names

def get_prices(symbols):
    prices = []
    for symbol in symbols:
        try:
            ticker = client.get_ticker(symbol=symbol)
            prices.append([
                symbol,
                round(float(ticker["lastPrice"]), 4),
                f'{float(ticker["priceChangePercent"]):+.2f}%',
                round(float(ticker["highPrice"]), 4),
                round(float(ticker["lowPrice"]), 4),
                round(float(ticker["quoteVolume"]), 2)
            ])
        except Exception as e:
            prices.append([symbol, "Error", "", "", "", ""])
    return prices

def main():
    while True:
        os.system("cls")  # use 'cls' if on Windows
        print("📈 Live Crypto Price Monitor — Johnny Moon Bot\n")

        price_table = get_prices(COINS)
        headers = ["Symbol", "Last Price", "24h %", "High", "Low", "Volume (USDT)"]
        print(tabulate(price_table, headers=headers, tablefmt="fancy_grid"))

        time.sleep(5)

if __name__ == "__main__":
    main()
