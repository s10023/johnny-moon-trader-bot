import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


def colorize(value, threshold=0):
    try:
        value = float(value)
        if value > threshold:
            return f"+{value:.2f}%"
        elif value < -threshold:
            return f"{value:.2f}%"
        else:
            return f"{value:.2f}%"
    except Exception as e:
        logging.error(f"Error in colorize: {e}")
        return value


def colorize_dollar(value):
    try:
        value = float(value)
        if value > 0:
            return f"+${value:,.2f}"
        elif value < 0:
            return f"-${abs(value):,.2f}"
        else:
            return "$0.00"
    except Exception as e:
        logging.error(f"Error in colorize_dollar: {e}")
        return f"${value}"


def color_sl_size(pct):
    pct = float(pct)
    if pct < 2:
        return f"{pct:.2f}%"
    elif pct < 3.5:
        return f"{pct:.2f}%"
    else:
        return f"{pct:.2f}%"


def color_risk_usd(value, total_balance):
    pct = (value / total_balance * 100) if total_balance else 0
    formatted = f"${value:,.2f} ({pct:.2f}%)"
    return formatted


def get_wallet_balance(client):
    balances = client.futures_account_balance()
    for b in balances:
        if b["asset"] == "USDT":
            balance = float(b["balance"])
            unrealized = float(b.get("crossUnPnl", 0))
            return balance, unrealized
    return 0.0, 0.0


def get_stop_loss_for_symbol(client, symbol):
    try:
        orders = client.futures_get_open_orders(symbol=symbol)
        for o in orders:
            if o["type"] in ("STOP_MARKET", "STOP") and o.get("reduceOnly"):
                return float(o["stopPrice"])
    except Exception:
        pass
    return None


def fetch_open_positions(
    client, coins_config, coin_order, sort_by="default", descending=True
):
    positions = client.futures_position_information()
    filtered = []
    wallet_balance, _ = get_wallet_balance(client)
    total_risk_usd = 0.0
    open_positions = []
    for pos in positions:
        symbol = pos["symbol"]
        if symbol not in coins_config:
            continue
        amt = float(pos["positionAmt"])
        if amt == 0:
            continue
        entry = float(pos["entryPrice"])
        mark = float(pos["markPrice"])
        notional = abs(float(pos["notional"]))
        margin = float(pos.get("positionInitialMargin", 0)) or 1e-6
        side_text = "LONG" if amt > 0 else "SHORT"
        open_positions.append(
            (symbol, side_text, entry, mark, margin, notional, amt, pos)
        )

    def fetch_sl(symbol, side_text, entry, notional):
        try:
            actual_sl = get_stop_loss_for_symbol(client, symbol)
            if actual_sl:
                if side_text == "SHORT":
                    sl_percent = (entry - actual_sl) / entry * 100
                else:
                    sl_percent = (actual_sl - entry) / entry * 100
                sl_risk_usd = notional * (sl_percent / 100)
                sl_size_str = colorize(sl_percent)
                actual_sl_str = f"{actual_sl:.5f}"
                sl_usd_str = colorize_dollar(sl_risk_usd)
            else:
                sl_percent = None
                sl_risk_usd = 0.0
                actual_sl_str = "-"
                sl_size_str = "-"
                sl_usd_str = "-"
            return (
                symbol,
                actual_sl_str,
                sl_size_str,
                sl_usd_str,
                sl_risk_usd,
                sl_percent,
            )
        except Exception:
            return (symbol, "-", "-", "-", 0.0, None)

    sl_results = {}
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_sl, symbol, side_text, entry, notional)
            for (
                symbol,
                side_text,
                entry,
                mark,
                margin,
                notional,
                amt,
                pos,
            ) in open_positions
        ]
        for future in as_completed(futures):
            symbol, actual_sl_str, sl_size_str, sl_usd_str, sl_risk_usd, sl_percent = (
                future.result()
            )
            sl_results[symbol] = (
                actual_sl_str,
                sl_size_str,
                sl_usd_str,
                sl_risk_usd,
                sl_percent,
            )
    for symbol, side_text, entry, mark, margin, notional, amt, pos in open_positions:
        pnl = float(pos.get("unRealizedProfit", 0))
        pnl_pct = (pnl / margin) * 100
        leverage = round(notional / margin)
        actual_sl_str, sl_size_str, sl_usd_str, sl_risk_usd, sl_percent = (
            sl_results.get(symbol, ("-", "-", "-", 0.0, None))
        )
        if sl_risk_usd:
            total_risk_usd += sl_risk_usd
        row = [
            symbol,  # 0
            side_text,  # 1
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
        row.append(pnl_pct)  # index 13
        row.append(sl_risk_usd)  # index 14
        filtered.append(row)
    open_symbols = set(row[0] for row in filtered)
    missing_symbols = [s for s in coin_order if s not in open_symbols]
    for symbol in missing_symbols:
        leverage = coins_config[symbol]["leverage"]
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
    else:
        filtered.sort(
            key=lambda r: coin_order.index(r[0]) if r[0] in coin_order else 999
        )
    filtered = [row[:13] for row in filtered]
    return filtered, total_risk_usd
