"""Redis-based order book for intent/ask matching and storage."""

import json
from typing import Optional, List
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel

from app.config import settings


class OrderBook:
    """Manage buyer intents and seller asks in Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = settings.order_book_ttl_seconds

    async def publish_intent(self, intent_data: dict) -> str:
        """
        Store buyer intent in Redis.
        
        Key format: ob:bids:hotels (sorted set)
        Stores: JSON intent data with timestamp score
        Returns: intent_id
        """
        intent_id = f"intent_{uuid4().hex[:12]}"
        timestamp = intent_data.get("timestamp", 0)
        
        # Store in sorted set (score = timestamp)
        await self.redis.zadd(
            "ob:bids:hotels",
            {intent_id: timestamp}
        )
        
        # Store full intent data
        await self.redis.setex(
            f"ob:intent:{intent_id}",
            self.ttl,
            json.dumps(intent_data)
        )
        
        return intent_id

    async def publish_ask(self, ask_data: dict) -> str:
        """
        Store seller ask in Redis.
        
        Key format: ob:asks:hotels (sorted set)
        Stores: JSON ask data with price score
        Returns: ask_id
        """
        ask_id = f"ask_{uuid4().hex[:12]}"
        price = ask_data.get("floor_price_cents", 0)
        
        # Store in sorted set (score = price for ascending order)
        await self.redis.zadd(
            "ob:asks:hotels",
            {ask_id: price}
        )
        
        # Store full ask data
        await self.redis.setex(
            f"ob:ask:{ask_id}",
            self.ttl,
            json.dumps(ask_data)
        )
        
        return ask_id

    async def get_matching_asks(
        self,
        intent_data: dict,
        limit: int = 5
    ) -> List[dict]:
        """
        Get asks matching buyer intent.
        
        1. ZRANGEBYSCORE to filter by price
        2. Fetch full ask data
        3. Score remaining asks
        4. Return top `limit` sorted by score
        """
        budget_ceiling = intent_data.get("budget_ceiling_cents", 0)
        
        # Get asks within budget (price <= budget_ceiling)
        ask_ids = await self.redis.zrangebyscore(
            "ob:asks:hotels",
            min=0,
            max=budget_ceiling,
            start=0,
            num=limit * 2  # Fetch more to account for filtering
        )
        
        # Fetch full asks
        asks = []
        for ask_id in ask_ids:
            ask_json = await self.redis.get(f"ob:ask:{ask_id}")
            if ask_json:
                ask_data = json.loads(ask_json)
                ask_data["ask_id"] = ask_id
                asks.append(ask_data)
        
        # Score and sort
        scored_asks = [
            (ask, self._score_ask(ask, intent_data))
            for ask in asks
            if self._is_compatible(ask, intent_data)
        ]
        
        # Sort by score (highest first)
        scored_asks.sort(key=lambda x: x[1], reverse=True)
        
        # Return top `limit` asks without scores
        return [ask for ask, _ in scored_asks[:limit]]

    async def remove_intent(self, intent_id: str) -> None:
        """Remove intent from order book."""
        await self.redis.zrem("ob:bids:hotels", intent_id)
        await self.redis.delete(f"ob:intent:{intent_id}")

    async def remove_ask(self, ask_id: str) -> None:
        """Remove ask from order book."""
        await self.redis.zrem("ob:asks:hotels", ask_id)
        await self.redis.delete(f"ob:ask:{ask_id}")

    async def get_active_intent_count(self, agent_id: str) -> int:
        """Count active intents for an agent (rate limiting)."""
        all_intents = await self.redis.zrange("ob:bids:hotels", 0, -1)
        count = 0
        
        for intent_id in all_intents:
            intent_json = await self.redis.get(f"ob:intent:{intent_id}")
            if intent_json:
                intent_data = json.loads(intent_json)
                if intent_data.get("sender_id") == agent_id:
                    count += 1
        
        return count

    def _is_compatible(self, ask: dict, intent: dict) -> bool:
        """Check if ask matches intent requirements."""
        # Check dates
        if (
            ask.get("available_from_date") > intent.get("check_out_date") or
            ask.get("available_to_date") < intent.get("check_in_date")
        ):
            return False
        
        # Check room type
        acceptable_types = intent.get("room_types", [])
        if acceptable_types and ask.get("room_type") not in acceptable_types:
            return False
        
        # Check occupants
        if ask.get("max_occupants", 0) < intent.get("occupants", 0):
            return False
        
        return True

    def _score_ask(self, ask: dict, intent: dict) -> float:
        """
        Score an ask against an intent.
        
        Formula:
        - price_score (0.40): How close to budget
        - terms_score (0.35): Matching terms
        - reputation_score (0.15): Seller reputation
        - stake_bonus (0.10): Performance bond
        """
        budget_ceiling = intent.get("budget_ceiling_cents", 1)
        ask_price = ask.get("floor_price_cents", budget_ceiling)
        
        # Price score: 1.0 at $0, 0.0 at budget ceiling
        price_score = 1.0 - (ask_price / budget_ceiling)
        price_score = max(0.0, min(1.0, price_score))
        
        # Terms score (placeholder - all terms match for now)
        terms_score = 1.0
        
        # Reputation score (0-100 → 0-1)
        reputation_score = ask.get("seller_reputation_score", 50) / 100.0
        
        # Stake bonus
        stake_amount = ask.get("stake_amount_cents", 0)
        stake_bonus = 0.0
        if stake_amount >= 10000:
            stake_bonus = 0.10
        elif stake_amount >= 2500:
            stake_bonus = 0.08
        elif stake_amount >= 500:
            stake_bonus = 0.05
        elif stake_amount >= 100:
            stake_bonus = 0.02
        
        # Combined score
        total = (
            (price_score * 0.40) +
            (terms_score * 0.35) +
            (reputation_score * 0.15) +
            (stake_bonus * 0.10)
        )
        
        return total
