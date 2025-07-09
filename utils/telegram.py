import os
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

load_dotenv()


def get_telegram_config():
    """Load Telegram bot token and chat id from environment variables."""
    return {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
    }


def send_telegram_message(text, bot_token=None, chat_id=None):
    """
    Send a message to a Telegram chat. Optionally provide bot_token and chat_id for testability.
    If not provided, loads from environment variables.
    """
    if bot_token is None or chat_id is None:
        config = get_telegram_config()
        bot_token = bot_token or config["bot_token"]
        chat_id = chat_id or config["chat_id"]
    if not bot_token or not chat_id:
        logging.error("Telegram not configured properly.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")


def echo_message(text):
    """Return the text. Used for testing purposes."""
    return text
