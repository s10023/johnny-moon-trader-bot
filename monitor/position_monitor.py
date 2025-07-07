import os
import json
from dotenv import load_dotenv
from binance.client import Client
from tabulate import tabulate
import argparse
import time


def sync_binance_time(client):
    server_time = client.get_server_time()["serverTime"]
    local_time = int(time.time() * 1000)
    client.TIME_OFFSET = server_time - local_time


# Load .env variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)
sync_binance_time(client)

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


def colorize_dollar(value):
    try:
        value = float(value)
        if value > 0:
            return f"\033[92m${value:,.2f}\033[0m"
        elif value < 0:
            return f"\033[91m-${abs(value):,.2f}\033[0m"
        else:
            return f"\033[93m$0.00\033[0m"
    except:
        return f"${value}"


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
    if pct < -50:
        return f"\033[91m{formatted}\033[0m"
    elif pct < -30:
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


def fetch_open_positions(sort_by="default", descending=True):
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

        side_text = "LONG" if amt > 0 else "SHORT"
        side_colored = (
            f"\033[92m{side_text}\033[0m" if amt > 0 else f"\033[91m{side_text}\033[0m"
        )

        pnl = float(pos.get("unRealizedProfit", 0))
        pnl_pct = (pnl / margin) * 100
        leverage = round(notional / margin)

        actual_sl = get_stop_loss_for_symbol(symbol)

        if actual_sl:
            if side_text == "SHORT":
                sl_percent = (entry - actual_sl) / entry * 100
            else:  # SHORT
                sl_percent = (actual_sl - entry) / entry * 100

            sl_risk_usd = notional * (sl_percent / 100)
            total_risk_usd += sl_risk_usd
            sl_size_str = colorize(sl_percent)
            actual_sl_str = f"{actual_sl:.5f}"
            sl_usd_str = colorize_dollar(sl_risk_usd)
        else:
            sl_percent = None
            sl_risk_usd = 0.0
            actual_sl_str = "-"
            sl_size_str = "-"
            sl_usd_str = "-"

        row = [
            symbol,  # 0
            side_colored,  # 1
            leverage,  # 2
            round(entry, 5),  # 3
            round(mark, 5),  # 4
            round(margin, 2),  # 5
            round(notional, 2),  # 6
            colorize_dollar(pnl),  # 7
            colorize(pnl_pct),  # 8
            f"{(margin / wallet_balance) * 100:.2f}%",  # 9
            actual_sl_str,  # 10
            sl_size_str,  # 11
            sl_usd_str,  # 12
        ]
        # Append extra values at the end for sorting (not shown)
        row.append(pnl_pct)  # index 13
        row.append(sl_risk_usd)  # index 14

        filtered.append(row)

    # Get coins without open positions
    open_symbols = set(row[0] for row in filtered)
    missing_symbols = [s for s in COIN_ORDER if s not in open_symbols]

    # Add placeholder rows for missing symbols
    for symbol in missing_symbols:
        leverage = COINS_CONFIG[symbol]["leverage"]
        row = [
            symbol,  # 0
            "-",  # side
            leverage,  # lev
            "-",
            "-",  # entry, mark
            "-",
            "-",  # margin, size
            "-",
            "-",  # pnl, pnl%
            "-",
            "-",
            "-",  # risk%, sl price, % to sl
            "-",  # sl usd
            -999,  # hidden sort: pnl_pct
            -9999,  # hidden sort: sl_usd
        ]
        filtered.append(row)

    if sort_by == "pnl_pct":
        filtered.sort(key=lambda r: r[13], reverse=descending)
    elif sort_by == "sl_usd":
        filtered.sort(key=lambda r: r[14], reverse=descending)
    else:  # default sort by COIN_ORDER
        filtered.sort(
            key=lambda r: COIN_ORDER.index(r[0]) if r[0] in COIN_ORDER else 999
        )

    # Remove hidden sort columns
    filtered = [row[:13] for row in filtered]

    return filtered, total_risk_usd


def display_table(sort_by="default", descending=True):
    table, total_risk_usd = fetch_open_positions(sort_by, descending)
    wallet, unrealized = get_wallet_balance()
    total = wallet + unrealized
    unrealized_pct = (unrealized / wallet * 100) if wallet else 0

    used_margin = sum(
        float(row[5]) for row in table if isinstance(row[5], (int, float))
    )
    available_balance = total - used_margin

    print(f"\n💰 Wallet Balance: ${wallet:,.2f}")
    print(f"💼 Available Balance: ${available_balance:,.2f}")
    print(
        f"📊 Total Unrealized PnL: {colorize_dollar(unrealized)} ({colorize(unrealized_pct)} of wallet)"
    )
    print(f"🧾 Wallet w/ Unrealized: ${total:,.2f}")
    print(f"⚠️ Total SL Risk: {color_risk_usd(total_risk_usd, wallet)}\n")

    headers = [
        "Symbol",
        "Side",
        "Lev",
        "Entry",
        "Mark",
        "Used Margin (USD)",
        "Position Size (USD)",
        "PnL",
        "PnL%",
        "Risk%",
        "SL Price",
        "% to SL",
        "SL USD",
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort",
        default="default",
        help="Sort order, e.g., 'pnl_pct:desc', 'sl_usd:asc', or 'default'",
    )
    args = parser.parse_args()
    sort_key, _, sort_dir = args.sort.partition(":")
    sort_order = sort_dir.lower() != "asc"  # default to descending if not asc

    os.system("cls" if os.name == "nt" else "clear")
    display_table(sort_by=sort_key, descending=sort_order)


if __name__ == "__main__":
    main()
