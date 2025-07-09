import argparse
import time
import os
import json
from binance.client import Client
from dotenv import load_dotenv
from tabulate import tabulate
import sys
from utils.telegram import send_telegram_message
from monitor import price_lib
from colorama import Fore, Style, init

init(autoreset=True)


def load_config():
    with open("config/coins.json") as f:
        return list(json.load(f).keys())


def get_client():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    return Client(api_key, api_secret)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def colorize_pct(pct_str):
    try:
        pct = float(pct_str.replace("%", "").replace("+", ""))
        if pct_str.startswith("+") or pct > 0:
            return Fore.GREEN + pct_str + Style.RESET_ALL
        elif pct < 0:
            return Fore.RED + pct_str + Style.RESET_ALL
        else:
            return Fore.YELLOW + pct_str + Style.RESET_ALL
    except Exception:
        return pct_str


def main(live=False, telegram=False):
    client = get_client()
    coins = load_config()
    if not live:
        clear_screen()
        print("📈 Crypto Price Snapshot — Buibui Moon Bot\n")
        headers = ["Symbol", "Last Price", "15m %", "1h %", "Since Asia 8AM", "24h %"]
        price_table, invalid_symbols = price_lib.get_price_changes(client, coins)
        # Colorize percentage columns for terminal output
        if not telegram:
            for row in price_table:
                for idx in [2, 3, 4, 5]:  # percentage columns
                    row[idx] = colorize_pct(str(row[idx]))
        print(tabulate(price_table, headers=headers, tablefmt="fancy_grid"))
        if invalid_symbols:
            print("\n⚠️  The following symbols had errors:")
            for symbol, reason in sorted(invalid_symbols):
                print(f"  - {symbol}: {reason}")
        if telegram:
            price_table, _ = price_lib.get_price_changes(client, coins, telegram=True)
            plain_table = tabulate(price_table, headers=headers, tablefmt="plain")
            try:
                send_telegram_message(
                    f"📈 Snapshot Price Monitor\n```\n{plain_table}\n```"
                )
            except Exception as e:
                print("❌ Telegram message failed:", e)
    else:
        try:
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
                price_table, invalid_symbols = price_lib.get_price_changes(
                    client, coins
                )
                for row in price_table:
                    for idx in [2, 3, 4, 5]:
                        row[idx] = colorize_pct(str(row[idx]))
                print(tabulate(price_table, headers=headers, tablefmt="fancy_grid"))
                if invalid_symbols:
                    print("\n⚠️  The following symbols had errors:")
                    for symbol, reason in sorted(invalid_symbols):
                        print(f"  - {symbol}: {reason}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nExiting gracefully. Goodbye!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buibui Moon Crypto Monitor")
    parser.add_argument("--live", action="store_true", help="Run in live refresh mode")
    parser.add_argument(
        "--telegram", action="store_true", help="Send output to Telegram"
    )
    args = parser.parse_args()
    main(live=args.live, telegram=args.telegram)
