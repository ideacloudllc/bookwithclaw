"""Transaction model for settlement."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TransactionStatus(str, Enum):
    """Transaction settlement status."""

    PENDING = "pending"
    ESCROW_LOCKED = "escrow_locked"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class Transaction(Base):
    """Transaction record for a completed negotiation."""

    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    booking_ref: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    buyer_agent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    seller_agent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    agreed_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    seller_payout_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus), default=TransactionStatus.PENDING
    )
    
    # Stripe
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), nullable=True)
    stripe_charge_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
