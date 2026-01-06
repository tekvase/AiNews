from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json
from datetime import datetime, timedelta

from openai import OpenAI
from dotenv import load_dotenv

# 🔹 DATABASE
from database import engine
from models import Base

# 🔹 ROUTERS
from auth import router as auth_router
from trades import router as trades_router

# 🔹 DAY 4: PRICE TRACKER
from price_tracker import check_targets

# -------------------------------------------------
# 1. ENV SETUP
# -------------------------------------------------

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

if not OPENAI_API_KEY or not FINNHUB_API_KEY:
    print("⚠️ WARNING: API keys are missing")

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------------------------------
# 2. APP SETUP
# -------------------------------------------------

app = FastAPI(title="AI Stock News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for MVP
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# 3. DATABASE INIT
# -------------------------------------------------

Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# 4. ROUTERS
# -------------------------------------------------

app.include_router(auth_router)
app.include_router(trades_router, prefix="/trades")

# -------------------------------------------------
# 5. HEALTH CHECK
# -------------------------------------------------

@app.get("/")
def home():
    return {"message": "AI Stock News API is running!"}

# -------------------------------------------------
# 6. AI ANALYSIS (BATCHED & SAFE)
# -------------------------------------------------

def analyze_batch_sentiment(headlines: list) -> list:
    if not headlines:
        return []

    prompt = (
        "Analyze the sentiment of the following financial headlines. "
        "Return a JSON object with a single key 'sentiments' containing a list of strings. "
        "The strings must be exactly: 'positive', 'negative', or 'neutral'. "
        "The list order must match the headlines exactly.\n\n"
        f"Headlines: {json.dumps(headlines)}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst helper. Output valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            return ["neutral"] * len(headlines)

        content = json.loads(raw_content)
        sentiments = content.get("sentiments", [])

        if len(sentiments) != len(headlines):
            return ["neutral"] * len(headlines)

        return sentiments

    except Exception as e:
        print(f"AI Error: {e}")
        return ["neutral"] * len(headlines)

# -------------------------------------------------
# 7. MAIN NEWS + SIGNAL ENDPOINT
# -------------------------------------------------

@app.get("/news/{symbol}")
def get_stock_news(symbol: str):
    symbol = symbol.upper()

    # --- A. GET CURRENT PRICE ---
    try:
        quote_url = (
            f"https://finnhub.io/api/v1/quote"
            f"?symbol={symbol}&token={FINNHUB_API_KEY}"
        )
        quote_res = requests.get(quote_url, timeout=5)
        current_price = quote_res.json().get("c", 0)
    except Exception:
        current_price = 0

    # --- B. GET NEWS (LAST 7 DAYS) ---
    today = datetime.now().date()
    from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        news_url = (
            f"https://finnhub.io/api/v1/company-news"
            f"?symbol={symbol}&from={from_date}&to={today}"
            f"&token={FINNHUB_API_KEY}"
        )
        articles = requests.get(news_url, timeout=5).json()[:7]
    except Exception:
        articles = []

    # --- C. AI SENTIMENT ---
    headlines = [a.get("headline", "") for a in articles]
    sentiments = analyze_batch_sentiment(headlines)

    positive = negative = neutral = 0

    for i, article in enumerate(articles):
        s = sentiments[i]
        article["sentiment"] = s

        if s == "positive":
            positive += 1
        elif s == "negative":
            negative += 1
        else:
            neutral += 1

    score = 50 + (positive * 10) - (negative * 10)
    score = max(0, min(100, score))

    if score >= 60:
        signal = "BUY"
    elif score <= 40:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    return {
        "symbol": symbol,
        "price": current_price,
        "alert": signal != "NEUTRAL",
        "sentiment": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "buy_score": score,
            "signal": signal
        },
        "news": articles
    }

# -------------------------------------------------
# 8. DAY 4 – DEBUG PRICE CHECK (TEMPORARY)
# -------------------------------------------------

@app.post("/debug/check-targets")
def debug_check_targets():
    check_targets()
    return {"message": "Price target check executed"}
