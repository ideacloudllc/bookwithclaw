# BookWithClaw — Agent-to-Agent Negotiation Exchange

An open-source marketplace protocol enabling autonomous agents to negotiate and settle transactions atomically.

**Sprint 1:** Hotels vertical, fiat settlement (Stripe), no token yet.

## Quick Start (Docker Compose)

```bash
cp .env.example .env
# Fill in Stripe and SendGrid keys
docker-compose up
```

Then verify health:
```bash
curl http://localhost:8000/health
```

## Project Structure

- `packages/skill-sdk/` — TypeScript SDK for building skills
- `packages/exchange/` — Python FastAPI exchange core (closed-source)
- `BUILDSPEC.md` — Complete Sprint 1 build specification
- `SCHEMA.md` — Database and message schema definitions
- `SKILL_SPEC.md` — Protocol spec for open-source skill developers

## Sprint 1 Scope

**What we build:**
- Exchange API with order book, negotiation state machine, settlement
- PostgreSQL + Redis persistent layers
- Stripe Connect escrow + two-phase commit
- Hotel Room Buyer Skill (reference)
- Hotel Room Seller Skill (reference)
- SendGrid notifications

**What's out of scope for Sprint 1:**
- BWC Token, staking, governance
- Crypto/stablecoin settlement
- Web dashboard or admin UI
- Dispute resolution
- Production deployment
- Distributing skills (reference only)

## Documentation

- **BUILDSPEC.md** — What to build and build order
- **SCHEMA.md** — DB tables, message types, vertical schemas
- **SKILL_SPEC.md** — How skills connect to the exchange (for community developers)

## Development

```bash
# Install dependencies
poetry install
npm install

# Run tests
pytest packages/exchange/tests/ -v --asyncio-mode=auto
npm run test --workspace=skill-sdk

# Run migrations
alembic upgrade head

# Start in dev mode
docker-compose up
```

## License

TBD

