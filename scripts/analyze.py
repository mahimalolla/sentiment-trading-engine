#!/usr/bin/env python3
import argparse, os, json, math, sys, csv, time
from collections import Counter, defaultdict
import pandas as pd

from senti_tool.config import NEWSAPI_KEY, DEFAULT_MAX_RESULTS
from senti_tool.fetchers.newsapi_fetcher import fetch_newsapi_headlines
from senti_tool.fetchers.rss_fetcher import fetch_rss_google_news
from senti_tool.sentiment import KeywordSentiment, normalize_title
from senti_tool.sizing import direction_from_ratio, position_dollars
from senti_tool.reporting import generate_pdf
from senti_tool.utils import date_window_str
from senti_tool.db import init_db, insert_run, insert_headlines

def load_json(path: str, default):
    if not path or not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_aum_csv(path: str):
    if not path or not os.path.exists(path):
        return {}
    df = pd.read_csv(path, header=None, names=["ticker","aum"])
    return {str(r.ticker).upper(): float(r.aum) for _, r in df.iterrows() if pd.notna(r.aum)}

def aggregate_sources(items):
    c = Counter(x.get("source","") or "Unknown" for x in items if x.get("source"))
    return c.most_common()

def dedup_items(items):
    seen = set()
    uniq = []
    for it in items:
        key = (normalize_title(it.get("title","")), (it.get("url") or "").split("?")[0])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(it)
    return uniq

def main():
    ap = argparse.ArgumentParser(description="Rule-based sentiment trading tool (Pro)")
    ap.add_argument("--tickers", required=True, help="Comma separated tickers (e.g., AAPL,TSLA)")
    ap.add_argument("--cash", type=float, required=True, help="Total cash to allocate")
    ap.add_argument("--date", required=True, help="End date YYYY-MM-DD")
    ap.add_argument("--lookback", type=int, default=14, help="Lookback window in days")
    ap.add_argument("--threshold", type=float, default=0.5, help="Log2 ratio threshold for LONG/SHORT")
    ap.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS, help="Max NewsAPI articles per ticker")
    ap.add_argument("--min-news", type=int, default=0, help="Require at least this many headlines to trade")
    ap.add_argument("--max-positions", type=int, default=999, help="Cap number of non-HOLD positions across tickers")
    ap.add_argument("--max-per-ticker", type=float, default=1.0, help="Cap fraction of per-ticker budget (0..1)")
    ap.add_argument("--keywords", default="data/keywords.json", help="Path to keywords JSON")
    ap.add_argument("--source-weights", default="data/source_weights.json", help="Path to source weight map")
    ap.add_argument("--aum-file", default="data/aum.csv", help="CSV of ticker,aum (USD)")
    ap.add_argument("--pdf", default="", help="Path to output PDF report (e.g., out/report.pdf)")
    ap.add_argument("--orders-csv", default="", help="Write orders to CSV (symbol,side,amount_usd)")
    ap.add_argument("--no-dedup", action="store_true", help="Disable deduplication of headlines")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    cash = args.cash
    from_date, to_date = date_window_str(args.date, args.lookback)

    print(f"[INFO] Date window: {from_date} \u2192 {to_date}")
    print(f"[INFO] Tickers: {', '.join(tickers)}")
    print(f"[INFO] Total Cash: ${cash:,.2f} | Per-Ticker Budget: ${cash/len(tickers):,.2f}")
    print(f"[INFO] Threshold (log2 ratio): {args.threshold}")
    print(f"[DEBUG] NEWSAPI_KEY present: {bool(NEWSAPI_KEY)}")

    keywords = load_json(args.keywords, {"positive":[], "negative":[], "negations":[], "phrase_window":3})
    src_weights = load_json(args.source_weights, {})
    senti = KeywordSentiment(positives=keywords.get("positive", []),
                             negatives=keywords.get("negative", []),
                             negations=keywords.get("negations", []),
                             phrase_window=keywords.get("phrase_window", 3),
                             source_weights=src_weights)
    aum_map = load_aum_csv(args.aum_file)

    init_db()
    run_id = insert_run(json.dumps({
        "tickers": tickers, "cash": cash, "from": from_date, "to": to_date,
        "threshold": args.threshold, "min_news": args.min_news
    }))

    per_ticker_rows = []
    all_sources_counter = Counter()
    orders = []
    positions_used = 0

    for tkr in tickers:
        items = []
        if NEWSAPI_KEY:
            try:
                items = fetch_newsapi_headlines(tkr, from_date, to_date, NEWSAPI_KEY, page_size=args.max_results)
            except Exception as e:
                print(f"[WARN] NewsAPI fetch failed for {tkr}: {e}. Falling back to RSS.")
        if not items:
            items = fetch_rss_google_news(tkr)

        if not args.no_dedup:
            items = dedup_items(items)

        # score
        pos = neg = 0
        headlines = []
        for it in items:
            p, n, hits = senti.score_item(it)
            pos += p; neg += n
            headlines.append({
                "ticker": tkr,
                "title": it.get("title",""),
                "url": it.get("url",""),
                "source": it.get("source","Unknown"),
                "published_at": it.get("published_at",""),
                "pos_hits": p,
                "neg_hits": n
            })
        # save to DB
        if headlines:
            insert_headlines(run_id, headlines)

        ratio = pos / max(1, neg)
        all_sources_counter.update(x.get("source","Unknown") or "Unknown" for x in items)

        per_budget = cash / len(tickers)
        aum = aum_map.get(tkr)
        direction = direction_from_ratio(ratio, args.threshold)

        # risk controls
        eligible = True
        if args.min_news and len(items) < args.min_news:
            eligible = False
            direction = "HOLD"
        if positions_used >= args.max_positions and direction != "HOLD":
            eligible = False
            direction = "HOLD"

        invest = 0.0
        if direction != "HOLD" and eligible:
            invest = position_dollars(per_budget, aum, ratio)
            invest = min(invest, per_budget * max(0.0, min(args.max_per_ticker, 1.0)))
            positions_used += 1

        print(f"{tkr:<6} | news={len(items):>3} | pos={pos:<3} neg={neg:<3} | ratio={ratio:+.2f} | dir={direction:<5} | AUM={aum if aum else 'n/a'} | invest=${invest:,.2f}")

        per_ticker_rows.append({
            "ticker": tkr, "pos": pos, "neg": neg, "ratio": ratio,
            "direction": direction, "invest": invest
        })

        if direction in ("LONG", "SHORT") and invest > 0:
            orders.append({"symbol": tkr, "side": direction, "amount_usd": round(invest,2)})

    # outputs
    top_sources = all_sources_counter.most_common(10)
    if args.pdf:
        os.makedirs(os.path.dirname(args.pdf) or ".", exist_ok=True)
        run_ctx = {"from_date": from_date, "to_date": to_date, "cash": cash, "threshold": args.threshold}
        try:
            generate_pdf(args.pdf, run_ctx, per_ticker_rows, top_sources)
            print(f"[INFO] PDF written to {args.pdf}")
        except Exception as e:
            print(f"[ERROR] Failed to write PDF: {e}")

    # JSON summary
    summary = {"run": {"from": from_date, "to": to_date, "cash": cash, "threshold": args.threshold},
               "per_ticker": per_ticker_rows, "top_sources": top_sources, "orders": orders}
    with open("out_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        print("[INFO] Wrote out_summary.json")

    # orders CSV
    if args.orders_csv:
        os.makedirs(os.path.dirname(args.orders_csv) or ".", exist_ok=True)
        with open(args.orders_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["symbol","side","amount_usd"])
            w.writeheader()
            for o in orders:
                w.writerow(o)
        print(f"[INFO] Wrote orders CSV → {args.orders_csv}")

if __name__ == "__main__":
    main()
