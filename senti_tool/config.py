import os
from dotenv import load_dotenv
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY","").strip()
DEFAULT_MAX_RESULTS = 60
USER_AGENT = "SentimentTrader/2.0"
DB_PATH = os.getenv("SENTI_DB_PATH","sentiment.db")
