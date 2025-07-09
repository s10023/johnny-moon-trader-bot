import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitor import price_lib
from unittest.mock import MagicMock


def test_format_pct():
    assert price_lib.format_pct(5) == "+5.00%"
    assert price_lib.format_pct(-2.5) == "-2.50%"
    assert price_lib.format_pct(0) == "+0.00%"


def test_format_pct_simple():
    assert price_lib.format_pct_simple(3.1415) == "+3.14%"
    assert price_lib.format_pct_simple(-1) == "-1.00%"


def test_get_klines_returns_last_kline():
    mock_client = MagicMock()
    mock_client.get_klines.return_value = [[1, 2, 3], [4, 5, 6]]
    result = price_lib.get_klines(mock_client, "BTCUSDT", "1m", 15)
    assert result == [4, 5, 6]


def test_get_price_changes_handles_invalid_symbol():
    mock_client = MagicMock()
    mock_client.get_ticker.return_value = [
        {"symbol": "BTCUSDT", "lastPrice": "100", "priceChangePercent": "5"}
    ]
    mock_client.get_klines.return_value = [[0, "100"]]
    table, invalid = price_lib.get_price_changes(mock_client, ["BTCUSDT", "FAKECOIN"])
    assert any(row[0] == "FAKECOIN" and row[1] == "Error" for row in table)
    assert ("FAKECOIN", "Ticker not found") in invalid
