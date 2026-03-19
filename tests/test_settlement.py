"""
Tests for Settlement Engine and Two-Phase Commit Protocol.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'settlement'))

from escrow import (
    SettlementEngine, Settlement, SettlementRecord,
    Phase1Status, Phase2Status, SettlementStatus,
    EscrowAccount
)


class TestSettlementRecord(unittest.TestCase):
    """Test the canonical settlement record."""
    
    def test_settlement_record_calculates_fees(self):
        """Settlement should calculate platform fee correctly."""
        record = SettlementRecord(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=100.0,
            platform_fee_pct=1.5,  # 1.5%
        )
        
        self.assertEqual(record.platform_fee, 1.5)
        self.assertEqual(record.seller_receives, 98.5)
    
    def test_settlement_record_canonical_json_is_deterministic(self):
        """Canonical JSON should be identical for same data."""
        record = SettlementRecord(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={"cancellation": "free_until_24h"},
        )
        
        json1 = record.canonical_json
        json2 = record.canonical_json
        
        self.assertEqual(json1, json2)
    
    def test_settlement_record_hash_is_consistent(self):
        """Hash should be consistent for same record."""
        record = SettlementRecord(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
        )
        
        hash1 = record.hash
        hash2 = record.hash
        
        self.assertEqual(hash1, hash2)


class TestEscrowAccount(unittest.TestCase):
    """Test escrow account lifecycle."""
    
    def test_escrow_starts_locked(self):
        """Escrow should start in locked state."""
        escrow = EscrowAccount(
            settlement_id="settle-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            escrow_amount=215.0,
        )
        
        self.assertTrue(escrow.is_locked)
        self.assertIsNone(escrow.released_at)
    
    def test_escrow_tracks_lock_duration(self):
        """Escrow should track how long it's been locked."""
        escrow = EscrowAccount(
            settlement_id="settle-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            escrow_amount=215.0,
            created_at=datetime.utcnow() - timedelta(seconds=10),
        )
        
        locked_for = escrow.locked_for_seconds
        self.assertGreaterEqual(locked_for, 10)


class TestSettlementEngine(unittest.TestCase):
    """Test the settlement engine and two-phase commit."""
    
    def setUp(self):
        """Create a fresh engine for each test."""
        self.engine = SettlementEngine()
    
    def test_create_settlement_initializes_correctly(self):
        """Creating a settlement should initialize all fields."""
        settlement = self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={"cancellation": "free_until_24h"},
        )
        
        self.assertEqual(settlement.settlement_id, "settle-001")
        self.assertEqual(settlement.record.final_price, 215.0)
        self.assertEqual(settlement.overall_status, SettlementStatus.IN_PHASE1)
        self.assertTrue(settlement.escrow.is_locked)
    
    def test_create_settlement_stores_in_engine(self):
        """Created settlement should be retrievable."""
        settlement = self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        retrieved = self.engine.get_settlement("settle-001")
        self.assertEqual(retrieved.settlement_id, "settle-001")
    
    def test_buyer_phase1_commit_succeeds(self):
        """Buyer should be able to commit in Phase 1."""
        settlement = self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        success = self.engine.commit_buyer_phase1(
            "settle-001",
            "buyer_sig_123"
        )
        
        self.assertTrue(success)
        self.assertEqual(settlement.phase1_status, Phase1Status.BUYER_COMMITTED)
        self.assertIsNotNone(settlement.buyer_phase1_commitment)
    
    def test_seller_phase1_commit_succeeds(self):
        """Seller should be able to commit in Phase 1."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        success = self.engine.commit_seller_phase1(
            "settle-001",
            "seller_sig_456",
            "inventory_hold_xyz"
        )
        
        settlement = self.engine.get_settlement("settle-001")
        
        self.assertTrue(success)
        self.assertEqual(settlement.phase1_status, Phase1Status.SELLER_COMMITTED)
        self.assertIsNotNone(settlement.seller_phase1_commitment)
    
    def test_both_commits_trigger_phase1_complete(self):
        """When both commit, Phase 1 should be complete."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        self.engine.commit_seller_phase1("settle-001", "seller_sig")
        
        settlement = self.engine.get_settlement("settle-001")
        
        self.assertEqual(settlement.phase1_status, Phase1Status.BOTH_COMMITTED)
    
    def test_duplicate_buyer_commit_fails(self):
        """Buyer shouldn't be able to commit twice."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        success1 = self.engine.commit_buyer_phase1("settle-001", "sig1")
        success2 = self.engine.commit_buyer_phase1("settle-001", "sig2")
        
        self.assertTrue(success1)
        self.assertFalse(success2)  # Second commit fails
    
    def test_phase2_requires_both_commits(self):
        """Phase 2 should require both Phase 1 commitments."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        # Only buyer commits
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        
        # Phase 2 should fail
        success = self.engine.execute_phase2("settle-001")
        self.assertFalse(success)
    
    def test_phase2_execute_succeeds_with_both_commits(self):
        """Phase 2 should succeed when both Phase 1 commits exist."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        # Both commit
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        self.engine.commit_seller_phase1("settle-001", "seller_sig")
        
        # Phase 2 executes
        success = self.engine.execute_phase2("settle-001")
        
        settlement = self.engine.get_settlement("settle-001")
        
        self.assertTrue(success)
        self.assertEqual(settlement.overall_status, SettlementStatus.COMPLETED)
        self.assertEqual(settlement.phase2_status, Phase2Status.EXECUTED)
    
    def test_completion_releases_escrow(self):
        """Successful completion should release escrow to seller."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        self.engine.commit_seller_phase1("settle-001", "seller_sig")
        self.engine.execute_phase2("settle-001")
        
        escrow = self.engine.escrow_accounts.get("settle-001")
        
        self.assertFalse(escrow.is_locked)
        self.assertIsNotNone(escrow.released_at)
        self.assertEqual(escrow.release_reason, "Completed - funds transferred to seller")
    
    def test_failure_releases_escrow_to_buyer(self):
        """Settlement failure should release escrow back to buyer."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        success = self.engine.fail_settlement(
            "settle-001",
            "Seller inventory hold failed"
        )
        
        settlement = self.engine.get_settlement("settle-001")
        escrow = self.engine.escrow_accounts.get("settle-001")
        
        self.assertTrue(success)
        self.assertEqual(settlement.overall_status, SettlementStatus.FAILED)
        self.assertFalse(escrow.is_locked)
    
    def test_slashing_on_seller_failure(self):
        """Seller should be slashed for inventory hold failure."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        self.engine.fail_settlement(
            "settle-001",
            "Seller inventory hold failed",
            slash_amount=0.5  # 0.5 ABT slashed
        )
        
        settlement = self.engine.get_settlement("settle-001")
        
        self.assertEqual(settlement.slash_amount, 0.5)
        self.assertEqual(settlement.slash_reason, "Failed to hold inventory")
    
    def test_rewards_on_completion(self):
        """Both parties should receive token rewards on completion."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        self.engine.commit_seller_phase1("settle-001", "seller_sig")
        self.engine.execute_phase2("settle-001")
        
        settlement = self.engine.get_settlement("settle-001")
        
        self.assertEqual(settlement.buyer_reward_tokens, 2)
        self.assertGreater(settlement.seller_reward_tokens, 0)
    
    def test_high_stake_bonus_rewards(self):
        """High-stake sellers should receive bonus rewards."""
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
            seller_token_stake=2500,  # High stake
        )
        
        self.engine.commit_buyer_phase1("settle-001", "buyer_sig")
        self.engine.commit_seller_phase1("settle-001", "seller_sig")
        self.engine.execute_phase2("settle-001")
        
        settlement = self.engine.get_settlement("settle-001")
        
        # Base 3 + bonus 2 = 5
        self.assertEqual(settlement.seller_reward_tokens, 5)
    
    def test_cleanup_expired_phase1_settlements(self):
        """Cleanup should timeout Phase 1 settlements past 30s."""
        # Create a settlement and artificially set it to 40s old
        self.engine.create_settlement(
            settlement_id="settle-001",
            booking_ref="BK-001",
            buyer_agent_id="buyer-001",
            seller_agent_id="seller-001",
            intent_id="BID-001",
            ask_id="ASK-001",
            session_id="sess-001",
            final_price=215.0,
            final_terms={},
        )
        
        settlement = self.engine.get_settlement("settle-001")
        # Fake the expiry time to past
        settlement.record.phase1_expires_at = datetime.utcnow() - timedelta(seconds=1)
        
        cleaned = self.engine.cleanup_expired_phase1()
        
        self.assertEqual(cleaned, 1)
        self.assertEqual(settlement.overall_status, SettlementStatus.FAILED)
        self.assertIn("timeout", settlement.failure_reason.lower())


if __name__ == "__main__":
    unittest.main()
