"""Agent model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AgentRole(str, Enum):
    """Agent role: buyer or seller."""

    BUYER = "buyer"
    SELLER = "seller"


class Agent(Base):
    """Agent registration and authentication."""

    __tablename__ = "agents"

    agent_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    public_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[AgentRole] = mapped_column(
        SQLEnum(AgentRole), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)  # For seller login
    hotel_name: Mapped[str] = mapped_column(String(255), nullable=True)  # For sellers/buyers (name field)
    stripe_account_id: Mapped[str] = mapped_column(String(255), nullable=True)  # Stripe Connect account ID
    stripe_status: Mapped[str] = mapped_column(String(50), default="not_connected", nullable=False)  # not_connected, pending, connected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    rooms = relationship("Room", back_populates="seller")
