import requests
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_current_price(symbol: str) -> float:
    try:
        url = (
            f"https://finnhub.io/api/v1/quote"
            f"?symbol={symbol}&token={FINNHUB_API_KEY}"
        )
        res = requests.get(url, timeout=5).json()
        return res.get("c", 0)
    except Exception:
        return 0
