import os
import json
from binance.client import Client
from dotenv import load_dotenv
from tabulate import tabulate
import argparse
from utils.telegram import send_telegram_message
from monitor import position_lib


def load_config():
    with open("config/coins.json") as f:
        coins_config = json.load(f)
        coin_order = list(coins_config.keys())
    return coins_config, coin_order


def get_client():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    return Client(api_key, api_secret)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def display_table(
    client,
    coins_config,
    coin_order,
    sort_by="default",
    descending=True,
    telegram=False,
    wallet_target=0.0,
):
    table, total_risk_usd = position_lib.fetch_open_positions(
        client, coins_config, coin_order, sort_by, descending
    )
    wallet, unrealized = position_lib.get_wallet_balance(client)
    total = wallet + unrealized
    unrealized_pct = (unrealized / wallet * 100) if wallet else 0
    used_margin = sum(
        float(row[5]) for row in table if isinstance(row[5], (int, float))
    )
    available_balance = total - used_margin
    print(f"\n💰 Wallet Balance: ${wallet:,.2f}")
    print(f"💼 Available Balance: ${available_balance:,.2f}")
    print(
        f"📊 Total Unrealized PnL: {position_lib.colorize_dollar(unrealized)} ({position_lib.colorize(unrealized_pct)} of wallet)"
    )
    print(f"🧾 Wallet w/ Unrealized: ${total:,.2f}")
    print(f"⚠️ Total SL Risk: {position_lib.color_risk_usd(total_risk_usd, wallet)}\n")
    if wallet_target > 0:
        pct = min(max(total / wallet_target, 0), 1)
        filled = int(30 * pct)
        empty = 30 - filled
        bar = "█" * filled + "-" * empty
        print(
            f"Wallet Target: ${total:,.2f} / ${wallet_target:,.2f} |{bar}| {pct*100:.1f}%"
        )
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
    if telegram:
        summary = (
            f"📌 Open Positions Snapshot\n\n"
            f"💰 Wallet Balance: ${wallet:,.2f}\n"
            f"💼 Available Balance: ${available_balance:,.2f}\n"
            f"📊 Unrealized PnL: {unrealized:+.2f} ({unrealized_pct:+.2f}%)\n"
            f"🧾 Wallet + PnL: ${total:,.2f}\n"
            f"⚠️ SL Risk: ${total_risk_usd:,.2f}"
        )
        try:
            send_telegram_message(summary)
        except Exception as e:
            print(f"❌ Telegram message failed: {e}")


def main(sort="default", telegram=False):
    client = get_client()
    coins_config, coin_order = load_config()
    wallet_target = float(os.getenv("WALLET_TARGET", 0))
    clear_screen()
    sort_key, _, sort_dir = sort.partition(":")
    sort_order = sort_dir.lower() != "asc"  # default to descending if not asc
    display_table(
        client,
        coins_config,
        coin_order,
        sort_by=sort_key,
        descending=sort_order,
        telegram=telegram,
        wallet_target=wallet_target,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort",
        default="default",
        help="Sort order, e.g., 'pnl_pct:desc', 'sl_usd:asc', or 'default'",
    )
    parser.add_argument(
        "--telegram", action="store_true", help="Send output to Telegram"
    )
    args = parser.parse_args()
    main(sort=args.sort, telegram=args.telegram)
