"""
BookWithClaw — Message Type Definitions

All inter-agent messages flowing through the AgentBook Exchange.
Each message is JSON-serializable with Ed25519 signature support.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Literal
from enum import Enum
import json
from datetime import datetime
import uuid

# ============================================================================
# Message Enums
# ============================================================================

class MessageType(str, Enum):
    """All valid message types."""
    BUYER_INTENT = "BuyerIntent"
    SELLER_ASK = "SellerAsk"
    BUYER_COUNTER_OFFER = "BuyerCounterOffer"
    SELLER_COUNTER_OFFER = "SellerCounterOffer"
    DEAL_ACCEPTED = "DealAccepted"
    SETTLEMENT_PHASE1 = "SettlementPhase1"
    SETTLEMENT_PHASE1_COMMIT = "SettlementPhase1Commit"
    SETTLEMENT_COMPLETE = "SettlementComplete"
    SETTLEMENT_FAILED = "SettlementFailed"


class SessionState(str, Enum):
    """Order book / session states."""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    SETTLED = "settled"
    FAILED = "failed"


class PartyType(str, Enum):
    """Settlement party type."""
    BUYER = "buyer"
    SELLER = "seller"


class SettlementStatus(str, Enum):
    """Settlement completion status."""
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Base Message
# ============================================================================

@dataclass
class BaseMessage:
    """Base class for all messages. Provides common structure."""
    
    msg_type: MessageType
    msg_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:12]}")
    sender_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    body: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None  # "ed25519:base64(...)"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    
    def canonical_json(self) -> str:
        """Generate canonical JSON for signature validation (no whitespace, sorted keys)."""
        canonical = {
            "msg_type": self.msg_type.value,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "body": self.body,
        }
        return json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "msg_type": self.msg_type.value,
            "msg_id": self.msg_id,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "body": self.body,
            "signature": self.signature,
            "nonce": self.nonce,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


# ============================================================================
# L2 Protocol Messages (Order Book & Negotiation)
# ============================================================================

@dataclass
class BuyerIntentMessage(BaseMessage):
    """
    Buyer declares what they want to buy.
    
    Direction: Buyer Agent → Exchange
    Visibility: Exchange + visible to Seller Agents only
    Signed: Yes
    Idempotent: Yes (within 10s)
    """
    
    msg_type: MessageType = MessageType.BUYER_INTENT
    
    @dataclass
    class Body:
        intent_id: str  # e.g., "BID-0041"
        vertical: str  # e.g., "Hotels", "Freight"
        requirements: Dict[str, Any]  # Vertical-specific requirements
        budget_ceiling: float  # Max willing to pay
        currency: str = "USD"
        max_negotiation_rounds: int = 5
        walkaway_conditions: Dict[str, Any] = field(default_factory=dict)
        preferred_payment: str = "card"
        ttl_seconds: int = 120  # Time-to-live
        buyer_public_key: str = ""  # Ed25519 public key
        buyer_sig: str = ""  # Signature of (buyer_id || intent_id || budget || timestamp)
    
    def set_body(self, body: Body):
        """Set message body from typed Body object."""
        self.body = asdict(body)


@dataclass
class SellerAskMessage(BaseMessage):
    """
    Seller publishes what they have available.
    
    Direction: Seller Agent → Exchange
    Visibility: Exchange + visible to Buyer Agents only
    Signed: Yes
    Idempotent: Yes (within 10s)
    """
    
    msg_type: MessageType = MessageType.SELLER_ASK
    
    @dataclass
    class Body:
        ask_id: str  # e.g., "ASK-8801"
        vertical: str  # e.g., "Hotels"
        listing_id: str  # Seller's internal inventory ID
        inventory: Dict[str, Any]  # Vertical-specific inventory details
        published_price: float
        floor_price: float  # Minimum acceptable (floor <= published)
        currency: str = "USD"
        terms: Dict[str, Any] = field(default_factory=dict)
        discount_authority: float = 0.0  # Max discount seller can grant (0-0.5)
        token_stake: int = 0  # ABT tokens staked (0, 100, 500, 2500, 10000+)
        token_stake_proof: str = ""  # Hash proof of stake
        expiry_seconds: int = 180
        seller_public_key: str = ""
        seller_sig: str = ""
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class BuyerCounterOfferMessage(BaseMessage):
    """
    Buyer negotiates price/terms downward during private session.
    
    Direction: Buyer Agent → Exchange (private session)
    Visibility: Exchange + target Seller Agent only
    Signed: Yes
    Idempotent: No (each counter is unique)
    """
    
    msg_type: MessageType = MessageType.BUYER_COUNTER_OFFER
    
    @dataclass
    class Body:
        intent_id: str
        ask_id: str
        session_id: str
        round_num: int
        counter_price: float
        requested_terms: Dict[str, Any] = field(default_factory=dict)
        rationale: str = ""
        buyer_sig: str = ""  # Signature of this counter
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class SellerCounterOfferMessage(BaseMessage):
    """
    Seller negotiates price/terms. Cannot go below floor_price.
    
    Direction: Seller Agent → Exchange (private session)
    Visibility: Exchange + target Buyer Agent only
    Signed: Yes
    Idempotent: No
    """
    
    msg_type: MessageType = MessageType.SELLER_COUNTER_OFFER
    
    @dataclass
    class Body:
        intent_id: str
        ask_id: str
        session_id: str
        round_num: int
        revised_price: float
        granted_terms: Dict[str, Any] = field(default_factory=dict)
        terms_explanation: str = ""
        seller_sig: str = ""
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class DealAcceptedMessage(BaseMessage):
    """
    One party accepts the most recent offer. Locks both into settlement.
    
    Direction: Either party → Exchange
    Visibility: Exchange + both parties
    Signed: Yes
    Idempotent: Yes (only first acceptance matters)
    """
    
    msg_type: MessageType = MessageType.DEAL_ACCEPTED
    
    @dataclass
    class Body:
        intent_id: str
        ask_id: str
        session_id: str
        final_price: float
        final_terms: Dict[str, Any] = field(default_factory=dict)
        accepting_party: PartyType = PartyType.BUYER
        accepting_sig: str = ""  # Signature of acceptance
    
    def set_body(self, body: Body):
        self.body = asdict(body)


# ============================================================================
# L3 Settlement Messages (Two-Phase Commit)
# ============================================================================

@dataclass
class SettlementPhase1Message(BaseMessage):
    """
    Exchange sends both parties canonical settlement record for co-signature.
    
    Direction: Exchange → Both parties
    Visibility: Private
    Signed: Yes (by exchange)
    """
    
    msg_type: MessageType = MessageType.SETTLEMENT_PHASE1
    
    @dataclass
    class Body:
        intent_id: str
        ask_id: str
        session_id: str
        settlement_id: str
        booking_ref: str  # Customer-facing booking reference
        buyer_agent_id: str
        seller_agent_id: str
        final_price: float
        final_terms: Dict[str, Any] = field(default_factory=dict)
        escrow_amount: float = 0.0
        platform_fee: float = 0.0
        seller_receives: float = 0.0
        currency: str = "USD"
        phase1_timeout_seconds: int = 30
        canonical_msg: str = ""  # JSON for co-sig
        exchange_sig: str = ""  # Exchange signature
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class SettlementPhase1CommitMessage(BaseMessage):
    """
    Both parties respond with co-signature commitment.
    
    Direction: Both → Exchange
    Visibility: Private
    Signed: Yes
    """
    
    msg_type: MessageType = MessageType.SETTLEMENT_PHASE1_COMMIT
    
    @dataclass
    class Body:
        settlement_id: str
        commitment: Literal["accepted", "rejected"]
        buyer_sig_phase1: Optional[str] = None
        seller_sig_phase1: Optional[str] = None
        rejection_reason: str = ""
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class SettlementCompleteMessage(BaseMessage):
    """
    Settlement executed. Payment transferred, inventory confirmed, rewards queued.
    
    Direction: Exchange → Both parties
    Visibility: Public (recorded in ledger)
    Signed: Yes (by exchange)
    """
    
    msg_type: MessageType = MessageType.SETTLEMENT_COMPLETE
    
    @dataclass
    class Body:
        settlement_id: str
        booking_ref: str
        status: SettlementStatus = SettlementStatus.COMPLETED
        final_price: float = 0.0
        platform_fee: float = 0.0
        seller_received: float = 0.0
        currency: str = "USD"
        buyer_rewards: int = 0  # ABT tokens rewarded
        seller_rewards: int = 0
        tx_hash: str = ""  # Transaction hash (if on-chain)
        completion_timestamp: str = ""
        exchange_sig: str = ""
    
    def set_body(self, body: Body):
        self.body = asdict(body)


@dataclass
class SettlementFailedMessage(BaseMessage):
    """
    Settlement failed. Escrow released, parties notified.
    
    Direction: Exchange → Both parties
    Visibility: Public (recorded in ledger)
    Signed: Yes (by exchange)
    """
    
    msg_type: MessageType = MessageType.SETTLEMENT_FAILED
    
    @dataclass
    class Body:
        settlement_id: str
        status: SettlementStatus = SettlementStatus.FAILED
        failure_reason: str = ""  # e.g., "Seller inventory hold failed"
        escrow_status: Literal["released", "held"] = "released"
        slash_amount: float = 0.0  # ABT tokens slashed (if applicable)
        slash_reason: str = ""
        exchange_sig: str = ""
    
    def set_body(self, body: Body):
        self.body = asdict(body)


# ============================================================================
# Message Factory
# ============================================================================

def message_from_dict(data: Dict[str, Any]) -> BaseMessage:
    """Deserialize a message from a dictionary."""
    msg_type_str = data.get("msg_type")
    
    # Map message type to class
    message_classes = {
        "BuyerIntent": BuyerIntentMessage,
        "SellerAsk": SellerAskMessage,
        "BuyerCounterOffer": BuyerCounterOfferMessage,
        "SellerCounterOffer": SellerCounterOfferMessage,
        "DealAccepted": DealAcceptedMessage,
        "SettlementPhase1": SettlementPhase1Message,
        "SettlementPhase1Commit": SettlementPhase1CommitMessage,
        "SettlementComplete": SettlementCompleteMessage,
        "SettlementFailed": SettlementFailedMessage,
    }
    
    msg_class = message_classes.get(msg_type_str)
    if not msg_class:
        raise ValueError(f"Unknown message type: {msg_type_str}")
    
    msg = msg_class()
    msg.msg_id = data.get("msg_id", msg.msg_id)
    msg.sender_id = data.get("sender_id", "")
    msg.timestamp = data.get("timestamp", msg.timestamp)
    msg.body = data.get("body", {})
    msg.signature = data.get("signature")
    msg.nonce = data.get("nonce", msg.nonce)
    
    return msg


# ============================================================================
# Test Helpers
# ============================================================================

def create_test_buyer_intent(
    intent_id: str,
    vertical: str,
    budget_ceiling: float,
    ttl_seconds: int = 120,
) -> BuyerIntentMessage:
    """Create a test BuyerIntent message."""
    msg = BuyerIntentMessage(sender_id="test-buyer")
    
    if vertical.lower() == "hotels":
        requirements = {
            "location": "Chicago, IL",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
            "rooms": 1,
            "persons": 2,
            "amenities": ["wifi"],
        }
    else:
        requirements = {}
    
    body = BuyerIntentMessage.Body(
        intent_id=intent_id,
        vertical=vertical,
        requirements=requirements,
        budget_ceiling=budget_ceiling,
        ttl_seconds=ttl_seconds,
    )
    msg.set_body(body)
    return msg


def create_test_seller_ask(
    ask_id: str,
    vertical: str,
    published_price: float,
    floor_price: float,
    listing_id: str = "test-listing",
) -> SellerAskMessage:
    """Create a test SellerAsk message."""
    msg = SellerAskMessage(sender_id="test-seller")
    
    if vertical.lower() == "hotels":
        inventory = {
            "location": "Chicago, IL",
            "property_name": "Test Hotel",
            "room_type": "King Suite",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
            "available_rooms": 5,
        }
        terms = {
            "cancellation": "free_until_24h",
            "breakfast": "not_included",
            "parking": "included",
        }
    else:
        inventory = {}
        terms = {}
    
    body = SellerAskMessage.Body(
        ask_id=ask_id,
        vertical=vertical,
        listing_id=listing_id,
        inventory=inventory,
        published_price=published_price,
        floor_price=floor_price,
        terms=terms,
        token_stake=100,
    )
    msg.set_body(body)
    return msg


if __name__ == "__main__":
    # Quick sanity check
    buyer_msg = create_test_buyer_intent("BID-001", "Hotels", 220.0)
    print("BuyerIntent:", buyer_msg.to_json())
    print()
    
    seller_msg = create_test_seller_ask("ASK-001", "Hotels", 249.0, 215.0)
    print("SellerAsk:", seller_msg.to_json())
    print()
    
    print("Canonical JSON (for signature):", buyer_msg.canonical_json())
