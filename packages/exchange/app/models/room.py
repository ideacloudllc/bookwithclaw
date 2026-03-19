"""Room (Listing) model for seller inventory."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Room(Base):
    """Hotel room listing."""
    __tablename__ = "rooms"

    id = Column(String, primary_key=True, index=True)
    seller_id = Column(String, ForeignKey("agent.agent_id"), index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # standard, deluxe, suite, economy
    description = Column(String, nullable=True)
    base_price = Column(Float, nullable=False)
    floor_price = Column(Float, nullable=False)
    max_occupancy = Column(Integer, nullable=False, default=2)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seller = relationship("Agent", back_populates="rooms")

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "base_price": self.base_price,
            "floor_price": self.floor_price,
            "max_occupancy": self.max_occupancy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
