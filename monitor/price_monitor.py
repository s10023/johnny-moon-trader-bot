import argparse
import time
import os
import json
import datetime as dt
import pytz
from binance.client import Client
from dotenv import load_dotenv
from tabulate import tabulate
from colorama import init, Fore, Style

# Init colorama
init(autoreset=True)

# Load environment
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Load symbols from config
with open("config/coins.json") as f:
    COINS = list(json.load(f).keys())


# Format % change with color
def format_pct(pct):
    try:
        pct = float(pct)
        if pct > 0:
            return Fore.GREEN + f"{pct:+.2f}%" + Style.RESET_ALL
        elif pct < 0:
            return Fore.RED + f"{pct:+.2f}%" + Style.RESET_ALL
        else:
            return Fore.YELLOW + f"{pct:+.2f}%" + Style.RESET_ALL
    except:
        return pct


# Convert datetime to Binance-compatible string
def get_klines(symbol, interval, lookback_minutes):
    now = dt.datetime.utcnow()
    start_time = int((now - dt.timedelta(minutes=lookback_minutes)).timestamp() * 1000)
    try:
        klines = client.get_klines(
            symbol=symbol, interval=interval, startTime=start_time
        )
        return klines[-1]  # most recent kline
    except:
        return None


def get_open_price_asia(symbol):
    now_utc = dt.datetime.utcnow().replace(tzinfo=pytz.utc)
    asia_tz = pytz.timezone("Asia/Shanghai")  # GMT+8
    asia_today_8am = now_utc.astimezone(asia_tz).replace(
        hour=8, minute=0, second=0, microsecond=0
    )
    if now_utc.astimezone(asia_tz) < asia_today_8am:
        asia_today_8am -= dt.timedelta(days=1)

    start_time = int(asia_today_8am.astimezone(pytz.utc).timestamp() * 1000)
    try:
        kline = client.get_klines(
            symbol=symbol, interval="1m", startTime=start_time, limit=1
        )
        return float(kline[0][1]) if kline else None  # open price
    except:
        return None


def get_price_changes(symbols):
    table = []

    # Get all tickers once (much faster)
    all_tickers = client.get_ticker()
    ticker_map = {t["symbol"]: t for t in all_tickers}

    for symbol in symbols:
        try:
            ticker = ticker_map.get(symbol)
            if not ticker:
                raise ValueError("Ticker not found")

            last_price = float(ticker["lastPrice"])
            change_24h = float(ticker["priceChangePercent"])

            # Still need individual klines
            k15 = get_klines(symbol, "15m", 15)
            k60 = get_klines(symbol, "1h", 60)
            open_15 = float(k15[1]) if k15 else last_price
            open_60 = float(k60[1]) if k60 else last_price

            change_15m = ((last_price - open_15) / open_15) * 100 if open_15 else 0
            change_1h = ((last_price - open_60) / open_60) * 100 if open_60 else 0

            # Asia session open
            asia_open = get_open_price_asia(symbol)
            change_asia = (
                ((last_price - asia_open) / asia_open) * 100 if asia_open else 0
            )

            table.append(
                [
                    symbol,
                    round(last_price, 4),
                    format_pct(change_15m),
                    format_pct(change_1h),
                    format_pct(change_asia),
                    format_pct(change_24h),
                ]
            )
        except Exception:
            table.append([symbol, "Error", "", "", "", ""])
    return table


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main(once=False):
    if once:
        clear_screen()
        print("📈 Crypto Price Snapshot — Buibui Moon Bot\n")
        headers = ["Symbol", "Last Price", "15m %", "1h %", "Since Asia 8AM", "24h %"]
        price_table = get_price_changes(COINS)
        print(tabulate(price_table, headers=headers, tablefmt="fancy_grid"))
    else:
        while True:
            clear_screen()
            print("📈 Live Crypto Price Monitor — Buibui Moon Bot\n")
            headers = [
                "Symbol",
                "Last Price",
                "15m %",
                "1h %",
                "Since Asia 8AM",
                "24h %",
            ]
            price_table = get_price_changes(COINS)
            print(tabulate(price_table, headers=headers, tablefmt="fancy_grid"))
            time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buibui Moon Crypto Monitor")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    main(once=args.once)
