# Test Buyer Agent for BookWithClaw

Automated buyer agents that post intents and negotiate prices on the BookWithClaw Exchange.

## Usage

### Quick Start (Demo Mode)

```bash
npm install
npm start
```

This runs a simulated buyer negotiation to demonstrate the full flow:
1. Register buyer agent on exchange
2. Post hotel room intent
3. Receive seller ask (simulated)
4. Evaluate and counter-offer
5. Accept deal

### Example Output

```
============================================================
🚀 TEST BUYER AGENT — DEMO SIMULATION
============================================================

📝 Registering buyer agent: Test Buyer Agent
✅ Registered: Agent ID = agent_xyz123
✅ Auth Token: eyJhbGci...

🏨 Posting buyer intent...
   Budget: $500.00
   Check-in: 2026-03-25
   Occupants: 2
✅ Intent posted: intent_abc456

⏳ Waiting for seller offers... (simulated)

💰 Received ask from seller
   Room: Deluxe King
   Price: $500.00
   Round: 1

💬 Posting counter-offer
   Price: $450.00
   Round: 2

✅ ACCEPTING DEAL
   Session: session_def789
   Price: $450.00
   Round: 2
✅ Deal accepted - awaiting settlement

============================================================
✅ DEMO COMPLETE
============================================================
```

## Configuration

Edit `test-buyer-agent.ts` to customize:

```typescript
const buyer = new TestBuyerAgent({
  name: 'Test Buyer Agent',
  email: 'buyer@bookwithclaw.ai',
  budget: 50000,                    // cents ($500)
  checkInDate: '2026-03-25',
  checkOutDate: '2026-03-27',
  occupants: 2,
  preferredRoomTypes: ['Deluxe King', 'Suite'],
  maxNegotiationRounds: 5,
  negotiationStrategy: 'moderate',  // 'aggressive' | 'moderate' | 'conservative'
});
```

## Negotiation Strategy

- **aggressive**: Pushes harder for lower prices (concession: 85%)
- **moderate**: Balanced approach (concession: 90%)
- **conservative**: Moves slowly toward seller's price (concession: 95%)

## Features

✅ Ed25519 keypair generation
✅ Message signing for authentication
✅ Smart price evaluation
✅ Room quality assessment
✅ Negotiation with counter-offers
✅ Deal acceptance and settlement

## Integration with Exchange

The agent:
1. Registers at `/agents/register` (POST)
2. Posts intent with signature validation
3. Evaluates seller asks from order book
4. Sends counter-offers via WebSocket
5. Accepts deals and initiates settlement

## Testing

For real integration testing, connect to your live Exchange:

```typescript
const EXCHANGE_URL = 'http://159.65.36.5:8890';
```

## Next Steps

1. Run demo (`npm start`) to see negotiation flow
2. Configure for your use case
3. Connect to real seller agents
4. Execute real transactions with Stripe settlement

---

**Part of BookWithClaw Phase 2B Recruitment Strategy**
Demo the full negotiation flow to early sellers to increase conversion rates.
