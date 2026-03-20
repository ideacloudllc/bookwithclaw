"""End-to-end integration test for BookWithClaw Exchange."""

import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.signing import generate_keypair, sign_message, canonical_json
from app.core.order_book import OrderBook
from app.core.state_machine import NegotiationStateMachine
from app.main import app, redis_client
from app.models.session import SessionState
from app.database import SessionLocal


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_full_negotiation_flow(db_session: AsyncSession):
    """
    End-to-end test: Order Book → State Machine → Agreement Flow
    
    Tests the core negotiation flow without REST endpoints.
    """
    # Setup
    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())
    seller_id = str(uuid.uuid4())
    intent_id = str(uuid.uuid4())
    ask_id = str(uuid.uuid4())

    # Initialize services
    redis_conn = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    order_book = OrderBook(redis_conn)
    state_machine = NegotiationStateMachine(db_session)

    # Step 1: Open session
    session = await state_machine.open_session(
        session_id=session_id,
        buyer_agent_id=buyer_id,
        vertical="hotels",
    )
    assert session.state == SessionState.OPEN

    # Step 2: Create buyer intent
    intent_data = {
        "intent_id": intent_id,
        "vertical": "hotels",
        "buyer_agent_id": buyer_id,
        "budget_ceiling": 50000,
        "max_negotiation_rounds": 10,
        "preferred_terms": {"free_wifi": True},
        "vertical_fields": {
            "checkin_date": "2026-04-01",
            "checkout_date": "2026-04-05",
            "occupants": 2,
            "acceptable_room_types": ["double"],
        },
        "timestamp": datetime.utcnow().timestamp(),
    }

    await state_machine.store_intent(session_id, intent_data)
    await order_book.publish_intent(intent_id, intent_data)

    # Step 3: Create seller ask
    ask_data = {
        "ask_id": ask_id,
        "vertical": "hotels",
        "seller_agent_id": seller_id,
        "session_id": session_id,
        "price": 40000,
        "floor_price": 30000,
        "terms": {"free_wifi": True},
        "seller_reputation_score": 85,
        "stake_amount": 5000,
        "vertical_fields": {
            "checkin_date": "2026-04-01",
            "checkout_date": "2026-04-05",
            "room_type": "double",
            "max_occupants": 2,
        },
        "timestamp": datetime.utcnow().timestamp(),
    }

    await state_machine.set_seller(session_id, seller_id)
    await state_machine.store_ask(session_id, ask_data)
    await order_book.publish_ask(ask_id, ask_data)

    # Step 4: Verify order book matching
    matches = await order_book.get_matching_asks(intent_data, limit=5)
    assert len(matches) > 0
    assert ask_id in [m.get("ask_id") for m in matches]

    # Step 5: Transition to NEGOTIATING
    session = await state_machine.transition(session_id, SessionState.MATCHING)
    assert session.state == SessionState.MATCHING
    
    session = await state_machine.transition(session_id, SessionState.NEGOTIATING)
    assert session.state == SessionState.NEGOTIATING

    # Step 6: Buyer accepts
    agreed_price = ask_data["price"]
    session = await state_machine.agree_price(session_id, agreed_price)
    assert session.state == SessionState.AGREED
    assert session.agreed_price == agreed_price

    # Step 7: Transition to SETTLING
    session = await state_machine.transition(session_id, SessionState.SETTLING)
    assert session.state == SessionState.SETTLING

    # Step 8: Transition to COMPLETE
    session = await state_machine.transition(session_id, SessionState.COMPLETE)
    assert session.state == SessionState.COMPLETE

    # Step 9: Verify final state
    final_session = await state_machine.get_session(session_id)
    assert final_session.state == SessionState.COMPLETE
    assert final_session.buyer_agent_id == buyer_id
    assert final_session.seller_agent_id == seller_id
    assert final_session.agreed_price == agreed_price
    
    await redis_conn.aclose()


@pytest.mark.asyncio
async def test_hotel_compatibility():
    """Test hotel vertical schema validation and compatibility checking."""
    from app.verticals.hotels import HotelVerticalValidator

    validator = HotelVerticalValidator()

    # Compatible booking
    intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 2,
        "acceptable_room_types": ["double"],
    }

    ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 2,
    }

    assert validator.check_compatibility(intent, ask)

    # Incompatible: room type doesn't match
    ask_incompatible = ask.copy()
    ask_incompatible["room_type"] = "suite"
    assert not validator.check_compatibility(intent, ask_incompatible)


@pytest.mark.asyncio
async def test_state_machine_timeouts(db_session: AsyncSession):
    """Test state machine timeout detection."""
    state_machine = NegotiationStateMachine(db_session)

    session_id = str(uuid.uuid4())
    buyer_id = str(uuid.uuid4())

    # Create session
    await state_machine.open_session(session_id, buyer_id, "hotels")

    # Check timeouts (should not timeout immediately)
    timed_out = await state_machine.check_timeouts()
    assert len(timed_out) == 0

    # Get session - should still be OPEN
    session = await state_machine.get_session(session_id)
    assert session.state == SessionState.OPEN


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
