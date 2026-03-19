"""Tests for Redis order book."""

import json
import uuid
from datetime import datetime

import pytest
import redis.asyncio as redis

from app.core.order_book import OrderBook


@pytest.fixture
async def order_book():
    """Create an order book with Redis client."""
    # Note: in real tests, would use real Redis or mock it
    client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    book = OrderBook(client)
    yield book
    # Cleanup
    await client.close()


@pytest.mark.asyncio
async def test_publish_intent():
    """Test publishing a buyer intent."""
    client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    book = OrderBook(client)

    intent_id = str(uuid.uuid4())
    intent_data = {
        "intent_id": intent_id,
        "vertical": "hotels",
        "buyer_agent_id": str(uuid.uuid4()),
        "budget_ceiling": 50000,
        "timestamp": datetime.utcnow().timestamp(),
        "preferred_terms": {"free_wifi": True},
    }

    result = await book.publish_intent(intent_id, intent_data)
    assert result == intent_id

    # Verify stored
    stored = await client.get(f"ob:intent:{intent_id}")
    assert stored is not None
    assert json.loads(stored)["intent_id"] == intent_id

    await client.close()


@pytest.mark.asyncio
async def test_publish_ask():
    """Test publishing a seller ask."""
    client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    book = OrderBook(client)

    ask_id = str(uuid.uuid4())
    ask_data = {
        "ask_id": ask_id,
        "vertical": "hotels",
        "seller_agent_id": str(uuid.uuid4()),
        "price": 40000,
        "timestamp": datetime.utcnow().timestamp(),
    }

    result = await book.publish_ask(ask_id, ask_data)
    assert result == ask_id

    # Verify stored
    stored = await client.get(f"ob:ask:{ask_id}")
    assert stored is not None

    await client.close()


@pytest.mark.asyncio
async def test_score_ask():
    """Test ask scoring algorithm."""
    client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    book = OrderBook(client)

    ask_data = {
        "price": 40000,
        "seller_reputation_score": 85,
        "stake_amount": 5000,
        "terms": {"free_wifi": True},
    }

    intent_data = {
        "budget_ceiling": 50000,
        "preferred_terms": {"free_wifi": True},
    }

    score = book._score_ask(ask_data, intent_data)
    
    # Score should be between 0 and 1
    assert 0 <= score <= 1
    # With good price, rep, and matching terms, should score well
    assert score > 0.5

    await client.close()


@pytest.mark.asyncio
async def test_matching_asks():
    """Test finding matching asks for an intent."""
    client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    book = OrderBook(client)

    # Publish a few asks
    ask_data_1 = {
        "ask_id": "ask-1",
        "vertical": "hotels",
        "price": 30000,
        "seller_reputation_score": 90,
        "stake_amount": 10000,
        "terms": {},
        "vertical_fields": {
            "checkin_date": "2026-04-01",
            "checkout_date": "2026-04-05",
            "room_type": "double",
            "max_occupants": 2,
        },
    }

    await book.publish_ask("ask-1", ask_data_1)

    # Intent with budget
    intent_data = {
        "vertical": "hotels",
        "budget_ceiling": 50000,
        "preferred_terms": {},
    }

    # Find matches
    matches = await book.get_matching_asks(intent_data, limit=5)
    assert len(matches) > 0
    assert matches[0]["ask_id"] == "ask-1"

    await client.close()
