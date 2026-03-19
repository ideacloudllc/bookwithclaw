"""Negotiation state machine for agent-to-agent hotel booking."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.session import Session, SessionState


class NegotiationStateMachine:
    """Manage negotiation session state and transitions."""
    
    VALID_TRANSITIONS = {
        SessionState.OPEN: [SessionState.MATCHING, SessionState.FAILED],
        SessionState.MATCHING: [SessionState.NEGOTIATING, SessionState.FAILED],
        SessionState.NEGOTIATING: [SessionState.AGREED, SessionState.FAILED],
        SessionState.AGREED: [SessionState.SETTLING, SessionState.FAILED],
        SessionState.SETTLING: [SessionState.COMPLETE, SessionState.FAILED],
        SessionState.COMPLETE: [],
        SessionState.FAILED: [],
    }
    
    def __init__(self, db: AsyncSession):
        """Initialize state machine with database session."""
        self.db = db
    
    async def open_session(
        self,
        session_id: str,
        buyer_agent_id: str,
        vertical: str = "hotels",
        max_rounds: int = 10,
    ) -> Session:
        """
        Create a new negotiation session.
        
        Args:
            session_id: Unique session ID
            buyer_agent_id: Buyer agent's ID
            vertical: Vertical market (e.g., "hotels")
            max_rounds: Maximum negotiation rounds allowed
            
        Returns:
            Created Session
        """
        timeout_at = datetime.utcnow() + timedelta(
            seconds=settings.session_negotiation_timeout
        )
        
        session = Session(
            session_id=session_id,
            buyer_agent_id=buyer_agent_id,
            vertical=vertical,
            max_rounds=max_rounds,
            timeout_at=timeout_at,
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        stmt = select(Session).where(Session.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def transition(
        self,
        session_id: str,
        new_state: SessionState,
        reason: Optional[str] = None,
    ) -> Session:
        """
        Transition a session to a new state.
        
        Validates that the transition is allowed by VALID_TRANSITIONS.
        
        Args:
            session_id: Session ID
            new_state: Target state
            reason: Optional reason for transition
            
        Returns:
            Updated Session
            
        Raises:
            InvalidStateTransitionError: If transition is not allowed
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if new_state not in self.VALID_TRANSITIONS.get(session.state, []):
            raise InvalidStateTransitionError(
                f"Cannot transition from {session.state} to {new_state}"
            )
        
        session.state = new_state
        session.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def set_seller(self, session_id: str, seller_agent_id: str) -> Session:
        """Set the seller for a session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.seller_agent_id = seller_agent_id
        session.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def store_intent(self, session_id: str, intent_data: dict) -> Session:
        """Store buyer intent data in session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.intent_data = intent_data
        session.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def store_ask(self, session_id: str, ask_data: dict) -> Session:
        """Store seller ask data in session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.ask_data = ask_data
        session.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def increment_round(self, session_id: str) -> Session:
        """
        Increment negotiation round.
        
        If max_rounds is exceeded, transitions to FAILED.
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.round_number += 1
        session.updated_at = datetime.utcnow()
        
        # Check if max rounds exceeded
        if session.round_number > session.max_rounds:
            session.state = SessionState.FAILED
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def agree_price(self, session_id: str, agreed_price: int) -> Session:
        """
        Record agreed price and transition to AGREED state.
        
        Args:
            session_id: Session ID
            agreed_price: Agreed price in cents
            
        Returns:
            Updated Session (now in AGREED state)
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.agreed_price = agreed_price
        session.updated_at = datetime.utcnow()
        
        # Transition to AGREED
        if session.state == SessionState.NEGOTIATING:
            session.state = SessionState.AGREED
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def check_timeouts(self) -> list:
        """
        Check for expired sessions and transition them to FAILED.
        
        Returns:
            List of sessions that timed out
        """
        now = datetime.utcnow()
        
        # Find sessions that have timed out
        stmt = select(Session).where(
            (Session.timeout_at < now) & (Session.state != SessionState.COMPLETE)
            & (Session.state != SessionState.FAILED)
        )
        result = await self.db.execute(stmt)
        timed_out_sessions = result.scalars().all()
        
        for session in timed_out_sessions:
            session.state = SessionState.FAILED
            session.updated_at = now
        
        if timed_out_sessions:
            await self.db.commit()
        
        return timed_out_sessions


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass
