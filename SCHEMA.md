# SCHEMA.md — Database and Message Schemas

*To be completed with detailed table definitions, Pydantic schemas, and vertical validators.*

## Part 1: Database Schema

Database tables will be defined in SQLAlchemy models under `packages/exchange/app/models/`.

Tables:
- `agents` — Agent registration (public key, role, email)
- `sessions` — Negotiation sessions (state machine, participants)
- `transactions` — Settlement records (price, fees, Stripe IDs)
- Additional tables for order book persistence (optional, Redis is primary)

## Part 2: Message Schemas

Pydantic message definitions for:
- BuyerIntent
- SellerAsk
- BuyerCounterOffer
- SellerCounterOffer
- DealAccepted
- SessionWalkaway
- SettlementComplete
- SettlementFailed

## Part 3: Hotel Vertical Schema

Hotel-specific fields:
- checkin_date, checkout_date
- room_type
- occupants
- preferred_terms (amenities, cancellation, etc.)

See `BUILDSPEC.md` section 9 for validation rules.
