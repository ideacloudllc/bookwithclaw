"""Negotiation state machine for agent-to-agent hotel booking."""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

from app.config import settings

Base = declarative_base()


class SessionState(str, Enum):
    """Negotiation session states."""
    OPEN = "OPEN"
    MATCHING = "MATCHING"
    NEGOTIATING = "NEGOTIATING"
    AGREED = "AGREED"
    SETTLING = "SETTLING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class Session(Base):
    """Session model for negotiation tracking."""
    __tablename__ = "sessions"
    
    session_id = Column(String(255), primary_key=True)
    state = Column(SQLEnum(SessionState), default=SessionState.OPEN)
    buyer_id = Column(String(255), nullable=True)
    seller_id = Column(String(255), nullable=True)
    
    intent_id = Column(String(255), nullable=True)
    ask_id = Column(String(255), nullable=True)
    
    round_number = Column(Integer, default=0)
    agreed_price_cents = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(seconds=settings.session_negotiation_timeout))


class NegotiationStateMachine:
    """Manage session state and transitions."""
    
    VALID_TRANSITIONS = {
        SessionState.OPEN: [SessionState.MATCHING, SessionState.FAILED],
        SessionState.MATCHING: [SessionState.NEGOTIATING, SessionState.FAILED],
        SessionState.NEGOTIATING: [SessionState.AGREED, SessionState.FAILED],
        SessionState.AGREED: [SessionState.SETTLING, SessionState.FAILED],
        SessionState.SETTLING: [SessionState.COMPLETE, SessionState.FAILED],
        SessionState.COMPLETE: [],
        SessionState.FAILED: [],
    }
    
    def __init__(self):
        pass
    
    async def create_session(self, buyer_id: str, intent_id: str) -> Session:
        """Create a new session for a buyer intent."""
        session = Session(
            session_id=f"session_{uuid4().hex[:16]}",
            state=SessionState.OPEN,
            buyer_id=buyer_id,
            intent_id=intent_id,
        )
        return session
    
    async def transition(
        self,
        session: Session,
        new_state: SessionState,
        reason: Optional[str] = None
    ) -> Session:
        """
        Transition session to new state.
        
        Validates state transition rules strictly.
        """
        if new_state not in self.VALID_TRANSITIONS.get(session.state, []):
            raise InvalidStateTransitionError(
                f"Cannot transition from {session.state} to {new_state}"
            )
        
        session.state = new_state
        session.updated_at = datetime.utcnow()
        
        return session
    
    async def handle_buyer_intent(self, session: Session, intent: dict) -> Session:
        """Handle buyer intent message."""
        if session.state != SessionState.OPEN:
            raise InvalidStateTransitionError(
                f"Cannot handle intent in state {session.state}"
            )
        
        # Move to MATCHING
        await self.transition(session, SessionState.MATCHING)
        return session
    
    async def handle_seller_ask(self, session: Session, ask: dict) -> Session:
        """Handle seller ask message."""
        if session.state != SessionState.MATCHING:
            raise InvalidStateTransitionError(
                f"Cannot handle ask in state {session.state}"
            )
        
        session.seller_id = ask.get("sender_id")
        session.ask_id = ask.get("ask_id")
        
        # Move to NEGOTIATING
        await self.transition(session, SessionState.NEGOTIATING)
        return session
    
    async def handle_counter_offer(self, session: Session, counter: dict) -> Session:
        """Handle counter-offer message."""
        if session.state != SessionState.NEGOTIATING:
            raise InvalidStateTransitionError(
                f"Cannot handle counter in state {session.state}"
            )
        
        # Validate envelope (counter must be within bounds)
        # This is checked at the messaging layer
        
        session.round_number += 1
        
        # Check max rounds
        if session.round_number > settings.max_negotiation_rounds:
            await self.transition(session, SessionState.FAILED, "Max rounds exceeded")
        
        return session
    
    async def handle_deal_accepted(self, session: Session, deal: dict) -> Session:
        """Handle deal_accepted message."""
        if session.state != SessionState.NEGOTIATING:
            raise InvalidStateTransitionError(
                f"Cannot accept deal in state {session.state}"
            )
        
        session.agreed_price_cents = deal.get("agreed_price_cents")
        
        # Move to AGREED
        await self.transition(session, SessionState.AGREED)
        return session
    
    async def handle_walkaway(self, session: Session, reason: str) -> Session:
        """Handle session_walkaway message."""
        if session.state in [SessionState.COMPLETE, SessionState.FAILED]:
            return session
        
        # Move to FAILED
        await self.transition(session, SessionState.FAILED, reason)
        return session
    
    async def check_timeouts(self, session: Session) -> Optional[Session]:
        """Check if session has expired."""
        if datetime.utcnow() > session.expires_at:
            await self.transition(session, SessionState.FAILED, "Session timeout")
            return session
        
        return None


class InvalidStateTransitionError(Exception):
    """Raised when invalid state transition attempted."""
    pass
