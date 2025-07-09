import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import telegram
import requests
from unittest.mock import patch


def test_echo_message():
    assert telegram.echo_message("hello") == "hello"


@patch("utils.telegram.requests.post")
def test_send_telegram_message_mocked(mock_post):
    # Should not raise or log error if bot_token and chat_id are provided
    telegram.send_telegram_message("test", bot_token="token", chat_id="chat")
    mock_post.assert_called_once()


@patch("utils.telegram.requests.post")
def test_send_telegram_message_no_config_logs_error(mock_post, caplog):
    # Should log error if no config is provided
    telegram.send_telegram_message("test", bot_token=None, chat_id=None)
    assert any(
        "Telegram not configured properly." in m for m in caplog.text.splitlines()
    )
