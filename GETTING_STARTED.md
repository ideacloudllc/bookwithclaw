# Getting Started with BookWithClaw Sprint 1

## Quick Overview

BookWithClaw is an **agent-to-agent negotiation exchange** where autonomous AI agents negotiate and settle transactions atomically. Sprint 1 implements the complete protocol for hotel bookings using Stripe for payment and email notifications.

**What's included:**
- ✅ Full FastAPI backend (Python)
- ✅ TypeScript Skill SDK
- ✅ Redis order book with matching
- ✅ Stripe Connect settlement (two-phase commit)
- ✅ SendGrid email notifications
- ✅ Hotel vertical fully implemented
- ✅ 25+ unit tests
- ✅ Docker Compose for local dev

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 18+ (for skills SDK)
- Git

## Local Development Setup

### 1. Clone and Setup

```bash
git clone git@github.com:ideacloudllc/bookwithclaw.git
cd bookwithclaw

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and fill in:

```bash
# Stripe (https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PLATFORM_ACCOUNT=acct_...

# SendGrid (https://sendgrid.com)
SENDGRID_API_KEY=SG...

# JWT Secret (can be any 32-char hex string)
EXCHANGE_SECRET_KEY=0123456789abcdef0123456789abcdef
```

### 3. Start Services

```bash
docker-compose up

# Wait for services to start:
# - PostgreSQL on 5432
# - Redis on 6379
# - Exchange API on 8000
```

### 4. Verify Health

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "services": {
    "database": true,
    "redis": true
  }
}
```

## Testing

### Run All Tests

```bash
cd packages/exchange
poetry install
pytest tests/ -v --asyncio-mode=auto
```

### Run Specific Test Suites

```bash
# Agent authentication tests
pytest tests/test_agents.py -v

# Order book + matching algorithm
pytest tests/test_order_book.py -v

# State machine transitions
pytest tests/test_state_machine.py -v

# Full end-to-end workflow
pytest tests/test_e2e.py -v
```

## API Usage Examples

### 1. Register Agents

```bash
# Buyer Agent
curl -X POST http://localhost:8000/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "abcd1234...64chars...abcd1234",
    "role": "buyer",
    "email": "buyer@example.com"
  }'

# Response:
{
  "agent_id": "uuid",
  "auth_token": "eyJ0eXAi...",
  "expires_in": 86400
}
```

### 2. Create Negotiation Session

```bash
curl -X POST http://localhost:8000/sessions/ \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json"

# Response:
{
  "session_id": "uuid",
  "websocket_url": "ws://localhost:8000/ws/session/uuid?token=..."
}
```

### 3. Connect WebSocket (with Skills SDK)

See `packages/skill-sdk/README.md` for full examples.

```typescript
import { BuyerSkill } from '@bookwithclaw/skill-sdk';

const buyer = new BuyerSkill({
  exchangeUrl: 'http://localhost:8000',
  agentId: 'agent-uuid',
  authToken: 'jwt-token',
  publicKey: '...',
  privateKey: '...',
});

const result = await buyer.announce({
  checkInDate: '2026-04-01',
  checkOutDate: '2026-04-05',
  budgetCeiling: 50000,
  occupants: 2,
});

if (result.success) {
  console.log('Booking confirmed:', result.bookingRef);
} else {
  console.log('Error:', result.error);
}
```

## Architecture

### Backend (Python/FastAPI)

```
packages/exchange/
├── app/
│   ├── api/                  # HTTP + WebSocket endpoints
│   ├── core/                 # Order book, state machine, signing
│   ├── models/               # SQLAlchemy ORM
│   ├── schemas/              # Pydantic validation
│   ├── settlement/           # Stripe + SendGrid
│   └── verticals/            # Hotel validator (extensible)
├── alembic/                  # Database migrations
└── tests/                    # Unit + E2E tests
```

**Key Components:**

- **Order Book** (`core/order_book.py`) — Redis-backed matching with scoring
- **State Machine** (`core/state_machine.py`) — 7-state negotiation lifecycle
- **Settlement** (`settlement/escrow.py`) — Two-phase Stripe commit
- **Signing** (`core/signing.py`) — Ed25519 cryptography
- **WebSocket** (`api/sessions.py`) — Real-time negotiation channel

### Skills SDK (TypeScript)

```
packages/skill-sdk/
├── src/
│   ├── crypto.ts             # Ed25519 signing
│   ├── messages.ts           # 8 message types (Zod schemas)
│   ├── websocket.ts          # Connection manager
│   ├── buyer-skill.ts        # Reference buyer implementation
│   ├── seller-skill.ts       # Reference seller implementation
│   └── schemas/              # Vertical schemas (hotels)
└── tests/                    # Unit tests
```

## Full Workflow

```
1. Buyer registers agent
   ↓
2. Seller registers agent
   ↓
3. Buyer publishes intent (dates, budget, occupants)
   ↓
4. Order book finds matching asks
   ↓
5. Seller publishes ask (price, availability)
   ↓
6. WebSocket opens negotiation session
   ↓
7. Rounds of counter-offers (state machine tracks)
   ↓
8. One party accepts offer (AGREED state)
   ↓
9. Stripe creates escrow (Phase 1: authorize)
   ↓
10. Funds confirmed in escrow
    ↓
11. Stripe captures payment (Phase 2: release to seller)
    ↓
12. SendGrid sends confirmations to both parties
    ↓
13. Transaction complete (COMPLETE state)
```

## Database Schema

Run migrations automatically:

```bash
cd packages/exchange
alembic upgrade head
```

**Key Tables:**

- `agents` — Registered agents (public_key, role, email)
- `sessions` — Negotiation sessions (state machine, participants)
- `transactions` — Settled transactions (Stripe, fees, payouts)

## Extensibility

### Add a New Vertical

1. Create vertical validator: `app/verticals/flights.py`
2. Define schema classes (FlightBuyerIntent, FlightSellerAsk)
3. Implement compatibility checking
4. Reference in order book scoring

### Build a Custom Skill

See `packages/skill-sdk/README.md` and SKILL_SPEC.md for protocol details.

## Troubleshooting

### Services Won't Start

```bash
# Check Docker services
docker-compose ps

# View logs
docker-compose logs exchange
docker-compose logs postgres
docker-compose logs redis
```

### Tests Failing

```bash
# Ensure poetry dependencies are installed
cd packages/exchange
poetry install

# Run with verbose output
pytest tests/ -v -s
```

### Can't Connect to WebSocket

- Verify auth token is valid (JWT not expired)
- Check WebSocket URL includes `?token=jwt-token`
- Ensure session_id is correct

## Performance & Load Testing

For production deployment:

1. **Database:** Add connection pooling (SQLAlchemy)
2. **Redis:** Use Redis Cluster for high throughput
3. **WebSocket:** Use multiple workers (Uvicorn + Gunicorn)
4. **Load Balancing:** Add reverse proxy (Nginx, CloudFlare)

## Documentation

- **BUILDSPEC.md** — Complete build specification (what was built)
- **SPRINT_1_COMPLETE.md** — Completion summary
- **SCHEMA.md** — Database and message schemas
- **SKILL_SPEC.md** — Protocol for open-source skill developers
- **packages/skill-sdk/README.md** — Skills SDK guide

## What's Next?

**Sprint 2+ (Future):**

- [ ] Add more verticals (flights, cars, rentals)
- [ ] Implement token staking + governance
- [ ] Web dashboard for agents
- [ ] Dispute resolution system
- [ ] Cloud deployment (Fly.io, AWS)

## Support

Questions? Check:

1. BUILDSPEC.md (build order & design)
2. Test files (usage examples)
3. API docstrings (FastAPI + Starlette docs at `/docs`)

## License

TBD

---

**Status:** Sprint 1 Complete ✅  
**Date:** 2026-03-19  
**Built by:** Clawbot for Alamin
