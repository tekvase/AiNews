from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Trade
from security import get_current_user
from price_service import get_current_price

router = APIRouter(prefix="/trades", tags=["trades"])


# -----------------------------
# DB dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Confirm Buy Trade
# -----------------------------
@router.post("/confirm-buy")
def confirm_buy(
    symbol: str,
    buy_price: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    target_price = round(buy_price * 1.3, 2)

    trade = Trade(
        user_id=current_user.id,
        symbol=symbol,
        buy_price=buy_price,
        target_price=target_price,
        status="OPEN",
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {
        "message": "Trade confirmed",
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "buy_price": trade.buy_price,
        "target_price": trade.target_price,
        "status": trade.status,
    }


# -----------------------------
# List My Trades
# -----------------------------
@router.get("/my")
def my_trades(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == current_user.id)
        .order_by(Trade.created_at.desc())
        .all()
    )

    return [
        {
            "trade_id": t.id,
            "symbol": t.symbol,
            "buy_price": t.buy_price,
            "target_price": t.target_price,
            "status": t.status,
            "created_at": t.created_at,
        }
        for t in trades
    ]


# -----------------------------
# Close Trade (NEW)
# -----------------------------
@router.post("/{trade_id}/close")
def close_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    trade = (
        db.query(Trade)
        .filter(
            Trade.id == trade_id,
            Trade.user_id == current_user.id,
        )
        .first()
    )

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    if trade.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Only OPEN trades can be closed",
        )

    trade.status = "CLOSED"
    db.commit()

    return {
        "message": "Trade closed",
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "status": trade.status,
    }