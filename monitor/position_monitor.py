import os
import json
import time
from dotenv import load_dotenv
from binance.client import Client
from tabulate import tabulate

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Load coin configuration
with open("config/coins.json") as f:
    COINS_CONFIG = json.load(f)
    COIN_ORDER = list(COINS_CONFIG.keys())

def colorize(value, threshold=0):
    try:
        value = float(value)
        if value > threshold:
            return f"\033[92m{value:+.2f}%\033[0m"
        elif value < -threshold:
            return f"\033[91m{value:+.2f}%\033[0m"
        else:
            return f"\033[93m{value:+.2f}%\033[0m"
    except:
        return value

def color_distance_pct(pct):
    if pct < 1:
        return f"\033[91m{pct:.2f}%\033[0m"  # red: <1% to SL
    elif pct < 3:
        return f"\033[93m{pct:.2f}%\033[0m"  # yellow: <3%
    else:
        return f"\033[92m{pct:.2f}%\033[0m"  # green

def get_wallet_balance():
    balances = client.futures_account_balance()
    for b in balances:
        if b["asset"] == "USDT":
            wallet_balance = float(b["balance"])
            unrealized = float(b.get("crossUnPnl", 0))
            return wallet_balance, unrealized
    return 0.0, 0.0

def get_stop_loss_for_symbol(symbol):
    try:
        orders = client.futures_get_open_orders(symbol=symbol)
        for o in orders:
            if o["type"] in ("STOP_MARKET", "STOP") and o.get("reduceOnly"):
                return float(o["stopPrice"])
    except:
        pass
    return None

def fetch_open_positions():
    positions = client.futures_position_information()
    filtered = []
    wallet_balance, _ = get_wallet_balance()

    for pos in positions:
        symbol = pos["symbol"]
        if symbol not in COINS_CONFIG:
            continue

        position_amt = float(pos["positionAmt"])
        if position_amt == 0:
            continue

        entry_price = float(pos["entryPrice"])
        mark_price = float(pos["markPrice"])
        notional = abs(float(pos["notional"]))
        margin_used = float(pos.get("positionInitialMargin", 0)) or 1e-6  # avoid div by zero

        leverage = notional / margin_used
        side = "LONG" if position_amt > 0 else "SHORT"
        position_size = notional
        pnl = float(pos.get("unRealizedProfit", 0))
        pnl_pct = (pnl / margin_used) * 100

        sl_percent = COINS_CONFIG[symbol]["sl_percent"]
        if side == "LONG":
            sl_price = entry_price * (1 - sl_percent / 100)
            pct_to_sl = ((mark_price - sl_price) / sl_price) * 100
        else:
            sl_price = entry_price * (1 + sl_percent / 100)
            pct_to_sl = ((sl_price - mark_price) / sl_price) * 100

        actual_sl = get_stop_loss_for_symbol(symbol)
        actual_sl_str = f"{actual_sl:.5f}" if actual_sl else "-"

        filtered.append([
            symbol,
            side,
            round(entry_price, 5),
            round(mark_price, 5),
            round(margin_used, 2),
            round(position_size, 2),
            round(pnl, 2),
            colorize(pnl_pct),
            f"{(margin_used / wallet_balance) * 100:.2f}%",
            actual_sl_str,
            color_distance_pct(pct_to_sl)
        ])

    filtered.sort(key=lambda row: COIN_ORDER.index(row[0]) if row[0] in COIN_ORDER else 999)
    return filtered


def display_table():
    table = fetch_open_positions()
    wallet, unrealized = get_wallet_balance()

    print(f"\n💰 Wallet Balance: ${wallet:,.2f}")
    print(f"📊 Total Unrealized PnL: {round(unrealized, 2):,.2f}\n")

    headers = [
        "Symbol", "Side", "Entry", "Mark",
        "Used Margin (USD)", "Position Size (USD)",
        "PnL", "PnL%", "Risk%", "SL Price", "% to SL"
    ]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid", numalign="right", stralign="left"))


def main():
    os.system("cls" if os.name == "nt" else "clear")
    display_table()

if __name__ == "__main__":
    main()
