"""
send_telegram.py — Step 5: Deliver the digest to Telegram.
"""

import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


def send_message(text: str) -> bool:
    """Send a message via the Telegram Bot API. Returns True on success."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"

    # Telegram messages cap at 4096 chars — truncate defensively so a send
    # never silently fails on a long digest.
    if len(text) > 4000:
        text = text[:3990] + "\n\n[...truncated]"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        logger.info("Telegram message sent successfully")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def format_digest_message(digest: str) -> str:
    """Wrap the raw digest with a date header."""
    today = datetime.now().strftime("%A, %d %B %Y")
    return f"Morning News Rundown — {today}\n\n{digest}"
