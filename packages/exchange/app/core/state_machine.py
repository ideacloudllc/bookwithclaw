"""Negotiation session state machine."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, SessionState


class InvalidStateTransitionError(Exception):
    """Raised when state transition is invalid."""

    pass


class NegotiationStateMachine:
    """Manages negotiation session state machine."""

    # Valid transitions
    VALID_TRANSITIONS = {
        SessionState.OPEN: [SessionState.MATCHING],
        SessionState.MATCHING: [SessionState.NEGOTIATING, SessionState.FAILED],
        SessionState.NEGOTIATING: [
            SessionState.NEGOTIATING,  # Multiple rounds
            SessionState.AGREED,
            SessionState.FAILED,
        ],
        SessionState.AGREED: [SessionState.SETTLING],
        SessionState.SETTLING: [SessionState.COMPLETE, SessionState.FAILED],
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def open_session(
        self,
        session_id: str,
        buyer_agent_id: str,
        vertical: str,
        max_rounds: int = 10,
    ) -> Session:
        """Create a new negotiation session."""
        session = Session(
            session_id=session_id,
            buyer_agent_id=buyer_agent_id,
            state=SessionState.OPEN,
            vertical=vertical,
            round_number=1,
            max_rounds=max_rounds,
            created_at=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.commit()
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Fetch session by ID."""
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        return result.scalars().first()

    async def transition(
        self,
        session_id: str,
        new_state: SessionState,
    ) -> Session:
        """
        Transition session to a new state.

        Args:
            session_id: Session to transition
            new_state: Target state

        Returns:
            Updated session

        Raises:
            InvalidStateTransitionError if transition is invalid
            ValueError if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Check valid transition
        valid_next = self.VALID_TRANSITIONS.get(session.state, [])
        if new_state not in valid_next:
            raise InvalidStateTransitionError(
                f"Cannot transition from {session.state} to {new_state}"
            )

        # Update state
        session.state = new_state
        session.updated_at = datetime.utcnow()

        await self.db.commit()
        return session

    async def set_seller(self, session_id: str, seller_agent_id: str) -> Session:
        """Assign a seller to the session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.seller_agent_id = seller_agent_id
        session.updated_at = datetime.utcnow()
        await self.db.commit()
        return session

    async def store_intent(
        self,
        session_id: str,
        intent_data: dict,
    ) -> Session:
        """Store buyer intent data in session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.intent_data = intent_data
        session.updated_at = datetime.utcnow()
        await self.db.commit()
        return session

    async def store_ask(
        self,
        session_id: str,
        ask_data: dict,
    ) -> Session:
        """Store seller ask data in session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.ask_data = ask_data
        session.updated_at = datetime.utcnow()
        await self.db.commit()
        return session

    async def increment_round(self, session_id: str) -> Session:
        """Increment negotiation round number."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Check if max rounds exceeded
        if session.round_number >= session.max_rounds:
            # Auto-fail session
            session.state = SessionState.FAILED
        else:
            session.round_number += 1

        session.updated_at = datetime.utcnow()
        await self.db.commit()
        return session

    async def agree_price(self, session_id: str, price_cents: int) -> Session:
        """Record agreed price and transition to AGREED."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.agreed_price = price_cents
        session.state = SessionState.AGREED
        session.updated_at = datetime.utcnow()
        await self.db.commit()
        return session

    async def check_timeouts(self) -> list[Session]:
        """
        Check all sessions for timeout and fail them if exceeded.

        Returns:
            List of sessions that timed out
        """
        timed_out = []
        now = datetime.utcnow()

        # Fetch all open/negotiating/settling sessions
        result = await self.db.execute(
            select(Session).where(
                Session.state.in_(
                    [
                        SessionState.OPEN,
                        SessionState.MATCHING,
                        SessionState.NEGOTIATING,
                        SessionState.SETTLING,
                    ]
                )
            )
        )
        sessions = result.scalars().all()

        for session in sessions:
            # Determine timeout based on state
            timeout_seconds = self._get_timeout_for_state(session.state)
            timeout_at = session.created_at + timedelta(seconds=timeout_seconds)

            if now > timeout_at:
                session.state = SessionState.FAILED
                session.updated_at = now
                timed_out.append(session)

        if timed_out:
            await self.db.commit()

        return timed_out

    # Private helpers

    def _get_timeout_for_state(self, state: SessionState) -> int:
        """Get timeout in seconds for a given state."""
        from app.config import settings

        if state == SessionState.OPEN:
            return settings.session_open_timeout
        elif state in [SessionState.MATCHING, SessionState.NEGOTIATING]:
            return settings.session_negotiation_timeout
        elif state == SessionState.SETTLING:
            return settings.session_settlement_timeout
        else:
            return 3600  # 1 hour default
