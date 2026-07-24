# Morning News Agent

Fetches headlines from BBC News, NPR, and News24, summarizes them into a neutral
digest, and sends it to Telegram every morning at 9:00 AM SAST.

## Files
- `fetch_news.py` — pulls and parses RSS feeds
- `summarize.py` — LLM summarization step (Groq)
- `send_telegram.py` — Telegram delivery
- `main.py` — orchestrates the full run
- `.github/workflows/morning-news.yml` — daily automation

## Setup

### 1. Create your Telegram bot
1. Message **@BotFather** on Telegram → send `/newbot` → follow the prompts
2. Save the token it gives you
3. Send your new bot any message (so it can see your chat)
4. Get your chat ID by visiting:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   — look for `"chat":{"id": ...}` in the response

### 2. Get a Groq API key
Sign up at console.groq.com and generate an API key (same one used for the
watchlist agent, if you still have it).

### 3. Local test
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export GROQ_API_KEY="..."
python main.py
```
You should get a Telegram message within a few seconds.

### 4. Push to GitHub
1. Create a new repo (private or public)
2. Push all these files, including the `.github/workflows/` folder
3. Go to **Settings → Secrets and variables → Actions** and add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GROQ_API_KEY`

### 5. Test the automation
Go to the **Actions** tab → select "Morning News Rundown" → **Run workflow**
(manual trigger via `workflow_dispatch`). Confirm the Telegram message arrives.

### 6. Let it run
Once confirmed working, it will fire automatically every day at 7:00 AM UTC
(9:00 AM SAST). No further action needed.

**Note:** if the repo is private, GitHub pauses scheduled Actions after 60 days
with no commits — any small commit resets that clock.

## Tuning
- `ARTICLES_PER_FEED` in `fetch_news.py` — how many stories to pull per source/category
- `ACTIVE_CATEGORIES` in `fetch_news.py` — which categories to pull (World, Politics, Business by default). Remove one to drop it across all sources at once.
- `EXCLUDE_KEYWORDS` in `fetch_news.py` — case-insensitive keyword blocklist checked against article titles (e.g. sport, celebrity gossip). Add more terms as you notice unwanted stories slipping through.
- `SOURCE_FEEDS` in `fetch_news.py` — add/remove source+category RSS URLs
- `SYSTEM_PROMPT` in `summarize.py` — adjust tone/length of the digest
