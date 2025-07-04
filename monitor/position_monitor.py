import os
from dotenv import load_dotenv
from binance.client import Client
from tabulate import tabulate
from colorama import Fore, Style, init
import requests
import json

init(autoreset=True)
load_dotenv()

# Load Binance and Telegram keys
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

with open("config/coins.json") as f:
    COIN_ORDER = list(json.load(f).keys())

client = Client(API_KEY, API_SECRET)

def color_pnl(pnl):
    if pnl > 0:
        return Fore.GREEN + f"{pnl:.2f}" + Style.RESET_ALL
    elif pnl < 0:
        return Fore.RED + f"{pnl:.2f}" + Style.RESET_ALL
    else:
        return f"{pnl:.2f}"

def color_pnl_pct(pct):
    try:
        pct_value = float(pct)
    except:
        return pct
    if pct_value > 0:
        return Fore.GREEN + f"{pct_value:+.2f}%" + Style.RESET_ALL
    elif pct_value < 0:
        return Fore.RED + f"{pct_value:+.2f}%" + Style.RESET_ALL
    else:
        return f"{pct_value:+.2f}%"

def fetch_open_positions():
    positions = client.futures_account()['positions']
    account_balances = client.futures_account_balance()

    # Find USDT wallet info
    usdt_balance_info = next((item for item in account_balances if item['asset'] == 'USDT'), None)
    if not usdt_balance_info:
        raise Exception("USDT balance not found in account.")

    wallet_balance = float(usdt_balance_info['balance'])
    total_pnl = 0
    filtered = []

    for pos in positions:
        amt = float(pos['positionAmt'])
        if abs(amt) > 0:
            symbol = pos['symbol']
            entry_price = float(pos['entryPrice'])
            mark_price = float(client.futures_mark_price(symbol=symbol)['markPrice'])
            side = "LONG" if amt > 0 else "SHORT"
            qty = abs(amt)
            leverage = int(pos['leverage'])
            pnl = float(pos.get('unrealizedProfit', 0.0))
            total_pnl += pnl

            position_size = qty * mark_price  # Total notional value
            used_margin = position_size / leverage  # Capital at risk
            pnl_pct = (pnl / (qty * entry_price)) * 100 if entry_price > 0 else 0
            risk_pct = (used_margin / wallet_balance) * 100 if wallet_balance > 0 else 0

            filtered.append([
                symbol,
                side,
                round(entry_price, 2),
                round(mark_price, 2),
                round(used_margin, 2),
                round(position_size, 2),
                color_pnl(pnl),
                color_pnl_pct(pnl_pct),
                f"{risk_pct:.2f}%"
            ])

    # Sort filtered based on COIN_ORDER
    sorted_positions = sorted(
        filtered,
        key=lambda x: COIN_ORDER.index(x[0]) if x[0] in COIN_ORDER else float('inf')
    )

    return sorted_positions, wallet_balance, total_pnl

def display_table():
    positions, wallet_balance, total_pnl = fetch_open_positions()

    headers = [
        "Symbol", "Side", "Entry", "Mark",
        "Used Margin (USD)", "Position Size (USD)",
        "PnL", "PnL%", "Risk%"
    ]

    print(f"💰 Wallet Balance: ${wallet_balance:,.2f}")
    print(f"📊 Total Unrealized PnL: {color_pnl(total_pnl)}\n")
    print(tabulate(positions, headers=headers, tablefmt="fancy_grid"))
    return positions, wallet_balance

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    if not response.ok:
        print("❌ Failed to send Telegram message:", response.text)

def format_table_for_telegram(raw_table, wallet):
    msg = f"📊 *Position Update*\n\n💼 Wallet Balance: `${wallet:.2f}`\n\n"
    msg += "```\n" + raw_table + "\n```"
    return msg

def main():
    table, wallet = display_table()
    # if table:
    #     message = format_table_for_telegram(table, wallet)
    #     send_telegram_message(message)

if __name__ == "__main__":
    main()
