"""
BookWithClaw — Escrow & Two-Phase Commit Settlement

Implements atomic settlement with:
- Phase 1: Lock (co-signatures + escrow + inventory hold)
- Phase 2: Execute (verify + release + notify)
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json


class Phase1Status(str, Enum):
    """Phase 1 commitment status."""
    PENDING = "pending"
    BUYER_COMMITTED = "buyer_committed"
    SELLER_COMMITTED = "seller_committed"
    BOTH_COMMITTED = "both_committed"
    TIMEOUT = "timeout"
    FAILED = "failed"


class Phase2Status(str, Enum):
    """Phase 2 execution status."""
    PENDING = "pending"
    ESCROW_VERIFIED = "escrow_verified"
    EXECUTED = "executed"
    FAILED = "failed"


class SettlementStatus(str, Enum):
    """Overall settlement status."""
    IN_PHASE1 = "in_phase1"
    IN_PHASE2 = "in_phase2"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"


@dataclass
class EscrowAccount:
    """Escrow account holding buyer's funds during settlement."""
    
    settlement_id: str
    buyer_agent_id: str
    seller_agent_id: str
    escrow_amount: float
    currency: str = "USD"
    platform_fee: float = 0.0
    seller_receives: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    released_at: Optional[datetime] = None
    release_reason: str = ""  # "completed", "failed", "dispute", etc.
    
    @property
    def is_locked(self) -> bool:
        """Escrow is locked (funds unavailable to buyer)."""
        return self.released_at is None
    
    @property
    def locked_for_seconds(self) -> int:
        """How long escrow has been locked."""
        end = self.released_at or datetime.utcnow()
        delta = end - self.created_at
        return int(delta.total_seconds())


@dataclass
class Phase1Commitment:
    """Phase 1: Lock — Co-signature commitment from one party."""
    
    settlement_id: str
    party: Literal["buyer", "seller"]
    committed_at: datetime = field(default_factory=datetime.utcnow)
    signature: str = ""  # Ed25519 signature of settlement record
    inventory_hold_id: Optional[str] = None  # Seller's inventory hold reference
    notes: str = ""
    
    @property
    def age_seconds(self) -> int:
        delta = datetime.utcnow() - self.committed_at
        return int(delta.total_seconds())


@dataclass
class SettlementRecord:
    """
    Canonical settlement record (immutable once created).
    
    Both parties sign this record to commit to the deal.
    This is the source of truth for Phase 2 execution.
    """
    
    settlement_id: str
    booking_ref: str  # Customer-facing booking reference
    
    buyer_agent_id: str
    seller_agent_id: str
    
    intent_id: str  # Reference to original buyer intent
    ask_id: str  # Reference to original seller ask
    session_id: str  # Reference to negotiation session
    
    final_price: float  # Final agreed price
    final_terms: Dict = field(default_factory=dict)  # Final agreed terms
    
    currency: str = "USD"
    
    # Fee structure
    platform_fee_pct: float = 1.5  # Percentage of final_price
    platform_fee: float = 0.0  # Calculated fee
    seller_receives: float = 0.0  # final_price - platform_fee
    
    # Stake information
    seller_token_stake: int = 0  # ABT tokens staked by seller
    
    # Phase 1 metadata
    phase1_timeout_seconds: int = 30
    phase1_created_at: datetime = field(default_factory=datetime.utcnow)
    phase1_expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(seconds=30))
    
    # Phase 2 metadata
    phase2_created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate fees after initialization."""
        self.platform_fee = max(0.0, self.final_price * (self.platform_fee_pct / 100.0))
        self.seller_receives = self.final_price - self.platform_fee
    
    @property
    def is_phase1_expired(self) -> bool:
        return datetime.utcnow() > self.phase1_expires_at
    
    @property
    def canonical_json(self) -> str:
        """
        Canonical JSON representation for co-signature.
        
        This is what both parties sign. Must be deterministic (sorted keys, no whitespace).
        """
        record = {
            "settlement_id": self.settlement_id,
            "booking_ref": self.booking_ref,
            "buyer_agent_id": self.buyer_agent_id,
            "seller_agent_id": self.seller_agent_id,
            "final_price": self.final_price,
            "final_terms": self.final_terms,
            "platform_fee": self.platform_fee,
            "seller_receives": self.seller_receives,
            "currency": self.currency,
        }
        return json.dumps(record, sort_keys=True, separators=(',', ':'))
    
    @property
    def hash(self) -> str:
        """SHA256 hash of canonical JSON (for reference)."""
        return hashlib.sha256(self.canonical_json.encode()).hexdigest()


# ============================================================================
# Settlement State Machine
# ============================================================================

class SettlementEngine:
    """
    Manages the entire settlement lifecycle:
    Phase 1 (Lock) → Phase 2 (Execute) → Completed or Failed
    """
    
    def __init__(self):
        """Initialize the settlement engine."""
        self.settlements: Dict[str, "Settlement"] = {}
        self.escrow_accounts: Dict[str, EscrowAccount] = {}
    
    def create_settlement(
        self,
        settlement_id: str,
        booking_ref: str,
        buyer_agent_id: str,
        seller_agent_id: str,
        intent_id: str,
        ask_id: str,
        session_id: str,
        final_price: float,
        final_terms: Dict,
        seller_token_stake: int = 0,
    ) -> "Settlement":
        """
        Create a new settlement record.
        
        Returns: Settlement object in PHASE_1_PENDING state.
        """
        record = SettlementRecord(
            settlement_id=settlement_id,
            booking_ref=booking_ref,
            buyer_agent_id=buyer_agent_id,
            seller_agent_id=seller_agent_id,
            intent_id=intent_id,
            ask_id=ask_id,
            session_id=session_id,
            final_price=final_price,
            final_terms=final_terms,
            seller_token_stake=seller_token_stake,
        )
        
        escrow = EscrowAccount(
            settlement_id=settlement_id,
            buyer_agent_id=buyer_agent_id,
            seller_agent_id=seller_agent_id,
            escrow_amount=record.platform_fee + record.seller_receives,  # Full amount held
            platform_fee=record.platform_fee,
            seller_receives=record.seller_receives,
        )
        
        settlement = Settlement(
            settlement_id=settlement_id,
            record=record,
            escrow=escrow,
        )
        
        self.settlements[settlement_id] = settlement
        self.escrow_accounts[settlement_id] = escrow
        
        return settlement
    
    def get_settlement(self, settlement_id: str) -> Optional["Settlement"]:
        """Retrieve a settlement by ID."""
        return self.settlements.get(settlement_id)
    
    def commit_buyer_phase1(
        self,
        settlement_id: str,
        buyer_signature: str,
    ) -> bool:
        """
        Buyer commits to Phase 1 (funds in escrow).
        
        Returns: True if accepted, False if invalid or already committed.
        """
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            return False
        
        if settlement.phase1_status == Phase1Status.BOTH_COMMITTED:
            return False  # Already complete
        
        if settlement.buyer_phase1_commitment:
            return False  # Already committed by buyer
        
        # Validate signature (in real implementation, cryptographic check)
        # For now, just accept it
        commitment = Phase1Commitment(
            settlement_id=settlement_id,
            party="buyer",
            signature=buyer_signature,
        )
        
        settlement.buyer_phase1_commitment = commitment
        
        # Update phase1 status
        if settlement.seller_phase1_commitment:
            settlement.phase1_status = Phase1Status.BOTH_COMMITTED
        else:
            settlement.phase1_status = Phase1Status.BUYER_COMMITTED
        
        return True
    
    def commit_seller_phase1(
        self,
        settlement_id: str,
        seller_signature: str,
        inventory_hold_id: str = "",
    ) -> bool:
        """
        Seller commits to Phase 1 (inventory held in source system).
        
        Returns: True if accepted, False if invalid or already committed.
        """
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            return False
        
        if settlement.phase1_status == Phase1Status.BOTH_COMMITTED:
            return False
        
        if settlement.seller_phase1_commitment:
            return False
        
        commitment = Phase1Commitment(
            settlement_id=settlement_id,
            party="seller",
            signature=seller_signature,
            inventory_hold_id=inventory_hold_id,
        )
        
        settlement.seller_phase1_commitment = commitment
        
        # Update phase1 status
        if settlement.buyer_phase1_commitment:
            settlement.phase1_status = Phase1Status.BOTH_COMMITTED
        else:
            settlement.phase1_status = Phase1Status.SELLER_COMMITTED
        
        return True
    
    def execute_phase2(self, settlement_id: str) -> bool:
        """
        Execute Phase 2 (verify + release funds + notify).
        
        This is called after both parties have committed in Phase 1.
        
        Returns: True if successful, False if failed.
        """
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            return False
        
        # Verify Phase 1 is complete
        if settlement.phase1_status != Phase1Status.BOTH_COMMITTED:
            return False
        
        # Mark Phase 2 as in-progress
        settlement.record.phase2_created_at = datetime.utcnow()
        settlement.phase2_status = Phase2Status.PENDING
        settlement.overall_status = SettlementStatus.IN_PHASE2
        
        # Step 1: Verify both commitments are valid (cryptographic checks)
        if not settlement.buyer_phase1_commitment or not settlement.seller_phase1_commitment:
            settlement.phase2_status = Phase2Status.FAILED
            settlement.overall_status = SettlementStatus.FAILED
            settlement.failure_reason = "Phase 1 commitments missing"
            self.release_escrow(settlement_id, "Phase 1 verification failed")
            return False
        
        settlement.phase2_status = Phase2Status.ESCROW_VERIFIED
        
        # Step 2: Release funds to seller (minus platform fee)
        escrow = self.escrow_accounts.get(settlement_id)
        if not escrow or not escrow.is_locked:
            settlement.phase2_status = Phase2Status.FAILED
            settlement.overall_status = SettlementStatus.FAILED
            settlement.failure_reason = "Escrow already released"
            return False
        
        # In real system, transfer funds here
        # For simulation: just mark as released
        self.release_escrow(
            settlement_id,
            "Completed - funds transferred to seller"
        )
        
        settlement.phase2_status = Phase2Status.EXECUTED
        settlement.overall_status = SettlementStatus.COMPLETED
        settlement.completed_at = datetime.utcnow()
        
        # Step 3: Queue token rewards
        settlement.buyer_reward_tokens = 2  # Base reward
        settlement.seller_reward_tokens = 3  # Base reward
        
        # Bonus for high stake
        if settlement.record.seller_token_stake >= 2500:
            settlement.seller_reward_tokens += 2
        
        return True
    
    def release_escrow(
        self,
        settlement_id: str,
        reason: str,
    ) -> bool:
        """
        Release escrow account (refund to buyer or pay to seller).
        
        This is called in failure scenarios or on completion.
        """
        escrow = self.escrow_accounts.get(settlement_id)
        if not escrow or not escrow.is_locked:
            return False
        
        escrow.released_at = datetime.utcnow()
        escrow.release_reason = reason
        
        return True
    
    def fail_settlement(
        self,
        settlement_id: str,
        failure_reason: str,
        slash_amount: float = 0.0,
    ) -> bool:
        """
        Fail the settlement (e.g., Phase 1 timeout, inventory unavailable).
        
        Returns: True if failed successfully, False if already final.
        """
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            return False
        
        # Can't fail if already completed
        if settlement.overall_status == SettlementStatus.COMPLETED:
            return False
        
        settlement.overall_status = SettlementStatus.FAILED
        settlement.failure_reason = failure_reason
        settlement.slash_amount = slash_amount
        settlement.failed_at = datetime.utcnow()
        
        # Release escrow (back to buyer)
        self.release_escrow(settlement_id, f"Failed: {failure_reason}")
        
        # Slash seller if applicable
        if slash_amount > 0:
            settlement.slash_reason = "Failed to hold inventory"
        
        return True
    
    def cleanup_expired_phase1(self) -> int:
        """
        Cleanup settlements stuck in Phase 1 past timeout.
        
        Returns: Number of settlements cleaned up.
        """
        cleaned = 0
        for settlement_id, settlement in list(self.settlements.items()):
            if (settlement.overall_status == SettlementStatus.IN_PHASE1 and
                settlement.record.is_phase1_expired):
                
                self.fail_settlement(
                    settlement_id,
                    "Phase 1 timeout (30s)",
                )
                cleaned += 1
        
        return cleaned


# ============================================================================
# Settlement Object (State Container)
# ============================================================================

@dataclass
class Settlement:
    """
    Complete settlement state container.
    
    Represents one deal's entire lifecycle from negotiation to completion.
    """
    
    settlement_id: str
    record: SettlementRecord
    escrow: EscrowAccount
    
    # Phase 1 state
    phase1_status: Phase1Status = Phase1Status.PENDING
    buyer_phase1_commitment: Optional[Phase1Commitment] = None
    seller_phase1_commitment: Optional[Phase1Commitment] = None
    
    # Phase 2 state
    phase2_status: Phase2Status = Phase2Status.PENDING
    
    # Overall state
    overall_status: SettlementStatus = SettlementStatus.IN_PHASE1
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    # Failure info
    failure_reason: str = ""
    slash_amount: float = 0.0
    slash_reason: str = ""
    
    # Rewards
    buyer_reward_tokens: int = 0
    seller_reward_tokens: int = 0
    
    @property
    def is_final(self) -> bool:
        """Settlement is in a final state (completed or failed)."""
        return self.overall_status in [
            SettlementStatus.COMPLETED,
            SettlementStatus.FAILED,
            SettlementStatus.DISPUTED,
        ]
    
    @property
    def phase1_timeout_at(self) -> datetime:
        """When Phase 1 expires."""
        return self.record.phase1_expires_at
    
    @property
    def age_seconds(self) -> int:
        """How long this settlement has existed."""
        end = self.failed_at or self.completed_at or datetime.utcnow()
        delta = end - self.created_at
        return int(delta.total_seconds())


if __name__ == "__main__":
    # Quick sanity test
    engine = SettlementEngine()
    
    # Create a settlement
    settlement = engine.create_settlement(
        settlement_id="settle-001",
        booking_ref="BK-2026-001",
        buyer_agent_id="buyer-001",
        seller_agent_id="seller-001",
        intent_id="BID-001",
        ask_id="ASK-001",
        session_id="sess-001",
        final_price=215.0,
        final_terms={"cancellation": "free_until_24h"},
    )
    
    print(f"✓ Created settlement: {settlement.settlement_id}")
    print(f"  Status: {settlement.overall_status.value}")
    print(f"  Buyer: {settlement.record.buyer_agent_id}")
    print(f"  Seller: {settlement.record.seller_agent_id}")
    print(f"  Price: ${settlement.record.final_price}")
    print(f"  Fee: ${settlement.record.platform_fee:.2f}")
    print(f"  Seller receives: ${settlement.record.seller_receives:.2f}")
    print()
    
    # Phase 1: Buyer commits
    success = engine.commit_buyer_phase1(
        "settle-001",
        "buyer_sig_123"
    )
    print(f"✓ Buyer committed: {success}")
    print(f"  Phase 1 status: {settlement.phase1_status.value}")
    print()
    
    # Phase 1: Seller commits
    success = engine.commit_seller_phase1(
        "settle-001",
        "seller_sig_456",
        "inventory_hold_xyz"
    )
    print(f"✓ Seller committed: {success}")
    print(f"  Phase 1 status: {settlement.phase1_status.value}")
    print()
    
    # Phase 2: Execute
    success = engine.execute_phase2("settle-001")
    print(f"✓ Phase 2 executed: {success}")
    print(f"  Overall status: {settlement.overall_status.value}")
    print(f"  Buyer rewards: {settlement.buyer_reward_tokens} ABT")
    print(f"  Seller rewards: {settlement.seller_reward_tokens} ABT")
    print(f"  Settlement completed in {settlement.age_seconds}s")
