"""Redis-based order book for buyer intents and seller asks."""

import json
from typing import Optional

import redis.asyncio as redis
from pydantic import BaseModel

from app.config import settings


class OrderBookEntry(BaseModel):
    """Entry in the order book."""

    id: str
    vertical: str
    agent_id: str
    data: dict
    timestamp: float


class OrderBook:
    """Redis-backed order book for buyer intents and seller asks."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = settings.order_book_ttl_seconds

    async def publish_intent(self, intent_id: str, intent_data: dict) -> str:
        """
        Publish a buyer intent to the order book.

        Args:
            intent_id: Unique intent identifier
            intent_data: Intent payload (includes vertical, timestamp, etc.)

        Returns:
            The intent_id
        """
        vertical = intent_data.get("vertical", "unknown")
        timestamp = intent_data.get("timestamp", 0)

        # Store in sorted set: score = timestamp (for FIFO ordering)
        key = f"ob:intents:{vertical}"
        await self.redis.zadd(key, {intent_id: timestamp}, ex=self.ttl)

        # Store full intent data
        data_key = f"ob:intent:{intent_id}"
        await self.redis.set(
            data_key,
            json.dumps(intent_data),
            ex=self.ttl,
        )

        return intent_id

    async def publish_ask(self, ask_id: str, ask_data: dict) -> str:
        """
        Publish a seller ask to the order book.

        Args:
            ask_id: Unique ask identifier
            ask_data: Ask payload (includes vertical, price, etc.)

        Returns:
            The ask_id
        """
        vertical = ask_data.get("vertical", "unknown")
        price = ask_data.get("price", 999999999)  # High default

        # Store in sorted set: score = price (for price ordering)
        key = f"ob:asks:{vertical}"
        await self.redis.zadd(key, {ask_id: price}, ex=self.ttl)

        # Store full ask data
        data_key = f"ob:ask:{ask_id}"
        await self.redis.set(
            data_key,
            json.dumps(ask_data),
            ex=self.ttl,
        )

        return ask_id

    async def get_matching_asks(
        self,
        intent_data: dict,
        limit: int = 5,
    ) -> list[dict]:
        """
        Find matching asks for a buyer intent.

        Steps:
        1. Filter asks by price (must be <= buyer's budget_ceiling)
        2. Validate against vertical schema
        3. Score each ask
        4. Return top `limit` sorted by score descending

        Args:
            intent_data: Buyer intent payload
            limit: Max number of asks to return

        Returns:
            List of matching ask data dicts, sorted by score descending
        """
        vertical = intent_data.get("vertical", "unknown")
        budget_ceiling = intent_data.get("budget_ceiling", 0)

        key = f"ob:asks:{vertical}"

        # Step 1: Price filter (ZRANGEBYSCORE: 0 to budget_ceiling)
        ask_ids = await self.redis.zrangebyscore(key, 0, budget_ceiling, start=0, num=100)

        if not ask_ids:
            return []

        # Step 2-3: Fetch full data and score each ask
        matches = []
        for ask_id in ask_ids:
            ask_id_str = ask_id.decode() if isinstance(ask_id, bytes) else ask_id
            data_key = f"ob:ask:{ask_id_str}"
            ask_json = await self.redis.get(data_key)

            if not ask_json:
                continue

            ask_data = json.loads(ask_json)

            # Validate against vertical schema (simplified - in production use verticals registry)
            if not self._validate_vertical(vertical, ask_data):
                continue

            # Score this ask
            score = self._score_ask(ask_data, intent_data)
            matches.append((ask_data, score))

        # Step 4: Sort by score descending and return top `limit`
        matches.sort(key=lambda x: x[1], reverse=True)
        return [ask_data for ask_data, _ in matches[:limit]]

    async def remove_intent(self, intent_id: str, vertical: str = "hotels") -> None:
        """Remove intent from order book."""
        key = f"ob:intents:{vertical}"
        await self.redis.zrem(key, intent_id)
        await self.redis.delete(f"ob:intent:{intent_id}")

    async def remove_ask(self, ask_id: str, vertical: str = "hotels") -> None:
        """Remove ask from order book."""
        key = f"ob:asks:{vertical}"
        await self.redis.zrem(key, ask_id)
        await self.redis.delete(f"ob:ask:{ask_id}")

    async def get_active_intent_count(self, agent_id: str, vertical: str = "hotels") -> int:
        """Count active intents for rate limiting."""
        # Simplified: count all intents for now
        # In production, would track per-agent
        key = f"ob:intents:{vertical}"
        count = await self.redis.zcard(key)
        return count or 0

    # Private helpers

    def _validate_vertical(self, vertical: str, data: dict) -> bool:
        """Validate data against vertical schema."""
        if vertical == "hotels":
            # Check required hotel fields in vertical_fields
            vf = data.get("vertical_fields", {})
            required = {"checkin_date", "checkout_date", "room_type", "max_occupants"}
            return all(k in vf for k in required)
        return True

    def _score_ask(self, ask_data: dict, intent_data: dict) -> float:
        """
        Score an ask against an intent.

        Formula:
        - price_score (40%): 1.0 when price=0, 0.0 when price=budget_ceiling
        - terms_score (35%): fraction of intent terms satisfied by ask
        - reputation_score (15%): normalized to 0-1
        - stake_bonus (10%): tiered bonus for high stake amounts
        """
        budget = intent_data.get("budget_ceiling", 1)
        price = ask_data.get("price", budget)

        # Price score: 1.0 - (price / budget)
        price_score = max(0, 1.0 - (price / budget))

        # Terms score
        intent_terms = intent_data.get("preferred_terms", {})
        ask_terms = ask_data.get("terms", {})
        if intent_terms:
            satisfied = sum(
                1 for k, v in intent_terms.items() if ask_terms.get(k) == v
            )
            terms_score = satisfied / len(intent_terms)
        else:
            terms_score = 1.0

        # Reputation score (0-100 -> 0-1)
        rep_score = ask_data.get("seller_reputation_score", 0) / 100.0

        # Stake bonus
        stake = ask_data.get("stake_amount", 0)
        stake_bonus = 0.0
        if stake >= 10000:
            stake_bonus = 0.10
        elif stake >= 2500:
            stake_bonus = 0.08
        elif stake >= 500:
            stake_bonus = 0.05
        elif stake >= 100:
            stake_bonus = 0.02

        # Weighted score
        return (
            (price_score * 0.40)
            + (terms_score * 0.35)
            + (rep_score * 0.15)
            + (stake_bonus * 0.10)
        )
