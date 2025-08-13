import requests
from typing import List, Dict

def fetch_newsapi_headlines(ticker: str, from_date: str, to_date: str, api_key: str, page_size: int = 50) -> List[Dict]:
    if not api_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{ticker} stock OR {ticker} earnings",
        "from": from_date,
        "to": to_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": min(page_size, 100)
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    articles = r.json().get("articles", [])
    items = []
    for a in articles:
        items.append({
            "title": a.get("title") or "",
            "description": a.get("description") or "",
            "content": a.get("content") or "",
            "url": a.get("url"),
            "source": (a.get("source") or {}).get("name", "") or "Unknown",
            "published_at": a.get("publishedAt", "")
        })
    return items
