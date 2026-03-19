"""
Tests for the Order Book and Matching Algorithm.
"""

import unittest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'protocol'))

from orderbook import OrderBook, MatchingAlgorithm, NegotiationSession
from messages import (
    create_test_buyer_intent,
    create_test_seller_ask,
    DealAcceptedMessage,
    SessionState,
)


class TestHardFilter(unittest.TestCase):
    """Test the hard filter step of matching."""
    
    def test_hard_filter_removes_overpriced_asks(self):
        """Asks above buyer ceiling should be filtered out."""
        # Buyer ceiling = $200
        asks = [
            create_test_seller_ask("A1", "Hotels", 150.0, 140.0),
            create_test_seller_ask("A2", "Hotels", 200.0, 190.0),
            create_test_seller_ask("A3", "Hotels", 250.0, 240.0),  # Over ceiling
        ]
        
        filtered = MatchingAlgorithm.hard_filter(200.0, asks)
        
        self.assertEqual(len(filtered), 2)
        self.assertIn(asks[0], filtered)
        self.assertIn(asks[1], filtered)
        self.assertNotIn(asks[2], filtered)
    
    def test_hard_filter_accepts_at_ceiling(self):
        """Ask exactly at ceiling should be accepted."""
        asks = [create_test_seller_ask("A1", "Hotels", 200.0, 190.0)]
        filtered = MatchingAlgorithm.hard_filter(200.0, asks)
        self.assertEqual(len(filtered), 1)


class TestSchemaValidation(unittest.TestCase):
    """Test vertical-specific schema validation."""
    
    def test_hotel_schema_accepts_matching_location(self):
        """Hotel with matching location should pass."""
        buyer_req = {
            "location": "Chicago, IL",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
            "rooms": 1,
        }
        seller_inv = {
            "location": "Chicago, IL",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
            "available_rooms": 5,
        }
        
        valid = MatchingAlgorithm.schema_validate(buyer_req, seller_inv, "Hotels")
        self.assertTrue(valid)
    
    def test_hotel_schema_rejects_location_mismatch(self):
        """Hotel in different city should fail."""
        buyer_req = {
            "location": "Chicago, IL",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
        }
        seller_inv = {
            "location": "New York, NY",
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
            "available_rooms": 5,
        }
        
        valid = MatchingAlgorithm.schema_validate(buyer_req, seller_inv, "Hotels")
        self.assertFalse(valid)
    
    def test_hotel_schema_rejects_insufficient_rooms(self):
        """Hotel with fewer available rooms should fail."""
        buyer_req = {
            "location": "Chicago, IL",
            "rooms": 3,
        }
        seller_inv = {
            "location": "Chicago, IL",
            "available_rooms": 2,
        }
        
        valid = MatchingAlgorithm.schema_validate(buyer_req, seller_inv, "Hotels")
        self.assertFalse(valid)
    
    def test_hotel_schema_rejects_date_mismatch(self):
        """Hotel with non-overlapping dates should fail."""
        buyer_req = {
            "checkin": "2026-04-20",
            "checkout": "2026-04-22",
        }
        seller_inv = {
            "checkin": "2026-04-15",
            "checkout": "2026-04-17",
        }
        
        valid = MatchingAlgorithm.schema_validate(buyer_req, seller_inv, "Hotels")
        self.assertFalse(valid)


class TestCompatibilityScoring(unittest.TestCase):
    """Test the 4-factor compatibility scoring."""
    
    def test_perfect_price_match_scores_high(self):
        """Seller at exactly buyer's ceiling should score high."""
        buyer_intent = create_test_buyer_intent("BID-001", "Hotels", 200.0)
        seller_ask = create_test_seller_ask("ASK-001", "Hotels", 200.0, 190.0)
        
        score = MatchingAlgorithm.compatibility_score(
            buyer_intent, seller_ask, 200.0, 190.0
        )
        
        # Should score highly due to perfect price match
        self.assertGreater(score, 70.0)
    
    def test_price_far_from_floor_scores_low(self):
        """Seller at floor should score lower than at ceiling."""
        buyer_intent = create_test_buyer_intent("BID-001", "Hotels", 200.0)
        
        ask_ceiling = create_test_seller_ask("ASK-C", "Hotels", 200.0, 190.0)
        ask_floor = create_test_seller_ask("ASK-F", "Hotels", 190.0, 180.0)
        
        score_ceiling = MatchingAlgorithm.compatibility_score(
            buyer_intent, ask_ceiling, 200.0, 190.0
        )
        score_floor = MatchingAlgorithm.compatibility_score(
            buyer_intent, ask_floor, 200.0, 180.0
        )
        
        self.assertGreater(score_ceiling, score_floor)
    
    def test_high_stake_increases_score(self):
        """Higher token stake should increase compatibility score."""
        buyer_intent = create_test_buyer_intent("BID-001", "Hotels", 200.0)
        
        ask_no_stake = create_test_seller_ask("ASK-1", "Hotels", 200.0, 190.0)
        ask_no_stake.body["token_stake"] = 0
        
        ask_high_stake = create_test_seller_ask("ASK-2", "Hotels", 200.0, 190.0)
        ask_high_stake.body["token_stake"] = 2500
        
        score_no_stake = MatchingAlgorithm.compatibility_score(
            buyer_intent, ask_no_stake, 200.0, 190.0
        )
        score_high_stake = MatchingAlgorithm.compatibility_score(
            buyer_intent, ask_high_stake, 200.0, 190.0
        )
        
        self.assertGreater(score_high_stake, score_no_stake)


class TestOrderBook(unittest.TestCase):
    """Test the full OrderBook functionality."""
    
    def setUp(self):
        """Create a fresh order book for each test."""
        self.ob = OrderBook()
    
    def test_post_intent_succeeds(self):
        """Posting a valid intent should succeed."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        result = self.ob.post_intent(intent)
        self.assertTrue(result)
        self.assertIn("BID-001", self.ob.intents)
    
    def test_post_intent_rejects_duplicate_within_10s(self):
        """Posting the same intent twice should reject the duplicate."""
        intent1 = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        result1 = self.ob.post_intent(intent1)
        
        intent2 = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        result2 = self.ob.post_intent(intent2)
        
        self.assertTrue(result1)
        self.assertFalse(result2)  # Duplicate rejected
    
    def test_post_ask_succeeds(self):
        """Posting a valid ask should succeed."""
        ask = create_test_seller_ask("ASK-001", "Hotels", 249.0, 215.0)
        result = self.ob.post_ask(ask)
        self.assertTrue(result)
        self.assertIn("ASK-001", self.ob.asks)
    
    def test_find_matches_returns_viable_asks(self):
        """Finding matches should return asks under budget."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        self.ob.post_intent(intent)
        
        # Post some asks
        self.ob.post_ask(create_test_seller_ask("ASK-1", "Hotels", 200.0, 190.0))
        self.ob.post_ask(create_test_seller_ask("ASK-2", "Hotels", 215.0, 205.0))
        self.ob.post_ask(create_test_seller_ask("ASK-3", "Hotels", 250.0, 240.0))  # Over budget
        
        matches = self.ob.find_matches_for_intent(intent)
        
        # Should find 2 matches (ASK-1 and ASK-2), not ASK-3
        self.assertEqual(len(matches), 2)
        
        ask_ids = [ask.body.get("ask_id") for ask, _ in matches]
        self.assertIn("ASK-1", ask_ids)
        self.assertIn("ASK-2", ask_ids)
        self.assertNotIn("ASK-3", ask_ids)
    
    def test_matches_ranked_by_score(self):
        """Matches should be ranked from highest to lowest score."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        self.ob.post_intent(intent)
        
        # Post asks at different prices
        self.ob.post_ask(create_test_seller_ask("ASK-LOW", "Hotels", 200.0, 190.0))
        self.ob.post_ask(create_test_seller_ask("ASK-MID", "Hotels", 210.0, 200.0))
        self.ob.post_ask(create_test_seller_ask("ASK-HIGH", "Hotels", 220.0, 210.0))
        
        matches = self.ob.find_matches_for_intent(intent)
        
        # Highest priced (closest to ceiling) should rank first
        self.assertEqual(matches[0][0].body.get("ask_id"), "ASK-HIGH")
    
    def test_create_sessions_for_intent(self):
        """Creating sessions for an intent should work."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        self.ob.post_intent(intent)
        
        self.ob.post_ask(create_test_seller_ask("ASK-1", "Hotels", 200.0, 190.0))
        self.ob.post_ask(create_test_seller_ask("ASK-2", "Hotels", 215.0, 205.0))
        self.ob.post_ask(create_test_seller_ask("ASK-3", "Hotels", 220.0, 210.0))
        
        sessions = self.ob.create_sessions_for_intent("BID-001", max_sessions=2)
        
        # Should create 2 sessions (top 2 matches)
        self.assertEqual(len(sessions), 2)
        
        # Sessions should be in NEGOTIATING state
        for session in sessions:
            self.assertEqual(session.state, SessionState.NEGOTIATING)
    
    def test_accept_deal_terminates_other_sessions(self):
        """Accepting a deal should terminate other sessions for same intent."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        self.ob.post_intent(intent)
        
        self.ob.post_ask(create_test_seller_ask("ASK-1", "Hotels", 200.0, 190.0))
        self.ob.post_ask(create_test_seller_ask("ASK-2", "Hotels", 215.0, 205.0))
        
        sessions = self.ob.create_sessions_for_intent("BID-001", max_sessions=2)
        session1_id = sessions[0].session_id
        session2_id = sessions[1].session_id
        
        # Accept the deal on session 1
        acceptance = DealAcceptedMessage(
            sender_id="test-buyer",
        )
        acceptance.body = {
            "intent_id": "BID-001",
            "ask_id": self.ob.get_session(session1_id).ask_id,
            "session_id": session1_id,
            "final_price": 215.0,
            "final_terms": {},
            "accepting_party": "buyer",
            "accepting_sig": ""
        }
        
        result = self.ob.accept_deal(acceptance)
        
        self.assertTrue(result)
        self.assertEqual(self.ob.get_session(session1_id).state, SessionState.ACCEPTED)
        self.assertEqual(self.ob.get_session(session2_id).state, SessionState.FAILED)
    
    def test_stats_returns_accurate_counts(self):
        """Stats should reflect current order book state."""
        intent = create_test_buyer_intent("BID-001", "Hotels", 220.0)
        self.ob.post_intent(intent)
        
        self.ob.post_ask(create_test_seller_ask("ASK-1", "Hotels", 200.0, 190.0))
        self.ob.post_ask(create_test_seller_ask("ASK-2", "Hotels", 215.0, 205.0))
        
        self.ob.create_sessions_for_intent("BID-001", max_sessions=2)
        
        stats = self.ob.stats()
        
        self.assertEqual(stats["total_intents"], 1)
        self.assertEqual(stats["total_asks"], 2)
        self.assertEqual(stats["total_sessions"], 2)
        self.assertEqual(stats["sessions_by_state"]["negotiating"], 2)


if __name__ == "__main__":
    unittest.main()
