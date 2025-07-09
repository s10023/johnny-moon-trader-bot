import datetime as dt
import pytz
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


# Format % change with color (no color for testability)
def format_pct(pct):
    try:
        pct = float(pct)
        return f"{pct:+.2f}%"
    except Exception as e:
        logging.error(f"Error in format_pct: {e}")
        return pct


def format_pct_simple(pct):
    try:
        return f"{float(pct):+.2f}%"
    except Exception as e:
        logging.error(f"Error in format_pct_simple: {e}")
        return pct


def get_klines(client, symbol, interval, lookback_minutes):
    now = dt.datetime.utcnow()
    start_time = int((now - dt.timedelta(minutes=lookback_minutes)).timestamp() * 1000)
    try:
        klines = client.get_klines(
            symbol=symbol, interval=interval, startTime=start_time
        )
        return klines[-1]  # most recent kline
    except Exception as e:
        logging.error(f"Error in get_klines for {symbol} [{interval}]: {e}")
        return None


def batch_get_klines(client, symbols, intervals_lookbacks):
    results = {}

    def fetch(symbol, interval, lookback):
        now = dt.datetime.utcnow()
        start_time = int((now - dt.timedelta(minutes=lookback)).timestamp() * 1000)
        try:
            klines = client.get_klines(
                symbol=symbol, interval=interval, startTime=start_time
            )
            return ((symbol, interval), klines[-1] if klines else None)
        except Exception as e:
            logging.error(f"Error in batch_get_klines for {symbol} [{interval}]: {e}")
            return ((symbol, interval), None)

    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch, symbol, interval, lookback)
            for symbol in symbols
            for interval, lookback in intervals_lookbacks
        ]
        for future in as_completed(futures):
            key, kline = future.result()
            results[key] = kline
    return results


def get_open_price_asia(client, symbol):
    now_utc = dt.datetime.utcnow().replace(tzinfo=pytz.utc)
    asia_tz = pytz.timezone("Asia/Shanghai")
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
        return float(kline[0][1]) if kline else None
    except Exception as e:
        logging.error(f"Error in get_open_price_asia for {symbol}: {e}")
        return None


def get_price_changes(client, symbols, telegram=False):
    table = []
    invalid_symbols = set()
    try:
        all_tickers = client.get_ticker()
        ticker_map = {t["symbol"]: t for t in all_tickers}
    except Exception as e:
        logging.error(f"Error fetching all tickers: {e}")
        return [[symbol, "Error", "", "", "", ""] for symbol in symbols], set()
    intervals_lookbacks = [("15m", 15), ("1h", 60)]
    kline_map = batch_get_klines(client, symbols, intervals_lookbacks)

    def get_asia_open_parallel(symbols):
        results = {}

        def fetch(symbol):
            return (symbol, get_open_price_asia(client, symbol))

        max_workers = 4
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch, symbol) for symbol in symbols]
            for future in as_completed(futures):
                symbol, asia_open = future.result()
                results[symbol] = asia_open
        return results

    asia_open_map = get_asia_open_parallel(symbols)
    for symbol in symbols:
        try:
            ticker = ticker_map.get(symbol)
            if not ticker:
                invalid_symbols.add((symbol, "Ticker not found"))
                table.append([symbol, "Error", "", "", "", ""])
                continue
            last_price = float(ticker["lastPrice"])
            change_24h = float(ticker["priceChangePercent"])
            k15 = kline_map.get((symbol, "15m"))
            k60 = kline_map.get((symbol, "1h"))
            open_15 = float(k15[1]) if k15 else last_price
            open_60 = float(k60[1]) if k60 else last_price
            change_15m = ((last_price - open_15) / open_15) * 100 if open_15 else 0
            change_1h = ((last_price - open_60) / open_60) * 100 if open_60 else 0
            asia_open = asia_open_map.get(symbol)
            change_asia = (
                ((last_price - asia_open) / asia_open) * 100 if asia_open else 0
            )
            if telegram:
                table.append(
                    [
                        symbol,
                        round(last_price, 4),
                        format_pct_simple(change_15m),
                        format_pct_simple(change_1h),
                        format_pct_simple(change_asia),
                        format_pct_simple(change_24h),
                    ]
                )
            else:
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
        except Exception as e:
            msg = str(e)
            if "Invalid symbol" in msg:
                invalid_symbols.add((symbol, "Invalid symbol"))
            else:
                invalid_symbols.add((symbol, msg))
            table.append([symbol, "Error", "", "", "", ""])
    return table, invalid_symbols
