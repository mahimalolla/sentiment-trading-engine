# Sentiment Trader Pro (Rule-Based, Resume-Ready)
An interpretable, production-style sentiment trading toolkit. Key features:
- **Dual fetchers**: NewsAPI (if `NEWSAPI_KEY`) with Google News RSS fallback
- **Keyword sentiment**: inflection-aware regex + *negation handling* + *earnings phrases*
- **Source weighting**: optionally up/down-weight outlets via `data/source_weights.json`
- **Deduplication**: near-duplicate title/URL pruning
- **Risk controls**: `--min-news`, `--max-positions`, `--max-per-ticker`
- **Sizing**: AUM + sentiment magnitude
- **Artifacts**: PDF report, orders CSV, JSON summary
- **SQLite ledger**: every run + headline saved for auditability (`sentiment.db`)
- **Backtesting**: `scripts/backtest.py` (optional `yfinance`) to compute forward returns
- **Docker + Makefile** for easy runs

## Quickstart
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "NEWSAPI_KEY=put-your-key-here" > .env   # optional

# AUM CSV (ticker,aum in USD)
echo -e "AAPL,3000000000000\nTSLA,800000000000" > data/aum.csv

# Run (PowerShell: use backticks for newlines, or keep in one line)
python -m scripts.analyze --tickers AAPL,TSLA --cash 10000 --date 2025-07-30 --lookback 14   --threshold 0.5 --max-results 60 --min-news 10 --max-positions 5   --orders-csv out/orders.csv --pdf out/report.pdf
```

## Backtest (toy example)
```bash
python -m scripts.backtest --tickers AAPL,TSLA --start 2025-07-01 --end 2025-08-01   --lookback 7 --threshold 0.5 --cash 10000 --min-news 10 --orders-per-day 3
```

## Files
- `scripts/analyze.py` – main CLI with risk controls, dedup, orders CSV, SQLite logging
- `scripts/backtest.py` – run daily decisions; optional price-based returns via yfinance
- `senti_tool/sentiment.py` – regex keywords, inflections, negation, phrase patterns
- `senti_tool/fetchers/*` – NewsAPI + Google News RSS
- `senti_tool/sizing.py` – direction + position sizing
- `senti_tool/reporting.py` – PDF with sources + chart
- `senti_tool/db.py` – SQLite ledger (`sentiment.db`), creates tables
- `data/keywords.json` – seed lists incl. earnings phrases
- `data/source_weights.json` – optional outlet weights (e.g., Reuters=1.2)
- `data/aum.csv` – sample AUM
