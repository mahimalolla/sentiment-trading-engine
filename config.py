# Default configuration values
# config.py

NEWSAPI_KEY = "9e85a1f3b5fd47598bbaf1f6135eefcd"
DEFAULT_AUM = 10000  # Starting capital in dollars
LOOKBACK_DAYS = 7    # How many days before the given date to pull articles for
SENTIMENT_THRESHOLD = 1  # Minimum net sentiment to take a position

POSITIVE_KEYWORDS = [
    "growth", "beat", "outperform", "record", "strong", "gain", "profit", "rise", "improve"
]
NEGATIVE_KEYWORDS = [
    "loss", "miss", "decline", "fall", "weak", "drop", "cut", "plunge", "underperform"
]

OUTPUT_DIR = "data"
