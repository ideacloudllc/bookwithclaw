# BUILDSPEC.md — BookWithClaw Exchange

## Claude Code Build Instructions — Sprint 1 (Hotels, Fiat, No Token)

---

## 0. What You Are Building

BookWithClaw is an **agent-to-agent negotiation exchange**. The **exchange protocol and settlement layer are the primary product**. AI agents acting on behalf of human buyers and sellers enter the marketplace, negotiate a price in real time, and settle a transaction atomically — with both human owners notified on completion.

Skills — the modules that give agents their negotiation capabilities — are created by the open-source community using a skill template that BookWithClaw defines and publishes. The exchange does not own or maintain skills. Skills connect to the exchange via the open protocol spec defined in SKILL_SPEC.md.

For Sprint 1, BookWithClaw will build exactly two reference skills internally to validate that the exchange protocol works end-to-end. These are **test implementations only**, not production products:

- **Hotel Room Buyer Skill** — reference buyer skill for the hotel vertical
- **Hotel Room Seller Skill** — reference seller skill for the hotel vertical

**Sprint 1 scope (build exactly this, nothing more):**

- Exchange API (Python FastAPI) — the primary deliverable
- Order book (Redis)
- Persistent storage (PostgreSQL via SQLAlchemy + Alembic)
- Negotiation state machine
- Settlement layer — Stripe Connect escrow, two-phase commit
- Email notification (SendGrid) on deal close
- Hotel Room Buyer Skill — reference implementation, hotel vertical only
- Hotel Room Seller Skill — reference implementation, hotel vertical only
- Local dev environment via Docker Compose

**Explicitly out of scope for Sprint 1:**

- BWC Token, staking, governance
- Any vertical other than hotels
- Crypto/stablecoin settlement
- Web dashboard or admin UI
- Dispute resolution system
- Production deployment / cloud infra
- Publishing or distributing skills — reference skills exist only to test the exchange

---

## 1. Monorepo Structure

Create this exact directory layout:

```
bookwithclaw/
├── BUILDSPEC.md # This file
├── SCHEMA.md # Database + API schemas
├── SKILL_SPEC.md # Open-source skill protocol spec
├── docker-compose.yml # Local dev environment
├── .env.example # All required env vars documented
├── .gitignore
├── README.md
│
├── packages/
│ ├── skill-sdk/ # Open-source TypeScript SDK (published to npm)
│ │ ├── package.json
│ │ ├── tsconfig.json
│ │ ├── src/
│ │ │ ├── index.ts # Public exports
│ │ │ ├── buyer-skill.ts # BuyerSkill class
│ │ │ ├── seller-skill.ts # SellerSkill class
│ │ │ ├── messages.ts # All message type definitions
│ │ │ ├── schemas/
│ │ │ │ └── hotels.ts # Hotel vertical schema
│ │ │ ├── crypto.ts # Ed25519 signing utilities
│ │ │ └── websocket.ts # Exchange connection manager
│ │ └── tests/
│ │ ├── buyer-skill.test.ts
│ │ └── seller-skill.test.ts
│ │
│ └── exchange/ # Closed-source Python exchange (never published)
│ ├── pyproject.toml
│ ├── alembic.ini
│ ├── alembic/
│ │ ├── env.py
│ │ └── versions/ # Migration files go here
│ ├── app/
│ │ ├── main.py # FastAPI app entrypoint
│ │ ├── config.py # Settings from env vars
│ │ ├── dependencies.py # FastAPI dependency injection
│ │ │
│ │ ├── api/
│ │ │ ├── __init__.py
│ │ │ ├── sessions.py # WebSocket session endpoints
│ │ │ ├── health.py # GET /health
│ │ │ └── webhooks.py # Stripe webhook receiver
│ │ │
│ │ ├── core/
│ │ │ ├── __init__.py
│ │ │ ├── order_book.py # Redis order book logic
│ │ │ ├── state_machine.py # Negotiation state machine
│ │ │ ├── matching.py # Buyer/seller matching algorithm
│ │ │ ├── session_manager.py # WebSocket session lifecycle
│ │ │ └── signing.py # Ed25519 message verification
│ │ │
│ │ ├── settlement/
│ │ │ ├── __init__.py
│ │ │ ├── escrow.py # Stripe Connect escrow logic
│ │ │ └── notifier.py # SendGrid notification dispatch
│ │ │
│ │ ├── models/
│ │ │ ├── __init__.py
│ │ │ ├── session.py # SQLAlchemy Session model
│ │ │ ├── listing.py # SQLAlchemy Listing model
│ │ │ ├── transaction.py # SQLAlchemy Transaction model
│ │ │ └── agent.py # SQLAlchemy Agent model
│ │ │
│ │ ├── schemas/
│ │ │ ├── __init__.py
│ │ │ ├── messages.py # Pydantic message schemas
│ │ │ ├── hotels.py # Hotel vertical Pydantic schema
│ │ │ └── settlement.py # Settlement Pydantic schemas
│ │ │
│ │ └── verticals/
│ │ ├── __init__.py
│ │ ├── registry.py # Vertical schema registry
│ │ └── hotels.py # Hotel vertical validator
│ │
│ └── tests/
│ ├── conftest.py
│ ├── test_order_book.py
│ ├── test_state_machine.py
│ ├── test_matching.py
│ └── test_settlement.py
```

---

## 2. Tech Stack — Exact Versions

### Exchange (Python)

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115"
uvicorn = { extras = ["standard"], version = "^0.32" }
websockets = "^13.1"
sqlalchemy = { extras = ["asyncio"], version = "^2.0" }
alembic = "^1.14"
asyncpg = "^0.30" # async Postgres driver
redis = { extras = ["hiredis"], version = "^5.2" }
pydantic = "^2.10"
pydantic-settings = "^2.7"
stripe = "^11.4"
sendgrid = "^6.11"
cryptography = "^44.0" # Ed25519 signing
python-jose = "^3.3" # JWT for agent auth tokens
httpx = "^0.28" # async HTTP client
pytest = "^8.3"
pytest-asyncio = "^0.24"
```

### Skill SDK (TypeScript)

```json
// packages/skill-sdk/package.json
{
  "name": "@bookwithclaw/skill-sdk",
  "version": "0.1.0",
  "dependencies": {
    "@noble/ed25519": "^2.1.0",
    "ws": "^8.18.0",
    "zod": "^3.23.0",
    "uuid": "^11.0.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vitest": "^2.1.0",
    "@types/ws": "^8.5.0",
    "@types/uuid": "^10.0.0"
  }
}
```

---

## 3. Docker Compose (Local Dev)

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: bookwithclaw
      POSTGRES_USER: bookwithclaw
      POSTGRES_PASSWORD: localdev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data

  exchange:
    build:
      context: ./packages/exchange
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./packages/exchange:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  pgdata:
  redisdata:
```

---

## 4. Environment Variables

Create `.env.example` with all of these. App must fail loudly at startup if any required var is missing.

```bash
# Database
DATABASE_URL=postgresql+asyncpg://bookwithclaw:localdev@localhost:5432/bookwithclaw

# Redis
REDIS_URL=redis://localhost:6379/0

# Exchange
EXCHANGE_SECRET_KEY= # 32-byte hex secret for JWT signing - REQUIRED
EXCHANGE_HOST=localhost
EXCHANGE_PORT=8000
ENVIRONMENT=development # development | production

# Stripe Connect (Sprint 1 settlement)
STRIPE_SECRET_KEY= # sk_test_... for dev - REQUIRED
STRIPE_WEBHOOK_SECRET= # whsec_... - REQUIRED
STRIPE_PLATFORM_ACCOUNT= # Your Stripe platform account ID - REQUIRED

# SendGrid (notifications)
SENDGRID_API_KEY= # SG.xxx - REQUIRED
SENDGRID_FROM_EMAIL=notifications@bookwithclaw.com

# Exchange fee (basis points - 180 = 1.80%)
PLATFORM_FEE_BPS=180

# Session timeouts (seconds)
SESSION_OPEN_TIMEOUT=30
SESSION_NEGOTIATION_TIMEOUT=120
SESSION_SETTLEMENT_TIMEOUT=30

# Order book
ORDER_BOOK_TTL_SECONDS=3600 # 60 minutes default
MAX_INTENTS_PER_MINUTE=10
MAX_ASKS_PER_MINUTE=50
MAX_NEGOTIATION_ROUNDS=10
```

---

## 5. Core Implementation — Build Order

Build in this exact order. Each step should be fully working and tested before moving to the next.

### Step 1 — Project scaffold and DB migrations

1. Initialize the monorepo structure as defined in section 1
2. Set up `pyproject.toml` with all dependencies
3. Configure FastAPI app in `main.py` with lifespan context manager for DB and Redis connection pools
4. Create all SQLAlchemy models (see SCHEMA.md for exact table definitions)
5. Write Alembic initial migration — `alembic revision --autogenerate -m "initial"`
6. Verify migration runs clean: `alembic upgrade head`
7. Write `GET /health` endpoint that checks Postgres and Redis connectivity and returns status JSON

### Step 2 — Agent authentication

1. Implement `POST /agents/register` — accepts `{ public_key: string (hex Ed25519), role: "buyer"|"seller", email: string }` and returns a JWT auth token
2. JWT payload: `{ agent_id, role, public_key, iat, exp: 24h }`
3. Implement `verify_session_key` in `signing.py` — given a message bytes and a signature (hex) and a public key (hex), verify using Ed25519
4. Implement FastAPI dependency `get_current_agent` that extracts and validates JWT from `Authorization: Bearer <token>` header
5. All WebSocket endpoints and protected REST endpoints must use this dependency

### Step 3 — Reference skill implementations (TypeScript)

> **Note:** These are the Hotel Room Buyer Skill and Hotel Room Seller Skill — two reference implementations built internally to test the exchange. They are not a general SDK. Open-source developers will build their own skills from the skill template defined in SKILL_SPEC.md.

1. Implement all message type definitions in `messages.ts` with Zod schemas (see SCHEMA.md section 2 for exact schemas)
2. Implement `crypto.ts` — generate Ed25519 keypair, sign message bytes, export public key as hex
3. Implement `websocket.ts` — `ExchangeConnection` class: connect to `ws://host/ws/session/{session_id}`, auto-reconnect with exponential backoff (max 5 retries), send/receive typed messages, emit events
4. Implement `BuyerSkill` class in `buyer-skill.ts`:
   - Constructor: `{ exchangeUrl, agentId, authToken, config: BuyerConfig }`
   - `announce(intent: HotelBuyerIntent): Promise<SessionResult>` — main entry point
   - Internal: evaluate offers, generate counter-offers, enforce envelope
5. Implement `SellerSkill` class in `seller-skill.ts`:
   - Constructor: `{ exchangeUrl, agentId, authToken, config: SellerConfig }`
   - `listen(): void` — subscribe to order book, respond to matching intents
   - Internal: generate asks, evaluate counter-offers, enforce floor price
6. Write unit tests for both skill classes using mocked WebSocket

### Step 4 — Order book (Redis)

Implement `order_book.py` with these exact functions:

```python
async def publish_intent(intent: BuyerIntentMessage) -> str:
    """
    Store intent in Redis sorted set 'ob:bids:{vertical}' scored by timestamp.
    Set TTL on the key.
    Return intent_id.
    Key format: ob:bids:hotels
    Value: JSON-serialized intent
    Also store full intent at ob:intent:{intent_id} with TTL.
    """

async def publish_ask(ask: SellerAskMessage) -> str:
    """
    Store ask in Redis sorted set 'ob:asks:{vertical}' scored by price (ascending).
    Set TTL.
    Return ask_id.
    Key format: ob:asks:hotels
    Also store full ask at ob:ask:{ask_id} with TTL.
    """

async def get_matching_asks(intent: BuyerIntentMessage, limit: int = 5) -> list[SellerAskMessage]:
    """
    1. ZRANGEBYSCORE ob:asks:{vertical} from 0 to budget_ceiling (price filter)
    2. For each result, fetch full ask from ob:ask:{ask_id}
    3. Validate against vertical schema
    4. Score remaining asks (see matching algorithm below)
    5. Return top `limit` sorted by score descending
    """

async def remove_intent(intent_id: str) -> None:
    """Remove intent from sorted set and delete intent key."""

async def remove_ask(ask_id: str) -> None:
    """Remove ask from sorted set and delete ask key."""

async def get_active_intent_count(agent_id: str) -> int:
    """Count active intents for rate limiting."""
```

**Matching score formula** (implement exactly):

```python
def score_ask(ask: SellerAskMessage, intent: BuyerIntentMessage) -> float:
    # price_score: 1.0 when ask.price == 0, 0.0 when ask.price == intent.budget_ceiling
    price_score = 1.0 - (ask.price / intent.budget_ceiling)
    
    # terms_score: fraction of intent.preferred_terms satisfied by ask.terms
    preferred = set(intent.preferred_terms.keys())
    satisfied = sum(1 for k in preferred if ask.terms.get(k) == intent.preferred_terms[k])
    terms_score = satisfied / len(preferred) if preferred else 1.0
    
    # reputation_score: ask.seller_reputation_score normalized to 0-1 (stored 0-100)
    reputation_score = ask.seller_reputation_score / 100.0
    
    # stake_bonus: tiered bonus
    stake_bonus = 0.0
    if ask.stake_amount >= 10000:
        stake_bonus = 0.10
    elif ask.stake_amount >= 2500:
        stake_bonus = 0.08
    elif ask.stake_amount >= 500:
        stake_bonus = 0.05
    elif ask.stake_amount >= 100:
        stake_bonus = 0.02
    
    return (price_score * 0.40) + (terms_score * 0.35) + (reputation_score * 0.15) + (stake_bonus * 0.10)
```

### Step 5 — Negotiation state machine

Implement `state_machine.py`. The state machine is the heart of the exchange.

**States:**

```python
class SessionState(str, Enum):
    OPEN = "OPEN"
    MATCHING = "MATCHING"
    NEGOTIATING = "NEGOTIATING"
    AGREED = "AGREED"
    SETTLING = "SETTLING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
```

**Transitions (enforce these strictly — reject any message that arrives in wrong state):**

```
OPEN → MATCHING (exchange, on intent published)
MATCHING → NEGOTIATING (exchange, on first ask received)
NEGOTIATING→ AGREED (either party sends DealAccepted)
NEGOTIATING→ FAILED (timeout OR max_rounds exceeded OR SessionWalkaway)
AGREED → SETTLING (exchange, on initiating settlement)
SETTLING → COMPLETE (exchange, on settlement confirmed)
SETTLING → FAILED (exchange, on settlement error)
```

**Implement these methods:**

```python
class NegotiationStateMachine:
    async def open_session(self, intent: BuyerIntentMessage) -> Session
    async def transition(self, session_id: str, event: SessionEvent) -> Session
    async def handle_buyer_intent(self, session_id: str, msg: BuyerIntentMessage) -> None
    async def handle_seller_ask(self, session_id: str, msg: SellerAskMessage) -> None
    async def handle_buyer_counter(self, session_id: str, msg: BuyerCounterOfferMessage) -> None
    async def handle_seller_counter(self, session_id: str, msg: SellerCounterOfferMessage) -> None
    async def handle_deal_accepted(self, session_id: str, msg: DealAcceptedMessage) -> None
    async def handle_walkaway(self, session_id: str, msg: SessionWalkawayMessage) -> None
    async def check_timeouts(self) -> None  # called by background task every 5s
```

**Validation rules to enforce in each handler:**

- Round number must equal current session round + 1 (reject out-of-order messages)
- Counter-offer price must not exceed buyer's budget_ceiling (reject envelope violation)
- Counter-offer price must not go below seller's floor_price (reject — do not expose floor, just reject)
- Max rounds: if `msg.round_num > session.max_negotiation_rounds`, auto-trigger walkaway
- All incoming messages must pass signature verification before any processing

### Step 6 — WebSocket session endpoints

Implement `api/sessions.py`:

```python
# POST /sessions — create a new session, returns session_id + WebSocket URL
# WS /ws/session/{session_id} — main negotiation channel
# GET /sessions/{session_id} — get session status (REST polling fallback)
# GET /sessions/{session_id}/transcript — full message log for completed session
```

WebSocket handler logic:

1. On connect: verify JWT auth token, verify agent is registered, attach agent to session
2. On message: parse JSON, validate Pydantic schema, verify Ed25519 signature, route to state machine handler
3. On state machine event: broadcast relevant message to appropriate connected agents in session
4. On AGREED: close order book entries for this intent, terminate sibling sessions for same intent
5. On COMPLETE or FAILED: send final status to all connected agents, close WebSocket connections cleanly

### Step 7 — Stripe settlement

Implement `settlement/escrow.py`:

```python
async def create_payment_intent(session: Session) -> stripe.PaymentIntent:
    """
    Create a Stripe PaymentIntent for the agreed amount.
    Use destination charges to route to seller's Stripe Connect account.
    Platform fee = agreed_price_cents * PLATFORM_FEE_BPS / 10000
    Metadata: { bookwithclaw_session_id, bookwithclaw_booking_ref }
    """

async def confirm_escrow_funded(payment_intent_id: str) -> bool:
    """
    Check PaymentIntent status == 'requires_capture' (funds authorized, not yet captured).
    This is Phase 1 of the two-phase commit.
    """

async def capture_payment(payment_intent_id: str) -> stripe.PaymentIntent:
    """
    Capture the authorized PaymentIntent.
    This releases funds to seller.
    This is Phase 2 of the two-phase commit.
    Call only after seller inventory hold is confirmed.
    """

async def cancel_payment_intent(payment_intent_id: str) -> None:
    """Cancel and release escrow. Called on settlement failure."""
```

**Stripe webhook handler** (`api/webhooks.py`):

- Handle `payment_intent.amount_capturable_updated` → confirm Phase 1 complete
- Handle `payment_intent.succeeded` → confirm Phase 2 complete, trigger notifications
- Handle `payment_intent.payment_failed` → trigger settlement failure flow
- Always verify Stripe webhook signature before processing

### Step 8 — Notifications

Implement `settlement/notifier.py`:

```python
async def notify_deal_complete(session: Session, transaction: Transaction) -> None:
    """
    Send email to both buyer_email and seller_email.
    Buyer email: subject "Your booking is confirmed — {booking_ref}"
    Body: property name, checkin/checkout dates, room type, final rate, booking reference
    Seller email: subject "New booking confirmed — {booking_ref}"
    Body: checkin/checkout dates, room type, agreed rate, platform fee, net amount, guest info
    Use SendGrid dynamic templates if template IDs are set in env, else plain text.
    """
```

### Step 9 — Hotel vertical schema validation

Implement `verticals/hotels.py`:

```python
class HotelVerticalValidator:
    def validate_intent(self, intent_fields: dict) -> HotelIntentFields
    def validate_ask(self, ask_fields: dict) -> HotelAskFields
    def check_compatibility(self, intent: HotelIntentFields, ask: HotelAskFields) -> bool:
        """
        Returns True only if:
        - ask.checkin_date <= intent.checkin_date (seller available from)
        - ask.checkout_date >= intent.checkout_date (seller available to)
        - ask.room_type in intent.acceptable_room_types (or intent list is empty = any)
        - ask.max_occupants >= intent.occupants
        """
```

### Step 10 — Integration test

Write a full end-to-end integration test in `tests/test_e2e.py`:

1. Register a buyer agent and a seller agent
2. Seller publishes a hotel ask to the order book
3. Buyer announces a hotel intent
4. Exchange matches them and opens a negotiation session
5. Simulate 2 rounds of counter-offers via WebSocket
6. Buyer accepts seller's counter-offer
7. Mock Stripe to confirm escrow funded + captured
8. Assert session state is COMPLETE
9. Assert both agents received SettlementComplete message
10. Assert Transaction record exists in DB with correct amounts

---

## 6. API Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | None | Exchange health check |
| POST | /agents/register | None | Register new agent, get JWT |
| POST | /sessions | Bearer JWT | Create new negotiation session |
| WS | /ws/session/{id} | Bearer JWT (query param) | Main negotiation channel |
| GET | /sessions/{id} | Bearer JWT | Get session status |
| GET | /sessions/{id}/transcript | Bearer JWT | Full message log |
| POST | /webhooks/stripe | Stripe-Signature header | Stripe event receiver |

---

## 7. Error Handling Standards

All API errors must return this shape:

```json
{
  "error": {
    "code": "ENVELOPE_VIOLATION",
    "message": "Counter-offer price exceeds buyer budget ceiling",
    "session_id": "...",
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

**Error codes to implement:**

- `INVALID_SIGNATURE` — Ed25519 verification failed
- `ENVELOPE_VIOLATION` — message violates agent's configured parameters
- `INVALID_STATE_TRANSITION` — message not valid in current session state
- `RATE_LIMIT_EXCEEDED` — agent exceeded intent/ask rate limit
- `SESSION_NOT_FOUND` — session_id does not exist
- `UNAUTHORIZED` — JWT missing, expired, or invalid
- `VERTICAL_SCHEMA_ERROR` — message fields fail vertical schema validation
- `SETTLEMENT_FAILED` — Stripe payment failed
- `SESSION_TIMEOUT` — session exceeded time limit

---

## 8. Testing Requirements

Minimum test coverage before Sprint 1 is "done":

- All state machine transitions: happy path + invalid transition rejection
- Matching algorithm: scoring formula correctness, edge cases (no matching asks, all asks over budget)
- Envelope validation: buyer ceiling enforcement, seller floor enforcement
- Signature verification: valid sig passes, tampered message fails, wrong key fails
- Settlement two-phase commit: Phase 1 success, Phase 1 failure (escrow), Phase 2 success, Phase 2 failure
- WebSocket session lifecycle: connect, negotiate, close cleanly
- Hotel vertical schema: valid intent, valid ask, compatibility check pass/fail

Run tests with: `pytest packages/exchange/tests/ -v --asyncio-mode=auto`

---

## 9. What "Done" Looks Like for Sprint 1

Sprint 1 is complete when:

1. `docker-compose up` starts all services with no errors
2. `alembic upgrade head` runs all migrations cleanly
3. All tests pass: `pytest` green
4. The end-to-end integration test passes (Step 10 above)
5. A Buyer Skill instance and Seller Skill instance can connect to the local exchange, complete a hotel negotiation, and both receive a `SettlementComplete` message (Stripe in test mode)
6. Both human owners receive SendGrid notification emails (or console-logged in dev mode if `ENVIRONMENT=development`)
