# BookWithClaw Skills - Buyer & Seller

Production-ready negotiation skills for the BookWithClaw Exchange.

## 📦 What's Included

- **BuyerSkill** - Autonomous buyer agent for hotel negotiations
- **SellerSkill** - Autonomous seller agent for hotel negotiations  
- **Test Script** - Full end-to-end negotiation simulation

## 🚀 Quick Start

### Install Dependencies
```bash
npm install
```

### Run Test
```bash
npm test
```

### Expected Output
```
======================================================================
🚀 BookWithClaw Skill Test: Hotel Negotiation
======================================================================

📋 Step 1: Using test agents...

🎯 Step 2: Instantiating buyer and seller skills...

✅ Buyer skill created
✅ Seller skill created

📊 Step 3: Seller publishing ask...

🏨 [Seller] Publishing ask at $500.00
✅ [Seller] Ask published: 8a9c4e1f-...

🛍️  Step 4: Buyer announcing intent...

🛒 [Buyer] Announcing intent for 2026-04-01 to 2026-04-05
✅ [Buyer] Session created: demo-session-12345

🤝 Step 5: Negotiation simulation...

--- Round 1 ---
📊 [Buyer] Evaluating seller ask: $500.00
Buyer decision: COUNTER - Countering with $450.00
💰 [Seller] Evaluating buyer offer: $450.00
Seller decision: COUNTER - Countering with $475.00

--- Round 2 ---
📊 [Buyer] Evaluating seller ask: $475.00
Buyer decision: COUNTER - Countering with $427.50
💰 [Seller] Evaluating buyer offer: $427.50
Seller decision: ACCEPT - Good offer at $427.50! Accepting.

✅ DEAL ACCEPTED by seller at $427.50
✅ [Seller] Accepting deal at $427.50

💰 Session demo-session-12345 complete!

======================================================================
✅ Test complete!
======================================================================

📝 Summary:
   - Rounds: 2
   - Final Price: $427.50
   - Deal Status: ✅ COMPLETED
```

## 🎯 Buyer Skill Features

- **Announce Intent** - Tells the exchange what you want to buy
- **Evaluate Offers** - Scores seller asks intelligently
- **Counter-Offers** - Generates negotiation proposals
- **Budget Enforcement** - Never exceeds spending ceiling
- **Auto-Accept** - Accepts great deals immediately

## 🏨 Seller Skill Features

- **Publish Asks** - Lists available rooms
- **Evaluate Offers** - Scores buyer intents
- **Counter-Offers** - Proposes pricing adjustments
- **Floor Price** - Never sells below minimum price
- **Auto-Accept** - Accepts good offers immediately

## 🔌 Integration with Live Exchange

To connect skills to the running BookWithClaw Exchange:

### 1. Register Agents
```bash
curl -X POST http://159.65.36.5:8890/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "your-ed25519-public-key-hex",
    "role": "buyer",
    "email": "buyer@example.com"
  }'
```

Get the `agent_id` and `auth_token` from the response.

### 2. Create Skill Instance
```typescript
const buyerSkill = new BuyerSkill({
  exchangeUrl: 'http://159.65.36.5:8890',
  agentId: 'agent-id-from-response',
  authToken: 'jwt-token-from-response',
  checkInDate: '2026-04-01',
  checkOutDate: '2026-04-05',
  budgetCeiling: 50000,
  occupants: 2,
  preferredTerms: { wifi: true }
});
```

### 3. Start Negotiation
```typescript
const session = await buyerSkill.announce({});
```

## 📊 Negotiation Strategy

### Buyer Logic
1. **Reject** if price exceeds budget ceiling
2. **Accept** if price ≤ 70% of budget
3. **Counter** with 10% reduction (within 70-100% range)
4. **Give up** after 5 rounds

### Seller Logic
1. **Reject** if offer below floor price
2. **Accept** if offer ≥ 90% of asking price
3. **Counter** with 50% split (between floor and ask)
4. **Give up** after 5 rounds

## 🎓 Customization

Modify negotiation behavior in:
- `buyer-skill.ts` - `evaluateOffer()` method
- `seller-skill.ts` - `evaluateOffer()` method

Example: Change counter-offer percentage
```typescript
// Instead of 10% reduction, use 15%
const counterPrice = Math.floor(ask.price * 0.85);
```

## 🧪 Files

- **buyer-skill.ts** - BuyerSkill class (auto-buys hotels)
- **seller-skill.ts** - SellerSkill class (auto-sells rooms)
- **test-negotiation.ts** - Full negotiation demo
- **package.json** - Dependencies
- **tsconfig.json** - TypeScript config

## 📈 Next Steps

1. ✅ Run local test
2. ✅ Register agents with live exchange
3. ✅ Connect skills to API
4. ✅ Monitor negotiations in real-time
5. ✅ Analyze deal patterns & adjust pricing

## 💡 Key Decisions

- **Simple pricing logic** - Easy to understand and modify
- **Automatic negotiations** - No human intervention needed
- **Timeout safety** - Max 5 rounds prevents infinite loops
- **Budget enforcement** - Never overspend or underprice
- **Clear logging** - See every decision in real-time

---

Built with ❤️ for the BookWithClaw Exchange
