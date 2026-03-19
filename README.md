# BookWithClaw — Agent Exchange & Settlement Protocol

**Status:** 🚀 Phase 1 — Building Foundations (2026-03-19)

A peer-to-peer marketplace protocol for autonomous agents. Foundation layer = exchange protocol + settlement mechanism. Test case: hotel room buyer/seller skills.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ L1 — Skill Layer                                            │
│ Buyer Agent (MCP) ←→ Exchange ←→ Seller Agent (MCP)        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ L2 — Protocol Layer (AgentBook Exchange)                    │
│ • Order Book (Bids + Asks)                                  │
│ • Session Manager (Auth + Routing)                          │
│ • State Machine (Negotiation Logic)                         │
│ • Dispute Arbiter (Resolution)                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ L3 — Settlement Layer                                       │
│ • Two-Phase Commit (Atomic Settlement)                      │
│ • Escrow Management                                         │
│ • Token Rewards                                             │
│ • Notifications                                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### L2 — Exchange Protocol

**Message Types:**
- `BuyerIntent` → Exchange with budget ceiling, requirements, max negotiation rounds
- `SellerAsk` → Exchange with price, terms, expiry, token stake proof
- `BuyerCounterOffer` / `SellerCounterOffer` → Bilateral negotiation
- `DealAccepted` → Either party accepts (locks into settlement)
- `SettlementComplete` → Exchange confirms both Phase 1 & 2 completion

**Order Book States:**
- `pending` → Initial broadcast (visible only to other party type)
- `negotiating` → Private session active
- `accepted` → Both parties agreed; moving to settlement
- `settled` → Payment executed; finalized
- `failed` → Settlement failed; escrow returned

**Matching Algorithm (5 Steps):**
1. **Hard filter** — Eliminate all asks where `price > buyer_ceiling`
2. **Schema validation** — Verify vertical requirements (date overlap, cargo type, etc.)
3. **Compatibility scoring** — Price (40%) + Terms (35%) + Reputation (15%) + Stake (10%)
4. **Route top 5** — Best matches get private negotiation channels
5. **First wins** — First accepted deal terminates all other sessions for that intent

### L3 — Settlement Layer

**Two-Phase Commit (Atomic):**

*Phase 1 — Lock (30s timeout):*
1. Exchange generates canonical settlement record
2. Both agents co-sign commitment
3. Buyer funds placed in escrow
4. Seller places inventory hold in source system (PMS/CRM)

*Phase 2 — Execute:*
1. Exchange verifies both Phase 1 confirmations
2. Escrow released to seller (minus platform fee)
3. Token rewards queued
4. Both parties notified

**Failure Handling:**
| Scenario | Cause | Resolution |
|----------|-------|-----------|
| Buyer escrow fail | Insufficient funds | FAILED, no funds moved |
| Seller inventory fail | Already booked | Escrow released, 0.5 ABT slashed |
| Co-sig timeout | Agent offline | Escrow released, both notified |
| Disputed terms | Config error | Dispute Arbiter activated |

## Directory Structure

```
bookwithclaw/
├── docs/
│   ├── PROTOCOL.md          # Full protocol specification
│   ├── SETTLEMENT.md        # Two-phase commit semantics
│   ├── MESSAGE_SCHEMA.md    # All message types + fields
│   └── GOVERNANCE.md        # Token + voting model
├── src/
│   ├── protocol/
│   │   ├── messages.py      # Message type definitions
│   │   ├── orderbook.py     # Order book state machine
│   │   ├── matching.py      # Matching algorithm
│   │   └── session_mgr.py   # Session routing + auth
│   ├── settlement/
│   │   ├── escrow.py        # Escrow state machine
│   │   ├── atomic_commit.py # Two-phase commit logic
│   │   ├── validator.py     # Co-signature validation
│   │   └── dispute.py       # Dispute arbiter
│   └── skills/
│       ├── buyer_skill.py   # Buyer agent MCP
│       ├── seller_skill.py  # Seller agent MCP
│       └── templates/       # Skill templates
├── tests/
│   ├── test_protocol.py
│   ├── test_settlement.py
│   ├── test_e2e.py
│   └── fixtures/
└── README.md
```

## Build Sequence (Step 1)

**Step 1a:** Message schema + Protocol spec
- Define all message types (BuyerIntent, SellerAsk, counters, etc.)
- Serialization (JSON + Ed25519 signature fields)
- Validation rules per vertical

**Step 1b:** Order Book state machine
- Pending → Negotiating → Accepted → Settled
- TTL + cleanup for expired intents/asks
- Basic matching (hard filter + schema)

**Step 1c:** Settlement protocol (Phase 1/2)
- Atomic two-phase commit spec
- Escrow state machine
- Co-signature validation + timeout handling

**Step 2:** Skill framework + templates
- MCP connector interface
- Config envelope for buyers (max_budget, walkaway_conditions)
- Config for sellers (floor_price, discount_authority)

**Step 3:** Hotel buyer/seller skills
- Real booking flow with test data
- Integration tests end-to-end

**Step 4:** Token economics + governance
- Staking validation
- Fee calculation by tier
- Buyback/burn

## Deployment Target

Single Python service with:
- FastAPI (protocol endpoints)
- SQLite (order book + settlement ledger)
- Pub/Sub messaging (WebSocket for agent comms)
- Ed25519 signatures (agnostic to blockchain)

No blockchain required for Phase 1. Token math is deterministic; can migrate to chain later.

---

Built by: Clawbot  
Owned by: Alamin + Trevor  
Channel: #project-bookwithclaw  
Started: 2026-03-19 04:45 UTC
