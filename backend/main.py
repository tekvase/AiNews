from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json
from datetime import datetime, timedelta

from openai import OpenAI

# 🔐 Security
from security import get_current_user

# 🔹 DATABASE
from database import engine
from models import Base

# 🔹 ROUTERS
from auth import router as auth_router
from trades import router as trades_router

# 🔹 PRICE TRACKER
from price_tracker import check_targets

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

if not OPENAI_API_KEY or not FINNHUB_API_KEY:
    print("⚠️ WARNING: API keys are missing")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------

app = FastAPI(title="AI Stock News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for MVP
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DATABASE INIT
# -------------------------------------------------

Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# ROUTERS
# -------------------------------------------------

app.include_router(auth_router)
app.include_router(trades_router)

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------

@app.get("/")
def home():
    return {"message": "AI Stock News API is running!"}

# -------------------------------------------------
# AI SENTIMENT ANALYSIS
# -------------------------------------------------

def analyze_batch_sentiment(headlines: list) -> list:
    if not headlines or not client:
        return ["neutral"] * len(headlines)

    prompt = (
        "Analyze the sentiment of the following financial headlines. "
        "Return a JSON object with key 'sentiments' as a list of "
        "'positive', 'negative', or 'neutral'.\n\n"
        f"{json.dumps(headlines)}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Output valid JSON only"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"}
        )

        content = json.loads(response.choices[0].message.content)
        sentiments = content.get("sentiments", [])

        if len(sentiments) != len(headlines):
            return ["neutral"] * len(headlines)

        return sentiments

    except Exception as e:
        print("AI Error:", e)
        return ["neutral"] * len(headlines)

# -------------------------------------------------
# NEWS + SIGNAL ENDPOINT
# -------------------------------------------------

@app.get("/news/{symbol}")
def get_stock_news(symbol: str):
    symbol = symbol.upper()

    # Current price
    try:
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        current_price = requests.get(quote_url, timeout=5).json().get("c", 0)
    except Exception:
        current_price = 0

    # News
    today = datetime.utcnow().date()
    from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        news_url = (
            f"https://finnhub.io/api/v1/company-news"
            f"?symbol={symbol}&from={from_date}&to={today}&token={FINNHUB_API_KEY}"
        )
        articles = requests.get(news_url, timeout=5).json()[:7]
    except Exception:
        articles = []

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

    score = max(0, min(100, 50 + positive * 10 - negative * 10))

    signal = "BUY" if score >= 60 else "SELL" if score <= 40 else "NEUTRAL"

    return {
        "symbol": symbol,
        "price": current_price,
        "alert": signal != "NEUTRAL",
        "sentiment": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "buy_score": score,
            "signal": signal,
        },
        "news": articles,
    }

# -------------------------------------------------
# DEBUG – PRICE CHECK (PROTECTED)
# -------------------------------------------------

@app.post("/debug/check-targets")
def debug_check_targets(current_user = Depends(get_current_user)):
    check_targets()
    return {"message": "Price target check executed"}

# -------------------------------------------------
# PROTECTED TEST
# -------------------------------------------------

@app.get("/protected")
def protected(current_user = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "email": current_user.email,
    }