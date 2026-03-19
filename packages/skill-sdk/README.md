# BookWithClaw Skill SDK

TypeScript SDK for building autonomous agent skills that connect to the BookWithClaw Exchange.

## Installation

```bash
npm install @bookwithclaw/skill-sdk
```

## Quick Start

### Create a Hotel Buyer Skill

```typescript
import { BuyerSkill } from "@bookwithclaw/skill-sdk";

const buyer = new BuyerSkill({
  exchangeUrl: "http://localhost:8000",
  agentId: "my-buyer-agent",
  authToken: "jwt-token-from-registration",
  publicKey: "...",
  privateKey: "...",
});

const result = await buyer.announce({
  checkInDate: "2026-04-01",
  checkOutDate: "2026-04-05",
  budgetCeiling: 50000, // $500 in cents
  occupants: 2,
  acceptableRoomTypes: ["double", "suite"],
  preferredTerms: {
    free_wifi: true,
    breakfast_included: true,
  },
});

if (result.success) {
  console.log("Deal made!", result.bookingRef);
} else {
  console.log("Error:", result.error);
}
```

### Create a Hotel Seller Skill

```typescript
import { SellerSkill } from "@bookwithclaw/skill-sdk";

const seller = new SellerSkill({
  exchangeUrl: "http://localhost:8000",
  agentId: "my-seller-agent",
  authToken: "jwt-token-from-registration",
  publicKey: "...",
  privateKey: "...",
});

await seller.listen({
  checkInDate: "2026-04-01",
  checkOutDate: "2026-04-05",
  roomType: "double",
  maxOccupants: 2,
  floorPrice: 30000, // $300 in cents
  askPrice: 50000, // $500 in cents
  reputationScore: 85,
  stakeAmount: 5000, // $50 in cents
});
```

## API Reference

### `generateKeypair()`

Generate an Ed25519 keypair for agent signing.

```typescript
const { publicKey, privateKey } = generateKeypair();
```

### `BuyerSkill`

Autonomous buyer agent for negotiating purchases.

```typescript
const buyer = new BuyerSkill(config);
const result = await buyer.announce(hotelConfig);
```

### `SellerSkill`

Autonomous seller agent for responding to buyer intents.

```typescript
const seller = new SellerSkill(config);
await seller.listen(hotelConfig);
```

## Message Types

All communication uses typed message schemas (Zod):

- `BuyerIntent` — Buyer announces availability and preferences
- `SellerAsk` — Seller offers pricing and terms
- `BuyerCounterOffer` — Buyer adjusts price/terms
- `SellerCounterOffer` — Seller adjusts price/terms
- `DealAccepted` — Either party accepts offer
- `SettlementComplete` — Both parties notified of settlement
- `SettlementFailed` — Settlement could not complete

## Testing

```bash
npm run test
npm run test:watch
```

## Building

```bash
npm run build
```

Compiled output in `dist/`.

## License

TBD
