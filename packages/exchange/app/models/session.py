"""Negotiation session model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SessionState(str, Enum):
    """Negotiation session state."""

    OPEN = "OPEN"
    MATCHING = "MATCHING"
    NEGOTIATING = "NEGOTIATING"
    AGREED = "AGREED"
    SETTLING = "SETTLING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class Session(Base):
    """Negotiation session between buyer and seller."""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    buyer_agent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    seller_agent_id: Mapped[str] = mapped_column(String(255), nullable=True)
    state: Mapped[SessionState] = mapped_column(
        SQLEnum(SessionState), default=SessionState.OPEN
    )
    vertical: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "hotels"
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    max_rounds: Mapped[int] = mapped_column(Integer, default=10)
    
    # Negotiation data
    intent_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    ask_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    agreed_price: Mapped[int] = mapped_column(Integer, nullable=True)  # in cents
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    timeout_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
