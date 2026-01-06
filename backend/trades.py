from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Trade
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/confirm-buy")
def confirm_buy(
    user_id: int,
    symbol: str,
    buy_price: float,
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()

    target_price = round(buy_price * 1.30, 2)

    trade = Trade(
        user_id=user_id,
        symbol=symbol,
        buy_price=buy_price,
        target_price=target_price
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {
        "message": "Trade confirmed",
        "trade_id": trade.id,
        "symbol": symbol,
        "buy_price": buy_price,
        "target_price": target_price
    }

@router.get("/my-trades")
def my_trades(user_id: int, db: Session = Depends(get_db)):
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()

    return trades

