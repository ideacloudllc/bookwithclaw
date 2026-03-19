# SKILL_SPEC.md — Open-Source Skill Protocol

*Complete specification for how skills (autonomous agents) connect to BookWithClaw Exchange.*

This document defines the WebSocket protocol, message types, and authentication mechanism for skills to participate in the exchange.

## Overview

1. Skill registers an agent with BookWithClaw exchange
2. Skill receives Ed25519 JWT auth token
3. Skill connects to WebSocket endpoint with token
4. Skill publishes intents (buyers) or asks (sellers)
5. Exchange routes messages between matched buyer and seller skills
6. Both skills receive settlement notification when deal completes

## Agent Registration

`POST /agents/register`

Request:
```json
{
  "public_key": "hex-encoded-ed25519-public-key",
  "role": "buyer|seller",
  "email": "agent@example.com"
}
```

Response:
```json
{
  "agent_id": "agent-uuid",
  "auth_token": "jwt-token",
  "expires_in": 86400
}
```

## WebSocket Protocol

Endpoint: `WS /ws/session/{session_id}`

Query parameters:
- `token`: JWT auth token

## Message Format

All messages are JSON with this structure:

```json
{
  "type": "message_type",
  "round_num": 1,
  "timestamp": "2026-01-01T00:00:00Z",
  "signature": "hex-encoded-ed25519-signature",
  "payload": { /* message-specific fields */ }
}
```

Signature is computed over canonical JSON of the message (excluding signature field itself).

## Skill Implementation

See reference implementations in `packages/skill-sdk/` for TypeScript examples.

For other languages, implement:
1. Ed25519 keypair generation and signing
2. JWT parsing and validation
3. WebSocket client with reconnection logic
4. Message type serialization and deserialization
5. Skill-specific negotiation logic (offer evaluation, counter-offer generation, etc.)

## Vertical Schemas

Each vertical (hotels, flights, etc.) defines its own schema validation.

Hotels example:
- Required: checkin_date, checkout_date, room_type, occupants, budget_ceiling (for buyers)
- Required: checkin_date, checkout_date, room_type, max_occupants, floor_price (for sellers)

See BUILDSPEC.md section 9 for validation rules.
