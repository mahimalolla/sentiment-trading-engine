import argparse
from datetime import datetime, timedelta
import os

from scripts import sentiment_utils
from config import DEFAULT_AUM, LOOKBACK_DAYS, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS, OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="Run sentiment-based investment decision.")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol")
    parser.add_argument("--date", type=str, required=True, help="Target date (YYYY-MM-DD)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    target_date = datetime.strptime(args.date, "%Y-%m-%d")
    start_date = target_date - timedelta(days=LOOKBACK_DAYS)

    print(f"[INFO] Running for {ticker} from {start_date.date()} to {target_date.date()}...")

    print("[TODO] Scrape articles and compute sentiment scores.")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()
