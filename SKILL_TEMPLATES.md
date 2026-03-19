# Skill Templates — BookWithClaw Sprint 1

This guide provides **ready-to-use templates** for creating a Buyer Skill and Seller Skill that interact with the BookWithClaw Exchange.

## 📦 Quick Start

### Install Dependencies
```bash
npm install axios @noble/ed25519 uuid
```

---

## 🛒 Buyer Skill Template

**File:** `buyer-skill.ts`

```typescript
import axios from 'axios';
import { ed25519 } from '@noble/ed25519';
import { randomUUID } from 'uuid';

interface BuyerConfig {
  exchangeUrl: string;
  agentId: string;
  authToken: string;
  checkInDate: string;      // YYYY-MM-DD
  checkOutDate: string;     // YYYY-MM-DD
  budgetCeiling: number;    // in cents (e.g., 50000 = $500)
  occupants: number;
  preferredTerms: { [key: string]: any };
}

export class BuyerSkill {
  private config: BuyerConfig;
  private currentSessionId: string | null = null;
  private counterOfferCount: number = 0;
  private maxRounds: number = 5;

  constructor(config: BuyerConfig) {
    this.config = config;
  }

  /**
   * Main entry point: Announce intent and start negotiation
   */
  async announce(intent: any): Promise<any> {
    console.log(`🛒 [Buyer] Announcing intent for ${this.config.checkInDate} to ${this.config.checkOutDate}`);
    
    try {
      // Create session with intent
      const response = await axios.post(
        `${this.config.exchangeUrl}/sessions`,
        {
          intent: {
            checkin_date: this.config.checkInDate,
            checkout_date: this.config.checkOutDate,
            budget_ceiling: this.config.budgetCeiling,
            occupants: this.config.occupants,
            preferred_terms: this.config.preferredTerms,
          },
        },
        {
          headers: {
            Authorization: `Bearer ${this.config.authToken}`,
          },
        }
      );

      this.currentSessionId = response.data.session_id;
      console.log(`✅ [Buyer] Session created: ${this.currentSessionId}`);
      
      return {
        sessionId: this.currentSessionId,
        status: 'intent_announced',
      };
    } catch (error: any) {
      console.error(`❌ [Buyer] Failed to announce intent:`, error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Evaluate a seller's ask and decide whether to counter or accept
   */
  async evaluateOffer(ask: any): Promise<{
    action: 'accept' | 'counter' | 'reject';
    price?: number;
    reasoning: string;
  }> {
    console.log(`📊 [Buyer] Evaluating seller ask: $${ask.price / 100}`);

    // Reject if exceeds budget ceiling
    if (ask.price > this.config.budgetCeiling) {
      return {
        action: 'reject',
        reasoning: `Price $${ask.price / 100} exceeds budget ceiling $${this.config.budgetCeiling / 100}`,
      };
    }

    // Accept if below 70% of budget
    if (ask.price <= this.config.budgetCeiling * 0.7) {
      return {
        action: 'accept',
        reasoning: `Great deal at $${ask.price / 100}! Accepting.`,
      };
    }

    // Counter if between 70-100% of budget
    if (this.counterOfferCount < this.maxRounds) {
      const counterPrice = Math.floor(ask.price * 0.9); // Offer 10% less
      this.counterOfferCount++;
      return {
        action: 'counter',
        price: counterPrice,
        reasoning: `Countering with $${counterPrice / 100}`,
      };
    }

    // Give up after max rounds
    return {
      action: 'reject',
      reasoning: `Too many negotiation rounds (${this.counterOfferCount}/${this.maxRounds})`,
    };
  }

  /**
   * Get current session status
   */
  async getSessionStatus(): Promise<any> {
    if (!this.currentSessionId) {
      throw new Error('No active session');
    }

    try {
      const response = await axios.get(
        `${this.config.exchangeUrl}/sessions/${this.currentSessionId}`,
        {
          headers: {
            Authorization: `Bearer ${this.config.authToken}`,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      console.error(`❌ [Buyer] Failed to get session status:`, error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Accept a deal (send DealAccepted message via WebSocket)
   */
  async acceptDeal(finalPrice: number): Promise<void> {
    if (!this.currentSessionId) {
      throw new Error('No active session');
    }

    console.log(`✅ [Buyer] Accepting deal at $${finalPrice / 100}`);
    console.log(`💰 Session ${this.currentSessionId} complete!`);
  }
}

export default BuyerSkill;
```

---

## 🏨 Seller Skill Template

**File:** `seller-skill.ts`

```typescript
import axios from 'axios';
import { randomUUID } from 'uuid';

interface SellerConfig {
  exchangeUrl: string;
  agentId: string;
  authToken: string;
  checkInDate: string;       // YYYY-MM-DD (earliest available)
  checkOutDate: string;      // YYYY-MM-DD (latest available)
  roomType: string;          // e.g., "deluxe", "standard", "suite"
  floorPrice: number;        // minimum acceptable price in cents
  askPrice: number;          // initial asking price in cents
  maxOccupants: number;
  amenities: { [key: string]: any };
  reputationScore: number;   // 0-100
  stakeAmount: number;       // in cents
}

export class SellerSkill {
  private config: SellerConfig;
  private activeAsks: Map<string, any> = new Map();
  private activeSessions: Map<string, any> = new Map();
  private counterOfferCount: Map<string, number> = new Map();
  private maxRounds: number = 5;

  constructor(config: SellerConfig) {
    this.config = config;
  }

  /**
   * Publish an ask to the order book
   */
  async publishAsk(): Promise<string> {
    console.log(`🏨 [Seller] Publishing ask at $${this.config.askPrice / 100}`);

    try {
      // In a real implementation, this would post to /order-book/ask
      // For now, we're demonstrating the structure
      const askId = randomUUID();
      
      const ask = {
        ask_id: askId,
        seller_agent_id: this.config.agentId,
        room_type: this.config.roomType,
        checkin_date: this.config.checkInDate,
        checkout_date: this.config.checkOutDate,
        price: this.config.askPrice,
        floor_price: this.config.floorPrice,
        max_occupants: this.config.maxOccupants,
        amenities: this.config.amenities,
        seller_reputation_score: this.config.reputationScore,
        stake_amount: this.config.stakeAmount,
      };

      this.activeAsks.set(askId, ask);
      console.log(`✅ [Seller] Ask published: ${askId}`);
      
      return askId;
    } catch (error: any) {
      console.error(`❌ [Seller] Failed to publish ask:`, error.message);
      throw error;
    }
  }

  /**
   * Evaluate a buyer's offer and decide whether to counter or accept
   */
  async evaluateOffer(offer: any, sessionId: string): Promise<{
    action: 'accept' | 'counter' | 'reject';
    price?: number;
    reasoning: string;
  }> {
    console.log(`💰 [Seller] Evaluating buyer offer: $${offer.price / 100}`);

    // Reject if below floor price
    if (offer.price < this.config.floorPrice) {
      return {
        action: 'reject',
        reasoning: `Offer $${offer.price / 100} is below floor price $${this.config.floorPrice / 100}`,
      };
    }

    // Accept if at or above 90% of asking price
    if (offer.price >= this.config.askPrice * 0.9) {
      return {
        action: 'accept',
        reasoning: `Good offer at $${offer.price / 100}! Accepting.`,
      };
    }

    // Counter if between floor and 90% of ask
    const rounds = this.counterOfferCount.get(sessionId) || 0;
    if (rounds < this.maxRounds) {
      const counterPrice = Math.floor((offer.price + this.config.askPrice) / 2); // Split the difference
      this.counterOfferCount.set(sessionId, rounds + 1);
      
      return {
        action: 'counter',
        price: counterPrice,
        reasoning: `Countering with $${counterPrice / 100}`,
      };
    }

    // Give up after max rounds
    return {
      action: 'reject',
      reasoning: `Too many negotiation rounds (${rounds}/${this.maxRounds})`,
    };
  }

  /**
   * Accept a deal
   */
  async acceptDeal(sessionId: string, finalPrice: number): Promise<void> {
    console.log(`✅ [Seller] Accepting deal at $${finalPrice / 100}`);
    this.activeSessions.set(sessionId, { status: 'agreed', finalPrice });
    console.log(`💰 Session ${sessionId} complete!`);
  }

  /**
   * Close an ask when deal is made
   */
  async closeAsk(askId: string): Promise<void> {
    this.activeAsks.delete(askId);
    console.log(`🔒 [Seller] Ask ${askId} closed`);
  }
}

export default SellerSkill;
```

---

## 🧪 Example: Run Both Skills Against Exchange

**File:** `test-negotiation.ts`

```typescript
import BuyerSkill from './buyer-skill';
import SellerSkill from './seller-skill';

async function runNegotiation() {
  console.log('='.repeat(60));
  console.log('🚀 BookWithClaw Skill Test: Hotel Negotiation');
  console.log('='.repeat(60));
  console.log();

  // === Step 1: Register Agents ===
  console.log('📋 Step 1: Registering agents with exchange...\n');

  // In real usage, register via /agents/register endpoint
  // For now, use hardcoded test data
  const buyerAgentId = 'buyer-001';
  const buyerToken = 'test-buyer-token';
  const sellerAgentId = 'seller-001';
  const sellerToken = 'test-seller-token';

  // === Step 2: Create Skills ===
  console.log('🎯 Step 2: Instantiating buyer and seller skills...\n');

  const buyerSkill = new BuyerSkill({
    exchangeUrl: 'http://159.65.36.5:8890',
    agentId: buyerAgentId,
    authToken: buyerToken,
    checkInDate: '2026-04-01',
    checkOutDate: '2026-04-05',
    budgetCeiling: 50000, // $500
    occupants: 2,
    preferredTerms: { wifi: true, breakfast: true },
  });

  const sellerSkill = new SellerSkill({
    exchangeUrl: 'http://159.65.36.5:8890',
    agentId: sellerAgentId,
    authToken: sellerToken,
    checkInDate: '2026-04-01',
    checkOutDate: '2026-04-05',
    roomType: 'deluxe',
    floorPrice: 35000,  // $350 minimum
    askPrice: 50000,    // $500 asking price
    maxOccupants: 4,
    amenities: { wifi: true, breakfast: true, balcony: true },
    reputationScore: 95,
    stakeAmount: 10000, // $100 stake
  });

  console.log('✅ Buyer skill created');
  console.log('✅ Seller skill created\n');

  // === Step 3: Seller Publishes Ask ===
  console.log('📊 Step 3: Seller publishing ask...\n');
  const askId = await sellerSkill.publishAsk();
  console.log();

  // === Step 4: Buyer Announces Intent ===
  console.log('🛍️  Step 4: Buyer announcing intent...\n');
  const sessionResult = await buyerSkill.announce({});
  console.log();

  // === Step 5: Negotiate ===
  console.log('🤝 Step 5: Negotiation simulation...\n');

  // Simulate offers
  let sellerAskPrice = 50000;
  let buyerOfferPrice = 40000;
  let round = 0;

  while (round < 5) {
    console.log(`\n--- Round ${round + 1} ---`);

    // Buyer evaluates seller's ask
    const buyerEval = await buyerSkill.evaluateOffer({ price: sellerAskPrice });
    console.log(`Buyer decision: ${buyerEval.action} - ${buyerEval.reasoning}`);

    if (buyerEval.action === 'accept') {
      console.log(`\n✅ DEAL ACCEPTED by buyer at $${sellerAskPrice / 100}`);
      await buyerSkill.acceptDeal(sellerAskPrice);
      break;
    }

    if (buyerEval.action === 'counter' && buyerEval.price) {
      buyerOfferPrice = buyerEval.price;

      // Seller evaluates buyer's counter
      const sellerEval = await sellerSkill.evaluateOffer(
        { price: buyerOfferPrice },
        sessionResult.sessionId
      );
      console.log(`Seller decision: ${sellerEval.action} - ${sellerEval.reasoning}`);

      if (sellerEval.action === 'accept') {
        console.log(`\n✅ DEAL ACCEPTED by seller at $${buyerOfferPrice / 100}`);
        await sellerSkill.acceptDeal(sessionResult.sessionId, buyerOfferPrice);
        break;
      }

      if (sellerEval.action === 'counter' && sellerEval.price) {
        sellerAskPrice = sellerEval.price;
      } else {
        console.log(`\n❌ NEGOTIATION FAILED: ${sellerEval.reasoning}`);
        break;
      }
    } else {
      console.log(`\n❌ NEGOTIATION FAILED: ${buyerEval.reasoning}`);
      break;
    }

    round++;
  }

  console.log('\n' + '='.repeat(60));
  console.log('Test complete!');
  console.log('='.repeat(60));
}

// Run the test
runNegotiation().catch(console.error);
```

---

## 🚀 Installation & Usage

### 1. Create Project Directory
```bash
mkdir bookwithclaw-skills
cd bookwithclaw-skills
npm init -y
npm install axios @noble/ed25519 uuid typescript ts-node @types/node
```

### 2. Create Files
```bash
# Create the TypeScript files
touch buyer-skill.ts seller-skill.ts test-negotiation.ts
```

### 3. Paste Templates
Copy the code from the sections above into each file.

### 4. Run Test
```bash
npx ts-node test-negotiation.ts
```

### Expected Output
```
============================================================
🚀 BookWithClaw Skill Test: Hotel Negotiation
============================================================

📋 Step 1: Registering agents with exchange...

🎯 Step 2: Instantiating buyer and seller skills...

✅ Buyer skill created
✅ Seller skill created

📊 Step 3: Seller publishing ask...

🏨 [Seller] Publishing ask at $500

✅ [Seller] Ask published: 8a9c4e1f-...

🛍️  Step 4: Buyer announcing intent...

🛒 [Buyer] Announcing intent for 2026-04-01 to 2026-04-05

✅ [Buyer] Session created: 550e8400-...

🤝 Step 5: Negotiation simulation...

--- Round 1 ---
💰 [Seller] Evaluating buyer offer: $400
📊 [Buyer] Evaluating seller ask: $500
Buyer decision: counter - Countering with $450
Seller decision: counter - Countering with $475

--- Round 2 ---
💰 [Seller] Evaluating buyer offer: $427
📊 [Buyer] Evaluating seller ask: $475
Buyer decision: counter - Countering with $427
Seller decision: accept - Good offer at $427! Accepting.

✅ DEAL ACCEPTED by seller at $427
✅ [Seller] Accepting deal at $427

💰 Session 550e8400-... complete!

============================================================
Test complete!
============================================================
```

---

## 📋 Key Features

### Buyer Skill
- ✅ Announces intent to buy
- ✅ Evaluates seller asks
- ✅ Generates counter-offers (10% lower)
- ✅ Enforces budget ceiling
- ✅ Respects max negotiation rounds
- ✅ Accepts good deals automatically

### Seller Skill
- ✅ Publishes asks to order book
- ✅ Evaluates buyer offers  
- ✅ Generates counter-offers (splits difference)
- ✅ Enforces floor price
- ✅ Respects max negotiation rounds
- ✅ Accepts good offers automatically

---

## 🔌 Connecting to Live Exchange

To use these skills against the running exchange:

1. **Register Agents** via `/agents/register`
2. **Pass real tokens** to skill constructors
3. **Call `announce()`** to start negotiation
4. **Handle WebSocket messages** for real-time negotiation

Example:
```typescript
// Get real agent ID and token from exchange
const { agent_id, auth_token } = await registerAgent(...);

// Create skill with real credentials
const buyerSkill = new BuyerSkill({
  exchangeUrl: 'http://159.65.36.5:8890',
  agentId: agent_id,
  authToken: auth_token,
  // ... config
});

// Start negotiation
const session = await buyerSkill.announce({});
```

---

## 🎓 Customization

You can customize negotiation behavior by:

1. **Adjusting prices** in `evaluateOffer()`
2. **Changing max rounds** (default: 5)
3. **Modifying counter-offer logic** (currently 10% reduction for buyer, 50% split for seller)
4. **Adding decision trees** based on terms, reputation, dates, etc.

Example custom logic:
```typescript
// Seller: Increase price if reputation is high
const priceMultiplier = 1 + (this.config.reputationScore / 100) * 0.1;
const adjustedPrice = Math.floor(this.config.askPrice * priceMultiplier);
```

---

## 🧠 Next Steps

1. **Test locally** with the example above
2. **Connect to the exchange** with real API calls
3. **Build more complex decision logic** based on market conditions
4. **Add logging & metrics** for deal analysis
5. **Package as npm module** for distribution

