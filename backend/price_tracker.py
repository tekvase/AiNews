# heart of your app
from typing import cast
from database import SessionLocal
from models import Trade
from price_service import get_current_price

def check_targets():
    db = SessionLocal()
    try:
        open_trades = db.query(Trade).filter(Trade.status == "OPEN").all()

        for trade in open_trades:
            current_price = get_current_price(str(trade.symbol))
            target_price = cast(float, trade.target_price)

            if current_price > 0 and current_price >= target_price:
                setattr(trade, 'status', 'TARGET_REACHED')
                db.commit()

                print(
                    f"🎯 Target hit for {trade.symbol} | "
                    f"Buy: {trade.buy_price} → Current: {current_price}"
                )
    finally:
        db.close()
