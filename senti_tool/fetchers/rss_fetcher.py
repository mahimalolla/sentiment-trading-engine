import feedparser
from typing import List, Dict
from urllib.parse import quote

def fetch_rss_google_news(ticker: str) -> List[Dict]:
    q = quote(f"{ticker} stock OR {ticker} earnings")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    d = feedparser.parse(url)
    items = []
    for e in d.entries:
        items.append({
            "title": e.get("title", ""),
            "description": e.get("summary", ""),
            "content": "",
            "url": e.get("link", ""),
            "source": (getattr(e, "source", None) or {}).get("title", "") if hasattr(e, "source") else "Unknown",
            "published_at": e.get("published", "") or e.get("updated", "")
        })
    return items
