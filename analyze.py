import argparse
from datetime import datetime, timedelta
import os

from scripts import sentiment_utils
from scripts.visualize import plot_sentiment_bar, plot_top_sources_pie
from scripts.scrape_news import scrape_articles_for_ticker
from config import DEFAULT_AUM, LOOKBACK_DAYS, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS, OUTPUT_DIR
from scripts.export_pdf import save_investment_report

def main():
    parser = argparse.ArgumentParser(description="Run sentiment-based investment decision.")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol")
    parser.add_argument("--date", type=str, required=True, help="Target date (YYYY-MM-DD)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    target_date = datetime.strptime(args.date, "%Y-%m-%d")
    start_date = target_date - timedelta(days=LOOKBACK_DAYS)

    print(f"[INFO] Running for {ticker} from {start_date.date()} to {target_date.date()}...")

    # Updated: get both article texts and sources
    articles, sources = scrape_articles_for_ticker(ticker, start_date, target_date)
    print(f"[INFO] Retrieved {len(articles)} articles.")

    total_pos, total_neg = 0, 0
    for text in articles:
        pos, neg = sentiment_utils.count_sentiment_words(text, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS)
        total_pos += pos
        total_neg += neg

    print(f"[RESULT] Total Positive Words: {total_pos}, Total Negative Words: {total_neg}")

    # Determine sentiment signal
    if total_pos > total_neg:
        sentiment = "LONG"
        strength = (total_pos - total_neg) / max(total_pos + total_neg, 1)
        position_size = round(DEFAULT_AUM * strength)
    elif total_neg > total_pos:
        sentiment = "SHORT"
        strength = (total_neg - total_pos) / max(total_pos + total_neg, 1)
        position_size = round(DEFAULT_AUM * strength)
    else:
        sentiment = "HOLD"
        strength = 0
        position_size = 0

    print(f"[ACTION] {sentiment} {ticker} with ${position_size} (Sentiment Strength: {strength:.2f})")

    # Save PDF report with sources
    save_investment_report(
        ticker,
        start_date,
        target_date,
        total_pos,
        total_neg,
        sentiment,
        position_size,
        len(articles),
        OUTPUT_DIR,
        sources
    )

    plot_sentiment_bar(ticker, total_pos, total_neg, OUTPUT_DIR)
    plot_top_sources_pie(ticker, sources, OUTPUT_DIR)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()
