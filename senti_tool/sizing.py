from typing import Optional
import math

def direction_from_ratio(ratio: float, threshold: float) -> str:
    score = math.log(max(ratio, 1e-9), 2)
    if score >= threshold:
        return "LONG"
    elif score <= -threshold:
        return "SHORT"
    return "HOLD"

def position_dollars(cash_per_ticker: float, aum_usd: Optional[float], ratio: float) -> float:
    cap = 3_000_000_000_000
    aum = max(0.0, min(aum_usd or 0.0, cap))
    aum_factor = math.sqrt(aum / cap) if aum > 0 else 0.5
    mag = abs(math.log(max(ratio, 1e-9), 2.0))
    sentiment_factor = 1.0 / (1.0 + math.exp(-3*(mag-0.3)))
    return cash_per_ticker * aum_factor * sentiment_factor
