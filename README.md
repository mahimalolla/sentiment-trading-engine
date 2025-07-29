# Sentiment Trading Engine

# Sentiment-Based Long/Short Trading Tool

This project is a lightweight rule-based trading system that uses recent news sentiment to determine whether to go long or short on a stock. It scrapes public news-like content (currently via Twitter as a proxy), analyzes it using keyword sentiment, and makes investment decisions based on simple heuristics.

---

## Problem Statement

Retail investors often lack access to real-time, interpretable tools that can convert public market sentiment into actionable trades. This project addresses that gap by developing a simple engine that:

- Scrapes recent news content related to a specific stock
- Counts positive and negative financial keywords
- Makes a trading decision: go long (buy), short (sell), or hold
- Sizes positions based on sentiment strength and capital (AUM)

---

##  How It Works

### Inputs:
- `ticker` (e.g. AAPL)
- `date` (reference date, e.g. 2025-07-28)
- Configurable: lookback window and default AUM

### Steps:

1. Scrape tweets mentioning the stock using `snscrape` over the lookback window.
2. Clean and parse each tweet.
3. Count how many positive and negative sentiment keywords appear.
4. Aggregate sentiment across all scraped content.
5. Determine whether to go long, short, or hold based on scores.
6. Simulate investment using AUM and sentiment ratio.

---

## Project Structure

sentiment_trader/
│
├── config.py # Keyword lists, lookback window, AUM, paths
├── analyze.py # Main execution script
│
├── scripts/
│ ├── init.py
│ ├── sentiment_utils.py # Word counting logic
│ └── scrape_news.py # Uses snscrape to fetch tweets

 Future Enhancements
- Add scraping from earnings call transcripts or news APIs

- Visualize sentiment with word clouds or plots

- Deploy as a Streamlit dashboard or API

- Incorporate more advanced NLP (e.g. FinBERT, VADER)

