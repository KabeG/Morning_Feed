"""
fetch_news.py — Step 3: Pull latest headlines from configured RSS sources,
scoped to specific categories, and apply keyword exclusion filtering.
"""

import feedparser
import logging
import difflib

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Source configuration ---
# Each source has one feed URL per category. Add/remove categories here as needed.
SOURCE_FEEDS = {
    "BBC News": {
        "World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "Politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    },
    "NPR": {
        "World": "https://feeds.npr.org/1004/rss.xml",
        "Politics": "https://feeds.npr.org/1014/rss.xml",
        "Business": "https://feeds.npr.org/1006/rss.xml",
    },
    "News24": {
        "World": "https://feeds.capi24.com/v1/Search/articles/News24/World/rss",
        "Politics": "https://feeds.capi24.com/v1/Search/articles/News24/Politics/rss",
        "Business": "https://feeds.capi24.com/v1/Search/articles/fin24/news/rss",
    },
}

# Which categories to actually pull. Remove one to drop it entirely (e.g. remove
# "Business" to stop pulling business news from all three sources at once).
ACTIVE_CATEGORIES = ["World", "Politics", "Business"]

# Case-insensitive keyword exclude list. Any article whose title contains one of
# these (as a whole word) is dropped before it ever reaches the digest.
EXCLUDE_KEYWORDS = [
    "sport", "rugby", "cricket", "soccer", "football", "tennis", "golf",
    "celebrity", "gossip", "royal family", "kardashian",
]

ARTICLES_PER_FEED = 3


def _is_excluded(title: str) -> bool:
    """Check a title against EXCLUDE_KEYWORDS, case-insensitive."""
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in EXCLUDE_KEYWORDS)


def fetch_feed(name: str, category: str, url: str, limit: int = ARTICLES_PER_FEED) -> list[dict]:
    """Fetch and parse a single RSS feed for one source+category. Returns [] on
    failure rather than raising, so one broken feed doesn't take down the whole run."""
    try:
        feed = feedparser.parse(url)

        # feedparser doesn't raise on HTTP errors — it just returns an empty/partial
        # feed and sets bozo=1. Check explicitly so we log real failures.
        if feed.bozo and not feed.entries:
            logger.warning(f"[{name}/{category}] Feed error: {feed.bozo_exception}")
            return []

        articles = []
        excluded_count = 0
        for entry in feed.entries:
            title = entry.get("title", "").strip()

            if _is_excluded(title):
                excluded_count += 1
                continue

            articles.append({
                "source": name,
                "category": category,
                "title": title,
                "summary": entry.get("summary", "").strip(),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })

            if len(articles) >= limit:
                break

        logger.info(
            f"[{name}/{category}] Fetched {len(articles)} articles"
            + (f" ({excluded_count} filtered out)" if excluded_count else "")
        )
        return articles

    except Exception as e:
        logger.warning(f"[{name}/{category}] Failed to fetch: {e}")
        return []


def deduplicate_articles(articles: list[dict], similarity_threshold: float = 0.6) -> list[dict]:
    """Collapse near-identical headlines covered by multiple sources/categories
    (e.g. the same tariff story appearing in BBC World, BBC Business, and NPR).
    Keeps the first occurrence and merges the other sources into 'also_covered_by'."""
    kept: list[dict] = []

    for article in articles:
        title_norm = article["title"].lower().strip()
        duplicate_of = None

        for existing in kept:
            existing_norm = existing["title"].lower().strip()
            ratio = difflib.SequenceMatcher(None, title_norm, existing_norm).ratio()
            if ratio >= similarity_threshold:
                duplicate_of = existing
                break

        if duplicate_of:
            duplicate_of.setdefault("also_covered_by", []).append(article["source"])
        else:
            kept.append(article)

    removed = len(articles) - len(kept)
    if removed:
        logger.info(f"Deduplication: collapsed {removed} near-duplicate headlines")

    return kept


def fetch_all_sources() -> list[dict]:
    """Fetch articles across every active category for every configured source,
    then deduplicate near-identical headlines across sources/categories."""
    all_articles = []
    for source_name, category_feeds in SOURCE_FEEDS.items():
        for category in ACTIVE_CATEGORIES:
            url = category_feeds.get(category)
            if not url:
                continue
            all_articles.extend(fetch_feed(source_name, category, url))

    return deduplicate_articles(all_articles)


if __name__ == "__main__":
    # Quick manual test: run this file directly to sanity-check the feeds.
    articles = fetch_all_sources()
    print(f"\nTotal articles fetched: {len(articles)}\n")
    for a in articles:
        print(f"[{a['source']}/{a['category']}] {a['title']}")
