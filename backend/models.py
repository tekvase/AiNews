from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from database import Base


# -------------------------------------------------
# USER MODEL
# -------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)


# -------------------------------------------------
# TRADE MODEL
# -------------------------------------------------

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    symbol = Column(String, index=True, nullable=False)

    buy_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)

    status = Column(String, default="OPEN")
     # OPEN → TARGET_REACHED → CLOSED


    created_at = Column(DateTime, default=datetime.utcnow)
