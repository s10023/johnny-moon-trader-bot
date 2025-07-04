import os
import json
from dotenv import load_dotenv
from binance.client import Client
from tabulate import tabulate

# Load .env variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# Load coin config
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


def color_sl_size(pct):
    if pct < 2:
        return f"\033[91m{pct:.2f}%\033[0m"
    elif pct < 3.5:
        return f"\033[93m{pct:.2f}%\033[0m"
    else:
        return f"\033[92m{pct:.2f}%\033[0m"


def color_risk_usd(value, total_balance):
    pct = (value / total_balance * 100) if total_balance else 0
    formatted = f"${value:,.2f} ({pct:.2f}%)"
    if pct >= 50:
        return f"\033[91m{formatted}\033[0m"
    elif pct >= 30:
        return f"\033[93m{formatted}\033[0m"
    else:
        return f"\033[92m{formatted}\033[0m"


def get_wallet_balance():
    balances = client.futures_account_balance()
    for b in balances:
        if b["asset"] == "USDT":
            balance = float(b["balance"])
            unrealized = float(b.get("crossUnPnl", 0))
            return balance, unrealized
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
    total_risk_usd = 0.0

    for pos in positions:
        symbol = pos["symbol"]
        if symbol not in COINS_CONFIG:
            continue

        amt = float(pos["positionAmt"])
        if amt == 0:
            continue

        entry = float(pos["entryPrice"])
        mark = float(pos["markPrice"])
        notional = abs(float(pos["notional"]))
        margin = float(pos.get("positionInitialMargin", 0)) or 1e-6

        side = "LONG" if amt > 0 else "SHORT"
        pnl = float(pos.get("unRealizedProfit", 0))
        pnl_pct = (pnl / margin) * 100
        leverage = round(notional / margin)

        # SL logic
        sl_percent = COINS_CONFIG[symbol]["sl_percent"]
        if side == "LONG":
            sl_price = entry * (1 - sl_percent / 100)
            distance_pct = ((mark - sl_price) / sl_price) * 100
        else:
            sl_price = entry * (1 + sl_percent / 100)
            distance_pct = ((sl_price - mark) / sl_price) * 100

        sl_risk_usd = notional * (sl_percent / 100)
        total_risk_usd += sl_risk_usd

        actual_sl = get_stop_loss_for_symbol(symbol)
        actual_sl_str = f"{actual_sl:.5f}" if actual_sl else "-"

        # Calculate actual % loss from entry to SL
        if actual_sl:
            if side == "SHORT":
                pct_sl_size = ((entry - actual_sl) / entry) * 100
            else:  # SHORT
                pct_sl_size = ((actual_sl - entry) / entry) * 100
            sl_size_str = colorize(pct_sl_size)
        else:
            pct_sl_size = None
            sl_size_str = "-"

        filtered.append(
            [
                symbol,
                side,
                round(entry, 5),
                round(mark, 5),
                leverage,
                round(margin, 2),
                round(notional, 2),
                round(pnl, 2),
                colorize(pnl_pct),
                f"{(margin / wallet_balance) * 100:.2f}%",
                actual_sl_str,
                sl_size_str,
            ]
        )

    filtered.sort(
        key=lambda row: COIN_ORDER.index(row[0]) if row[0] in COIN_ORDER else 999
    )
    return filtered, total_risk_usd


def display_table():
    table, total_risk_usd = fetch_open_positions()
    wallet, unrealized = get_wallet_balance()
    total = wallet + unrealized

    print(f"\n💰 Wallet Balance: ${wallet:,.2f}")
    print(f"📊 Total Unrealized PnL: {unrealized:,.2f}")
    print(f"🧾 Wallet w/ Unrealized: ${total:,.2f}")
    print(f"⚠️ Total SL Risk: {color_risk_usd(total_risk_usd, total)}\n")

    headers = [
        "Symbol",
        "Side",
        "Entry",
        "Mark",
        "Lev",
        "Used Margin (USD)",
        "Position Size (USD)",
        "PnL",
        "PnL%",
        "Risk%",
        "SL Price",
        "% to SL",
    ]

    print(
        tabulate(
            table,
            headers=headers,
            tablefmt="fancy_grid",
            numalign="right",
            stralign="left",
        )
    )


def main():
    os.system("cls" if os.name == "nt" else "clear")
    display_table()


if __name__ == "__main__":
    main()
