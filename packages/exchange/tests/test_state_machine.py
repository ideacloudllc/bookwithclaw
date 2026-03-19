"""Tests for negotiation state machine."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.state_machine import NegotiationStateMachine, InvalidStateTransitionError
from app.models.session import SessionState


@pytest.mark.asyncio
async def test_open_session(db_session: AsyncSession):
    """Test creating a new session."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    session = await machine.open_session(
        session_id=session_id,
        buyer_agent_id=buyer_id,
        vertical="hotels",
    )

    assert session.session_id == session_id
    assert session.buyer_agent_id == buyer_id
    assert session.state == SessionState.OPEN
    assert session.round_number == 1


@pytest.mark.asyncio
async def test_valid_transitions(db_session: AsyncSession):
    """Test valid state transitions."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    # Create session
    await machine.open_session(session_id, buyer_id, "hotels")

    # OPEN -> MATCHING
    session = await machine.transition(session_id, SessionState.MATCHING)
    assert session.state == SessionState.MATCHING

    # MATCHING -> NEGOTIATING
    session = await machine.transition(session_id, SessionState.NEGOTIATING)
    assert session.state == SessionState.NEGOTIATING

    # NEGOTIATING -> AGREED
    session = await machine.transition(session_id, SessionState.AGREED)
    assert session.state == SessionState.AGREED

    # AGREED -> SETTLING
    session = await machine.transition(session_id, SessionState.SETTLING)
    assert session.state == SessionState.SETTLING

    # SETTLING -> COMPLETE
    session = await machine.transition(session_id, SessionState.COMPLETE)
    assert session.state == SessionState.COMPLETE


@pytest.mark.asyncio
async def test_invalid_transition(db_session: AsyncSession):
    """Test that invalid transitions are rejected."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    await machine.open_session(session_id, buyer_id, "hotels")

    # OPEN -> COMPLETE is not valid
    with pytest.raises(InvalidStateTransitionError):
        await machine.transition(session_id, SessionState.COMPLETE)


@pytest.mark.asyncio
async def test_set_seller(db_session: AsyncSession):
    """Test assigning a seller to session."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())
    seller_id = str(uuid.uuid4())

    await machine.open_session(session_id, buyer_id, "hotels")
    session = await machine.set_seller(session_id, seller_id)

    assert session.seller_agent_id == seller_id


@pytest.mark.asyncio
async def test_store_intent(db_session: AsyncSession):
    """Test storing intent data."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    await machine.open_session(session_id, buyer_id, "hotels")

    intent_data = {
        "budget_ceiling": 50000,
        "preferred_terms": {"free_wifi": True},
    }

    session = await machine.store_intent(session_id, intent_data)
    assert session.intent_data == intent_data


@pytest.mark.asyncio
async def test_increment_round(db_session: AsyncSession):
    """Test incrementing negotiation round."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    await machine.open_session(session_id, buyer_id, "hotels", max_rounds=10)

    session = await machine.increment_round(session_id)
    assert session.round_number == 2

    session = await machine.increment_round(session_id)
    assert session.round_number == 3


@pytest.mark.asyncio
async def test_max_rounds_exceeded(db_session: AsyncSession):
    """Test that session fails when max rounds exceeded."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    # Create session with max_rounds = 2
    await machine.open_session(session_id, buyer_id, "hotels", max_rounds=2)

    # First increment: 1 -> 2
    await machine.increment_round(session_id)

    # Second increment: 2 -> fail (max reached)
    session = await machine.increment_round(session_id)

    assert session.state == SessionState.FAILED


@pytest.mark.asyncio
async def test_agree_price(db_session: AsyncSession):
    """Test recording agreed price."""
    machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    await machine.open_session(session_id, buyer_id, "hotels")

    # Transition to NEGOTIATING first (required for AGREED)
    await machine.transition(session_id, SessionState.MATCHING)
    await machine.transition(session_id, SessionState.NEGOTIATING)

    # Agree on price
    price = 40000
    session = await machine.agree_price(session_id, price)

    assert session.agreed_price == price
    assert session.state == SessionState.AGREED
