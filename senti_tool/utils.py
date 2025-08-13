from datetime import datetime, timedelta
from typing import Tuple, Iterable

def date_window_str(end_date_str: str, lookback_days: int) -> Tuple[str, str]:
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    start = end - timedelta(days=lookback_days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def daterange(start_date: str, end_date: str):
    s = datetime.strptime(start_date, "%Y-%m-%d")
    e = datetime.strptime(end_date, "%Y-%m-%d")
    d = s
    while d <= e:
        yield d.strftime("%Y-%m-%d")
        d += timedelta(days=1)
