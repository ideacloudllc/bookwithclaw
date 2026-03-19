"""
BookWithClaw — Order Book State Machine

The core matching engine that:
1. Accepts BuyerIntent and SellerAsk messages
2. Validates schema compatibility
3. Scores and ranks matches
4. Routes top 5 to private negotiation sessions
5. Manages session lifecycle (pending → negotiating → accepted → settled)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json

from messages import (
    BuyerIntentMessage, SellerAskMessage, 
    DealAcceptedMessage, SessionState, PartyType
)


# ============================================================================
# Order Book Entry Types
# ============================================================================

@dataclass
class OrderBookEntry:
    """Single entry in the order book (intent or ask)."""
    
    entry_id: str  # intent_id or ask_id
    entry_type: str  # "bid" (buyer) or "ask" (seller)
    sender_id: str  # agent-buyer-001 or agent-seller-xyz
    vertical: str  # "Hotels", "Freight", etc.
    price_level: float  # budget_ceiling (bid) or published_price (ask)
    state: SessionState = SessionState.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(seconds=120))
    original_message: Dict = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    @property
    def ttl_remaining_seconds(self) -> int:
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))


@dataclass
class NegotiationSession:
    """Private session between buyer and seller."""
    
    session_id: str
    intent_id: str  # Reference to buyer intent
    ask_id: str  # Reference to seller ask
    buyer_agent_id: str
    seller_agent_id: str
    state: SessionState = SessionState.NEGOTIATING
    round_num: int = 0
    max_rounds: int = 5
    last_buyer_offer: Optional[float] = None
    last_seller_offer: Optional[float] = None
    last_buyer_terms: Optional[Dict] = None
    last_seller_terms: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=30))
    compatibility_score: float = 0.0  # 0-100
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    @property
    def ttl_remaining_seconds(self) -> int:
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))


# ============================================================================
# Matching Algorithm
# ============================================================================

class MatchingAlgorithm:
    """Implements the 5-step matching algorithm."""
    
    @staticmethod
    def hard_filter(
        buyer_ceiling: float,
        seller_asks: List[SellerAskMessage]
    ) -> List[SellerAskMessage]:
        """Step 1: Remove all asks where published_price > buyer_ceiling."""
        return [ask for ask in seller_asks 
                if ask.body.get("published_price", 0) <= buyer_ceiling]
    
    @staticmethod
    def schema_validate(
        buyer_requirements: Dict,
        seller_inventory: Dict,
        vertical: str
    ) -> bool:
        """
        Step 2: Ensure ask fields satisfy buyer's vertical schema requirements.
        
        For Hotels: checkin/checkout overlap, room count >= persons, etc.
        For Freight: destination match, cargo type match, capacity, etc.
        """
        if vertical.lower() == "hotels":
            return MatchingAlgorithm._validate_hotel_schema(
                buyer_requirements, seller_inventory
            )
        # Add other verticals as needed
        return True
    
    @staticmethod
    def _validate_hotel_schema(buyer_req: Dict, seller_inv: Dict) -> bool:
        """Hotel-specific schema validation."""
        # Check location match
        buyer_loc = buyer_req.get("location", "").lower()
        seller_loc = seller_inv.get("location", "").lower()
        if buyer_loc and seller_loc and buyer_loc not in seller_loc:
            return False
        
        # Check date overlap
        buyer_checkin = buyer_req.get("checkin")
        buyer_checkout = buyer_req.get("checkout")
        seller_checkin = seller_inv.get("checkin")
        seller_checkout = seller_inv.get("checkout")
        
        if buyer_checkin and seller_checkout and buyer_checkin > seller_checkout:
            return False
        if buyer_checkout and seller_checkin and buyer_checkout < seller_checkin:
            return False
        
        # Check room count
        buyer_rooms = buyer_req.get("rooms", 0)
        seller_rooms = seller_inv.get("available_rooms", 0)
        if buyer_rooms > seller_rooms:
            return False
        
        return True
    
    @staticmethod
    def compatibility_score(
        buyer_intent: BuyerIntentMessage,
        seller_ask: SellerAskMessage,
        buyer_ceiling: float,
        seller_floor: float,
    ) -> float:
        """
        Step 3: Compatibility scoring
        
        - Price proximity (40%): How close is ask to buyer's ceiling?
        - Terms match (35%): Do terms align?
        - Reputation (15%): Seller's historical quality
        - Token stake (10%): Higher stake = higher trust signal
        """
        
        score = 0.0
        
        # Price proximity (40%)
        # Score = 100 if ask == ceiling, drops to 0 at floor
        published_price = seller_ask.body.get("published_price", buyer_ceiling)
        floor_price = seller_ask.body.get("floor_price", published_price)
        
        price_range = buyer_ceiling - floor_price
        if price_range > 0:
            distance_from_ceiling = buyer_ceiling - published_price
            price_proximity = max(0, 100 * (1 - distance_from_ceiling / price_range))
        else:
            price_proximity = 100 if published_price <= buyer_ceiling else 0
        
        score += price_proximity * 0.40
        
        # Terms match (35%)
        buyer_walkaway = buyer_intent.body.get("walkaway_conditions", {})
        seller_terms = seller_ask.body.get("terms", {})
        must_haves = buyer_walkaway.get("must_have_terms", [])
        
        terms_match = 100.0
        for must_have in must_haves:
            if must_have not in seller_terms or not seller_terms.get(must_have):
                terms_match = 0
                break
        
        score += terms_match * 0.35
        
        # Reputation (15%)
        # Placeholder: assume 50% reputation for now
        reputation_score = 50.0
        score += reputation_score * 0.15
        
        # Token stake (10%)
        # Tiers: 0 (0pts), 100 (25pts), 500 (50pts), 2500 (75pts), 10000+ (100pts)
        token_stake = seller_ask.body.get("token_stake", 0)
        stake_score = {
            0: 0,
            100: 25,
            500: 50,
            2500: 75,
            10000: 100,
        }.get(token_stake, 0)
        score += stake_score * 0.10
        
        return min(100.0, max(0.0, score))
    
    @staticmethod
    def score_and_rank(
        buyer_intent: BuyerIntentMessage,
        seller_asks: List[SellerAskMessage],
    ) -> List[Tuple[SellerAskMessage, float]]:
        """
        Compute compatibility score for all viable asks,
        then rank from highest to lowest.
        
        Returns: List of (ask, score) tuples, sorted by score descending.
        """
        buyer_ceiling = buyer_intent.body.get("budget_ceiling", 0)
        buyer_requirements = buyer_intent.body.get("requirements", {})
        vertical = buyer_intent.body.get("vertical", "")
        
        scored = []
        for ask in seller_asks:
            seller_floor = ask.body.get("floor_price", ask.body.get("published_price", 0))
            
            # Validate schema compatibility
            seller_inventory = ask.body.get("inventory", {})
            if not MatchingAlgorithm.schema_validate(buyer_requirements, seller_inventory, vertical):
                continue  # Skip this ask
            
            # Compute score
            score = MatchingAlgorithm.compatibility_score(
                buyer_intent, ask, buyer_ceiling, seller_floor
            )
            scored.append((ask, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


# ============================================================================
# Order Book
# ============================================================================

class OrderBook:
    """Central order book managing intents, asks, and sessions."""
    
    def __init__(self):
        """Initialize empty order book."""
        self.intents: Dict[str, BuyerIntentMessage] = {}  # intent_id -> message
        self.asks: Dict[str, SellerAskMessage] = {}  # ask_id -> message
        self.sessions: Dict[str, NegotiationSession] = {}  # session_id -> session
        self.intent_sessions: Dict[str, List[str]] = {}  # intent_id -> [session_ids]
        self.ask_sessions: Dict[str, List[str]] = {}  # ask_id -> [session_ids]
    
    # ========== Intent Management ==========
    
    def post_intent(self, msg: BuyerIntentMessage) -> bool:
        """
        Post a new buyer intent to the order book.
        
        Returns: True if accepted, False if duplicate/invalid.
        """
        intent_id = msg.body.get("intent_id")
        if not intent_id:
            return False
        
        # Reject duplicates (already posted within 10s)
        if intent_id in self.intents:
            existing = self.intents[intent_id]
            # Parse timestamp string to datetime (strip Z and parse as naive UTC)
            existing_ts = datetime.fromisoformat(existing.timestamp.rstrip('Z'))
            age = (datetime.utcnow() - existing_ts).total_seconds()
            if age < 10:
                return False  # Duplicate, ignored
            else:
                # Old intent, allow replacement
                pass
        
        self.intents[intent_id] = msg
        self.intent_sessions[intent_id] = []
        return True
    
    def get_intent(self, intent_id: str) -> Optional[BuyerIntentMessage]:
        """Retrieve an intent by ID."""
        return self.intents.get(intent_id)
    
    def cleanup_expired_intents(self) -> List[str]:
        """Remove expired intents. Returns list of removed intent_ids."""
        expired = []
        for intent_id, msg in list(self.intents.items()):
            ttl = msg.body.get("ttl_seconds", 120)
            age = (datetime.utcnow() - msg.timestamp).total_seconds()
            if age > ttl:
                expired.append(intent_id)
                del self.intents[intent_id]
        return expired
    
    # ========== Ask Management ==========
    
    def post_ask(self, msg: SellerAskMessage) -> bool:
        """
        Post a new seller ask to the order book.
        
        Returns: True if accepted, False if duplicate/invalid.
        """
        ask_id = msg.body.get("ask_id")
        if not ask_id:
            return False
        
        # Reject duplicates (within 10s)
        if ask_id in self.asks:
            existing = self.asks[ask_id]
            # Parse timestamp string to datetime (strip Z and parse as naive UTC)
            existing_ts = datetime.fromisoformat(existing.timestamp.rstrip('Z'))
            age = (datetime.utcnow() - existing_ts).total_seconds()
            if age < 10:
                return False
        
        self.asks[ask_id] = msg
        self.ask_sessions[ask_id] = []
        return True
    
    def get_ask(self, ask_id: str) -> Optional[SellerAskMessage]:
        """Retrieve an ask by ID."""
        return self.asks.get(ask_id)
    
    def cleanup_expired_asks(self) -> List[str]:
        """Remove expired asks. Returns list of removed ask_ids."""
        expired = []
        for ask_id, msg in list(self.asks.items()):
            ttl = msg.body.get("expiry_seconds", 180)
            age = (datetime.utcnow() - msg.timestamp).total_seconds()
            if age > ttl:
                expired.append(ask_id)
                del self.asks[ask_id]
        return expired
    
    # ========== Matching (5-Step Algorithm) ==========
    
    def find_matches_for_intent(self, intent: BuyerIntentMessage) -> List[Tuple[SellerAskMessage, float]]:
        """
        Step 1-3: Filter, validate, score all viable asks for a given intent.
        """
        buyer_ceiling = intent.body.get("budget_ceiling", 0)
        buyer_vertical = intent.body.get("vertical", "")
        
        # Get all active asks for this vertical
        vertical_asks = [ask for ask in self.asks.values()
                        if ask.body.get("vertical") == buyer_vertical]
        
        # Step 1: Hard filter (price ceiling)
        filtered = MatchingAlgorithm.hard_filter(buyer_ceiling, vertical_asks)
        
        # Step 2 & 3: Validate schema + score compatibility
        scored = MatchingAlgorithm.score_and_rank(intent, filtered)
        
        return scored
    
    # ========== Session Management ==========
    
    def create_sessions_for_intent(self, intent_id: str, max_sessions: int = 5) -> List[NegotiationSession]:
        """
        Step 4: Route top N matches to private negotiation sessions.
        
        Returns: List of created sessions.
        """
        intent = self.get_intent(intent_id)
        if not intent:
            return []
        
        # Find and score matches
        matches = self.find_matches_for_intent(intent)
        if not matches:
            return []
        
        # Take top max_sessions
        created = []
        for ask, score in matches[:max_sessions]:
            session = self._create_session(intent, ask, score)
            created.append(session)
        
        return created
    
    def _create_session(
        self,
        intent: BuyerIntentMessage,
        ask: SellerAskMessage,
        score: float
    ) -> NegotiationSession:
        """Create a private negotiation session."""
        import uuid
        
        intent_id = intent.body.get("intent_id")
        ask_id = ask.body.get("ask_id")
        session_id = f"sess-{ask_id}-{intent_id}-{uuid.uuid4().hex[:8]}"
        
        session = NegotiationSession(
            session_id=session_id,
            intent_id=intent_id,
            ask_id=ask_id,
            buyer_agent_id=intent.sender_id,
            seller_agent_id=ask.sender_id,
            max_rounds=intent.body.get("max_negotiation_rounds", 5),
            compatibility_score=score,
        )
        
        self.sessions[session_id] = session
        self.intent_sessions[intent_id].append(session_id)
        self.ask_sessions[ask_id].append(session_id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[NegotiationSession]:
        """Retrieve a negotiation session."""
        return self.sessions.get(session_id)
    
    # ========== Deal Acceptance (Step 5) ==========
    
    def accept_deal(self, msg: DealAcceptedMessage) -> bool:
        """
        Step 5: First accepted deal wins.
        
        When a deal is accepted:
        1. Mark this session as ACCEPTED
        2. Terminate all OTHER sessions for this intent
        3. Return True
        """
        intent_id = msg.body.get("intent_id")
        ask_id = msg.body.get("ask_id")
        session_id = msg.body.get("session_id")
        
        session = self.get_session(session_id)
        if not session or session.state != SessionState.NEGOTIATING:
            return False
        
        # Mark this session as accepted
        session.state = SessionState.ACCEPTED
        
        # Terminate all OTHER sessions for this intent
        other_sessions = self.intent_sessions.get(intent_id, [])
        for other_id in other_sessions:
            if other_id != session_id:
                other = self.get_session(other_id)
                if other and other.state == SessionState.NEGOTIATING:
                    other.state = SessionState.FAILED
        
        return True
    
    # ========== Cleanup ==========
    
    def cleanup_expired_sessions(self) -> List[str]:
        """Remove expired negotiation sessions."""
        expired = []
        for session_id, session in list(self.sessions.items()):
            if session.is_expired or session.state in [SessionState.SETTLED, SessionState.FAILED]:
                expired.append(session_id)
                del self.sessions[session_id]
        return expired
    
    def cleanup_all(self) -> Dict:
        """Run all cleanup routines. Returns summary."""
        return {
            "expired_intents": self.cleanup_expired_intents(),
            "expired_asks": self.cleanup_expired_asks(),
            "expired_sessions": self.cleanup_expired_sessions(),
        }
    
    # ========== Stats & Introspection ==========
    
    def stats(self) -> Dict:
        """Return current order book statistics."""
        return {
            "total_intents": len(self.intents),
            "total_asks": len(self.asks),
            "total_sessions": len(self.sessions),
            "sessions_by_state": {
                state.value: sum(1 for s in self.sessions.values() if s.state == state)
                for state in SessionState
            }
        }


if __name__ == "__main__":
    # Quick sanity test
    from messages import create_test_buyer_intent, create_test_seller_ask
    
    ob = OrderBook()
    
    # Post a buyer intent
    intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
    ob.post_intent(intent)
    print(f"✓ Posted intent: {intent.body.get('intent_id')}")
    
    # Post multiple seller asks
    for i in range(3):
        ask = create_test_seller_ask(
            f"ASK-{i:03d}",
            "Hotels",
            published_price=200 + (i * 15),
            floor_price=190 + (i * 15),
        )
        ob.post_ask(ask)
        print(f"✓ Posted ask: {ask.body.get('ask_id')} @ ${ask.body.get('published_price')}")
    
    print()
    
    # Find matches
    matches = ob.find_matches_for_intent(intent)
    print(f"Found {len(matches)} matches:")
    for ask, score in matches:
        print(f"  {ask.body.get('ask_id')} — Score: {score:.1f}")
    
    print()
    
    # Create negotiation sessions
    sessions = ob.create_sessions_for_intent("BID-001", max_sessions=2)
    print(f"Created {len(sessions)} negotiation sessions:")
    for session in sessions:
        print(f"  {session.session_id}: {session.buyer_agent_id} ↔ {session.seller_agent_id}")
    
    print()
    print("Order Book Stats:", ob.stats())
