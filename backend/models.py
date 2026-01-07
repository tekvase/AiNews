from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
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

    trades = relationship("Trade", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trades")


# -------------------------------------------------
# NOTIFICATION MODEL
# -------------------------------------------------

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")