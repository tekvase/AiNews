import os
import requests

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_current_price(symbol: str) -> float | None:
    url = "https://finnhub.io/api/v1/quote"
    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY,
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    # Finnhub returns current price as "c"
    return data.get("c")