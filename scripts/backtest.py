#!/usr/bin/env python3
import argparse, os, json, time
from collections import defaultdict
import pandas as pd

from senti_tool.config import NEWSAPI_KEY
from senti_tool.utils import daterange
from scripts.analyze import load_json, load_aum_csv
from senti_tool.fetchers.newsapi_fetcher import fetch_newsapi_headlines
from senti_tool.fetchers.rss_fetcher import fetch_rss_google_news
from senti_tool.sentiment import KeywordSentiment
from senti_tool.sizing import direction_from_ratio, position_dollars

def maybe_fetch_prices(tickers, start, end):
    try:
        import yfinance as yf
        df = yf.download(tickers=tickers, start=start, end=end, progress=False)["Adj Close"]
        if isinstance(df, pd.Series):
            df = df.to_frame()
        return df
    except Exception as e:
        print(f"[WARN] yfinance failed: {e}")
        return None

def main():
    ap = argparse.ArgumentParser(description="Daily backtest driver (toy)")
    ap.add_argument("--tickers", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--lookback", type=int, default=7)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--cash", type=float, default=10000.0)
    ap.add_argument("--min-news", type=int, default=0)
    ap.add_argument("--orders-per-day", type=int, default=3)
    ap.add_argument("--keywords", default="data/keywords.json")
    ap.add_argument("--source-weights", default="data/source_weights.json")
    ap.add_argument("--aum-file", default="data/aum.csv")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    keywords = load_json(args.keywords, {"positive":[], "negative":[], "negations":[], "phrase_window":3})
    src_weights = load_json(args.source_weights, {})
    senti = KeywordSentiment(positives=keywords.get("positive", []),
                             negatives=keywords.get("negative", []),
                             negations=keywords.get("negations", []),
                             phrase_window=keywords.get("phrase_window", 3),
                             source_weights=src_weights)
    aum_map = load_aum_csv(args.aum_file)
    per_budget = args.cash / len(tickers)

    # optional price data for naive next-day PnL
    price_df = maybe_fetch_prices(tickers, args.start, args.end)

    daily_pnl = []
    for d in daterange(args.start, args.end):
        orders = []
        for tkr in tickers:
            # fetch within d-lookback .. d
            # for simplicity, re-use RSS if NewsAPI missing; no dedup here to keep it simple
            # A real backtest would cache results to avoid refetching frequently.
            from datetime import datetime, timedelta
            end = d
            start_dt = (datetime.strptime(d, "%Y-%m-%d") - timedelta(days=args.lookback)).strftime("%Y-%m-%d")

            items = []
            if NEWSAPI_KEY:
                try:
                    items = fetch_newsapi_headlines(tkr, start_dt, end, NEWSAPI_KEY, page_size=60)
                except Exception:
                    pass
            if not items:
                items = fetch_rss_google_news(tkr)

            pos = neg = 0
            for it in items:
                p, n, _ = senti.score_item(it)
                pos += p; neg += n
            ratio = pos / max(1, neg)
            direction = direction_from_ratio(ratio, args.threshold)
            if args.min_news and len(items) < args.min_news:
                direction = "HOLD"

            if direction != "HOLD" and len(orders) < args.orders_per_day:
                invest = position_dollars(per_budget, aum_map.get(tkr), ratio)
                orders.append((tkr, direction, invest))

        # naive next-day return based on close-to-close if price_df available
        pnl = 0.0
        if price_df is not None and d in price_df.index.strftime("%Y-%m-%d"):
            try:
                day_idx = list(price_df.index.strftime("%Y-%m-%d")).index(d)
                if day_idx + 1 < len(price_df.index):
                    next_idx = day_idx + 1
                    for tkr, side, amt in orders:
                        p0 = float(price_df.iloc[day_idx][tkr])
                        p1 = float(price_df.iloc[next_idx][tkr])
                        ret = (p1 - p0)/p0
                        pnl += (ret if side == "LONG" else -ret) * amt
            except Exception:
                pass
        daily_pnl.append({"date": d, "pnl": pnl, "orders": len(orders)})

    df = pd.DataFrame(daily_pnl)
    print(df.tail())
    print(f"Total PnL: ${df['pnl'].sum():,.2f} | Avg per day: ${df['pnl'].mean():,.2f}")

if __name__ == "__main__":
    main()
