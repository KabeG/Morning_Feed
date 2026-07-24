"""
main.py — Step 6: Orchestrate the full run — fetch, summarize, send.
This is the single entry point GitHub Actions will call each morning.
"""

import logging
import sys

from fetch_news import fetch_all_sources
from summarize import build_digest
from send_telegram import send_message, format_digest_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run():
    logger.info("Starting morning news run...")

    articles = fetch_all_sources()
    if not articles:
        logger.warning("No articles fetched from any source.")

    digest = build_digest(articles)
    message = format_digest_message(digest)

    success = send_message(message)

    if not success:
        logger.error("Run completed but Telegram delivery failed.")
        sys.exit(1)  # non-zero exit so GitHub Actions flags the run as failed

    logger.info("Run completed successfully.")


if __name__ == "__main__":
    run()
