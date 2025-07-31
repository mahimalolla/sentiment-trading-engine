import requests
from datetime import datetime
from config import NEWSAPI_KEY

def scrape_articles_for_ticker(ticker, start_date, end_date, max_results=50):
    """
    Fetches recent news headlines and descriptions for a stock ticker using NewsAPI.
    Returns:
        - texts: list of combined title + description strings
        - sources: list of source names (e.g., CNBC, Reuters)
    """
    url = "https://newsapi.org/v2/everything"
    query = f'"{ticker}"'

    params = {
        "q": query,
        "from": start_date.strftime('%Y-%m-%d'),
        "to": end_date.strftime('%Y-%m-%d'),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_results,
        "apiKey": NEWSAPI_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "articles" not in data:
        print("[ERROR] NewsAPI response error:", data)
        return [], []

    texts = []
    sources = []

    for article in data["articles"]:
        text = article.get("title", "") + " " + (article.get("description") or "")
        source = article["source"]["name"]
        texts.append(text)
        sources.append(source)

    return texts, sources
