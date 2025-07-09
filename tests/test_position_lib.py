import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitor import position_lib
from unittest.mock import MagicMock


def test_colorize():
    assert position_lib.colorize(5) == "+5.00%"
    assert position_lib.colorize(-2.5) == "-2.50%"
    assert position_lib.colorize(0) == "0.00%"


def test_colorize_dollar():
    assert position_lib.colorize_dollar(10) == "+$10.00"
    assert position_lib.colorize_dollar(-5) == "-$5.00"
    assert position_lib.colorize_dollar(0) == "$0.00"


def test_get_wallet_balance():
    mock_client = MagicMock()
    mock_client.futures_account_balance.return_value = [
        {"asset": "USDT", "balance": "100", "crossUnPnl": "5"}
    ]
    balance, unrealized = position_lib.get_wallet_balance(mock_client)
    assert balance == 100.0
    assert unrealized == 5.0


def test_fetch_open_positions_empty():
    mock_client = MagicMock()
    mock_client.futures_position_information.return_value = []
    coins_config = {"BTCUSDT": {"leverage": 10}}
    coin_order = ["BTCUSDT"]
    table, total_risk_usd = position_lib.fetch_open_positions(
        mock_client, coins_config, coin_order
    )
    assert table[0][0] == "BTCUSDT"
    assert table[0][1] == "-"
