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

    async def publish_intent(self, intent_id: str, intent_data: dict) -> str:
        """
        Store buyer intent in Redis.
        
        Key format: ob:bids:hotels (sorted set)
        Stores: JSON intent data with timestamp score
        Returns: intent_id
        """
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

    async def publish_ask(self, ask_id: str, ask_data: dict) -> str:
        """
        Store seller ask in Redis.
        
        Key format: ob:asks:hotels (sorted set)
        Stores: JSON ask data with price score
        Returns: ask_id
        """
        # Support both "price" and "floor_price_cents" field names
        price = ask_data.get("price") or ask_data.get("floor_price_cents", 0)
        
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
        # Support both field name conventions
        budget_ceiling = intent_data.get("budget_ceiling") or intent_data.get("budget_ceiling_cents", 0)
        
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
        # Handle case where vertical_fields exist for hotel vertical
        ask_vertical = ask.get("vertical_fields", ask)
        intent_vertical = intent.get("vertical_fields", intent)
        
        # Check dates if present
        ask_checkin = ask_vertical.get("checkin_date") or ask.get("available_from_date")
        ask_checkout = ask_vertical.get("checkout_date") or ask.get("available_to_date")
        intent_checkin = intent_vertical.get("checkin_date") or intent.get("check_in_date")
        intent_checkout = intent_vertical.get("checkout_date") or intent.get("check_out_date")
        
        if ask_checkin and intent_checkout and ask_checkin > intent_checkout:
            return False
        if ask_checkout and intent_checkin and ask_checkout < intent_checkin:
            return False
        
        # Check room type
        acceptable_types = intent_vertical.get("acceptable_room_types", intent.get("room_types", []))
        ask_room_type = ask_vertical.get("room_type")
        if acceptable_types and ask_room_type and ask_room_type not in acceptable_types:
            return False
        
        # Check occupants
        ask_max_occupants = ask_vertical.get("max_occupants", ask.get("max_occupants", 0))
        intent_occupants = intent_vertical.get("occupants", intent.get("occupants", 0))
        if ask_max_occupants and intent_occupants and ask_max_occupants < intent_occupants:
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
        # Support both field name conventions
        budget_ceiling = intent.get("budget_ceiling") or intent.get("budget_ceiling_cents", 1)
        ask_price = ask.get("price") or ask.get("floor_price_cents", budget_ceiling)
        
        # Price score: 1.0 at $0, 0.0 at budget ceiling
        price_score = 1.0 - (ask_price / budget_ceiling)
        price_score = max(0.0, min(1.0, price_score))
        
        # Terms score: Check if preferred terms match
        terms_score = 1.0
        preferred_terms = intent.get("preferred_terms", {})
        ask_terms = ask.get("terms", {})
        if preferred_terms:
            matches = sum(1 for k, v in preferred_terms.items() if ask_terms.get(k) == v)
            terms_score = matches / len(preferred_terms) if preferred_terms else 1.0
        
        # Reputation score (0-100 → 0-1)
        reputation_score = ask.get("seller_reputation_score", 50) / 100.0
        
        # Stake bonus - support both field names
        stake_amount = ask.get("stake_amount") or ask.get("stake_amount_cents", 0)
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
