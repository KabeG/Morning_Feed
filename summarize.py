"""
summarize.py — Step 4: Turn raw articles into a short, neutral morning digest
using an LLM call (Groq, same pattern as the watchlist agent).
"""

import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

MODEL = "llama-3.3-70b-versatile"  # adjust to whichever Groq model you used before

SYSTEM_PROMPT = """You are a neutral news digest writer. You will be given a list \
of article headlines and short snippets from several sources. Produce a concise \
morning rundown for a phone message.

Rules:
- Group items by topic, not by source, unless a topic is single-source
- One to two neutral sentences per story — no editorializing, no speculation
- Skip near-duplicate stories covered by multiple sources; mention once, note \
if it's from multiple outlets
- Keep the whole digest readable in under a minute
- Plain text only — no markdown headers, just clear line breaks and light structure
- Start directly with the content, no greeting or preamble
"""


def build_digest(articles: list[dict]) -> str:
    """Send fetched articles to the LLM and return a formatted digest string."""
    if not articles:
        return "No articles were retrieved this morning — all sources may be unreachable."

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    # Keep the prompt compact: title + snippet + source per article
    article_lines = []
    for a in articles:
        snippet = a["summary"][:200] if a["summary"] else ""
        category = a.get("category", "")
        article_lines.append(f"- ({a['source']}, {category}) {a['title']}: {snippet}")

    user_prompt = "Articles:\n" + "\n".join(article_lines)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        # Fallback: raw headline list so the run still produces something useful
        fallback = "\n".join(f"- [{a['source']}] {a['title']}" for a in articles)
        return f"(Summary generation failed — raw headlines below)\n\n{fallback}"
