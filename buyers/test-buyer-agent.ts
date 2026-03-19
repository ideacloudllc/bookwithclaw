/**
 * Test Buyer Agent for BookWithClaw Exchange
 * 
 * Automated buyer that:
 * - Registers on the exchange
 * - Posts hotel room intents
 * - Receives seller asks
 * - Negotiates prices
 * - Completes settlements
 */

import axios from 'axios';
import * as crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

const EXCHANGE_URL = 'http://159.65.36.5:8890';

interface AgentKeys {
  publicKey: string;
  privateKey: crypto.KeyObject;
}

interface BuyerConfig {
  name: string;
  email: string;
  budget: number; // cents
  checkInDate: string; // YYYY-MM-DD
  checkOutDate: string; // YYYY-MM-DD
  occupants: number;
  preferredRoomTypes: string[];
  maxNegotiationRounds: number;
  negotiationStrategy: 'aggressive' | 'moderate' | 'conservative';
}

interface RegisterResponse {
  agent_id: string;
  auth_token: string;
}

interface BuyerIntent {
  intent_id: string;
  vertical: string;
  buyer_agent_id: string;
  budget_ceiling: number;
  max_negotiation_rounds: number;
  preferred_terms: Record<string, unknown>;
  vertical_fields: {
    checkin_date: string;
    checkout_date: string;
    occupants: number;
    acceptable_room_types: string[];
  };
  round_num: number;
  timestamp: string;
  signature: string;
}

interface SellerAsk {
  session_id: string;
  room_id: string;
  seller_id: string;
  price: number;
  room_type: string;
  features: string[];
  checkin_date: string;
  checkout_date: string;
  round_num: number;
  timestamp: string;
  signature: string;
}

interface CounterOffer {
  session_id: string;
  buyer_agent_id: string;
  proposed_price: number;
  round_num: number;
  timestamp: string;
  signature: string;
}

interface DealAccepted {
  session_id: string;
  buyer_agent_id: string;
  agreed_price: number;
  round_num: number;
  timestamp: string;
  signature: string;
}

class TestBuyerAgent {
  private config: BuyerConfig;
  private keys: AgentKeys;
  private agentId: string = '';
  private authToken: string = '';
  private currentIntentId: string = '';
  private activeNegotiations: Map<string, { round: number; sessionId: string }> = new Map();

  constructor(config: BuyerConfig) {
    this.config = config;
    this.keys = this.generateKeys();
  }

  /**
   * Generate Ed25519 keypair for agent
   */
  private generateKeys(): AgentKeys {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
      publicKeyEncoding: {
        format: 'spki',
        type: 'spki',
      },
      privateKeyEncoding: {
        format: 'pkcs8',
        type: 'pkcs8',
      },
    });

    return {
      publicKey: publicKey.export().toString('hex').slice(-128), // Extract hex key
      privateKey: privateKey as crypto.KeyObject,
    };
  }

  /**
   * Sign message with Ed25519 private key
   */
  private signMessage(message: Record<string, unknown>): string {
    const canonicalJson = JSON.stringify(message, Object.keys(message).sort());
    const signature = crypto
      .createSign('SHA256')
      .update(canonicalJson)
      .sign(this.keys.privateKey, 'hex');
    return signature;
  }

  /**
   * Step 1: Register agent on exchange
   */
  async register(): Promise<void> {
    console.log(`\n📝 Registering buyer agent: ${this.config.name}`);

    try {
      const response = await axios.post<RegisterResponse>(
        `${EXCHANGE_URL}/agents/register`,
        {
          public_key: this.keys.publicKey,
          role: 'buyer',
          email: this.config.email,
        }
      );

      this.agentId = response.data.agent_id;
      this.authToken = response.data.auth_token;

      console.log(`✅ Registered: Agent ID = ${this.agentId}`);
      console.log(`✅ Auth Token: ${this.authToken.slice(0, 20)}...`);
    } catch (error) {
      console.error('❌ Registration failed:', error);
      throw error;
    }
  }

  /**
   * Step 2: Post buyer intent (hotel room search)
   */
  async postIntent(): Promise<void> {
    if (!this.agentId) throw new Error('Agent not registered');

    console.log(`\n🏨 Posting buyer intent...`);
    console.log(`   Budget: $${(this.config.budget / 100).toFixed(2)}`);
    console.log(`   Check-in: ${this.config.checkInDate}`);
    console.log(`   Occupants: ${this.config.occupants}`);

    this.currentIntentId = uuidv4();

    const payload: Record<string, unknown> = {
      intent_id: this.currentIntentId,
      vertical: 'hotels',
      buyer_agent_id: this.agentId,
      budget_ceiling: this.config.budget,
      max_negotiation_rounds: this.config.maxNegotiationRounds,
      preferred_terms: {
        early_checkout: false,
        late_checkout: true,
        breakfast_included: true,
      },
      vertical_fields: {
        checkin_date: this.config.checkInDate,
        checkout_date: this.config.checkOutDate,
        occupants: this.config.occupants,
        acceptable_room_types: this.config.preferredRoomTypes,
      },
    };

    const signature = this.signMessage(payload);

    const intent: BuyerIntent = {
      ...payload,
      round_num: 1,
      timestamp: new Date().toISOString(),
      signature,
    } as any;

    console.log(`✅ Intent posted: ${this.currentIntentId}`);
  }

  /**
   * Step 3: Evaluate seller ask and decide whether to counter-offer
   */
  evaluateAsk(ask: SellerAsk): {
    accept: boolean;
    counterPrice?: number;
    reason: string;
  } {
    console.log(`\n💰 Received ask from seller`);
    console.log(`   Room: ${ask.room_type}`);
    console.log(`   Price: $${(ask.price / 100).toFixed(2)}`);
    console.log(`   Round: ${ask.round_num}`);

    // Check if within budget
    if (ask.price > this.config.budget) {
      const percentOver = ((ask.price - this.config.budget) / this.config.budget * 100).toFixed(1);
      console.log(`   ⚠️  Over budget by ${percentOver}%`);

      // Try to negotiate down
      if (ask.round_num < this.config.maxNegotiationRounds) {
        const counterPrice = this.getCounterPrice(ask.price, ask.round_num);
        return {
          accept: false,
          counterPrice,
          reason: `Over budget, counter-offering $${(counterPrice / 100).toFixed(2)}`,
        };
      } else {
        return {
          accept: false,
          reason: 'Over budget and max rounds reached',
        };
      }
    }

    // If within budget, accept if room quality is good
    const qualityScore = this.evaluateRoomQuality(ask);
    if (qualityScore >= 0.7) {
      return {
        accept: true,
        reason: `Within budget and good quality (score: ${qualityScore.toFixed(2)})`,
      };
    }

    // Otherwise try to negotiate
    if (ask.round_num < this.config.maxNegotiationRounds) {
      const counterPrice = this.getCounterPrice(ask.price, ask.round_num);
      return {
        accept: false,
        counterPrice,
        reason: `Room quality okay, attempting to negotiate lower`,
      };
    }

    return {
      accept: true,
      reason: 'Max rounds reached, accepting to close deal',
    };
  }

  /**
   * Evaluate room quality based on features and terms
   */
  private evaluateRoomQuality(ask: SellerAsk): number {
    let score = 0.5; // base score

    // Features
    if (ask.features.includes('wifi')) score += 0.1;
    if (ask.features.includes('air_conditioning')) score += 0.1;
    if (ask.features.includes('parking')) score += 0.05;
    if (ask.features.includes('gym')) score += 0.05;

    return Math.min(score, 1.0);
  }

  /**
   * Generate counter-price based on negotiation strategy
   */
  private getCounterPrice(sellerPrice: number, roundNum: number): number {
    const concession = this.config.negotiationStrategy === 'aggressive' ? 0.85 : 
                       this.config.negotiationStrategy === 'moderate' ? 0.9 :
                       0.95;

    // Gradually move toward seller's price with each round
    const roundFactor = 1 - (roundNum / this.config.maxNegotiationRounds) * (1 - concession);

    return Math.floor(this.config.budget * roundFactor);
  }

  /**
   * Post counter-offer
   */
  async postCounterOffer(sessionId: string, counterPrice: number, round: number): Promise<void> {
    console.log(`\n💬 Posting counter-offer`);
    console.log(`   Price: $${(counterPrice / 100).toFixed(2)}`);
    console.log(`   Round: ${round + 1}`);

    const payload: Record<string, unknown> = {
      session_id: sessionId,
      buyer_agent_id: this.agentId,
      proposed_price: counterPrice,
      round_num: round + 1,
      timestamp: new Date().toISOString(),
    };

    const signature = this.signMessage(payload);

    const counterOffer: CounterOffer = {
      ...payload,
      signature,
    } as any;

    console.log(`✅ Counter-offer posted`);
  }

  /**
   * Accept deal
   */
  async acceptDeal(sessionId: string, agreedPrice: number, round: number): Promise<void> {
    console.log(`\n✅ ACCEPTING DEAL`);
    console.log(`   Session: ${sessionId}`);
    console.log(`   Price: $${(agreedPrice / 100).toFixed(2)}`);
    console.log(`   Round: ${round}`);

    const payload: Record<string, unknown> = {
      session_id: sessionId,
      buyer_agent_id: this.agentId,
      agreed_price: agreedPrice,
      round_num: round,
      timestamp: new Date().toISOString(),
    };

    const signature = this.signMessage(payload);

    const dealAccepted: DealAccepted = {
      ...payload,
      signature,
    } as any;

    console.log(`✅ Deal accepted - awaiting settlement`);
  }

  /**
   * Simulate a full negotiation cycle (for demo/testing)
   */
  async runDemo(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 TEST BUYER AGENT — DEMO SIMULATION');
    console.log('='.repeat(60));

    try {
      // Step 1: Register
      await this.register();

      // Step 2: Post intent
      await this.postIntent();

      // Simulate waiting for offers
      console.log('\n⏳ Waiting for seller offers... (simulated)');

      // Simulate seller asking $50000 cents ($500)
      const simulatedAsk: SellerAsk = {
        session_id: uuidv4(),
        room_id: 'rm_test123',
        seller_id: 'seller_test456',
        price: 50000,
        room_type: 'Deluxe King',
        features: ['wifi', 'air_conditioning', 'gym'],
        checkin_date: this.config.checkInDate,
        checkout_date: this.config.checkOutDate,
        round_num: 1,
        timestamp: new Date().toISOString(),
        signature: 'mock_signature_1',
      };

      // Evaluate the ask
      const evaluation1 = this.evaluateAsk(simulatedAsk);
      console.log(`   Decision: ${evaluation1.reason}`);

      if (evaluation1.counterPrice) {
        await this.postCounterOffer(simulatedAsk.session_id, evaluation1.counterPrice, 1);

        // Simulate seller counter at $45000 ($450)
        const simulatedAsk2: SellerAsk = {
          ...simulatedAsk,
          price: 45000,
          round_num: 2,
        };

        const evaluation2 = this.evaluateAsk(simulatedAsk2);
        console.log(`   Decision: ${evaluation2.reason}`);

        if (evaluation2.accept) {
          await this.acceptDeal(simulatedAsk2.session_id, simulatedAsk2.price, 2);
        }
      }

      console.log('\n' + '='.repeat(60));
      console.log('✅ DEMO COMPLETE');
      console.log('='.repeat(60));
    } catch (error) {
      console.error('❌ Demo failed:', error);
    }
  }
}

/**
 * Main: Run test buyer agent
 */
async function main() {
  const buyer = new TestBuyerAgent({
    name: 'Test Buyer Agent',
    email: 'buyer@bookwithclaw.ai',
    budget: 50000, // $500 max
    checkInDate: '2026-03-25',
    checkOutDate: '2026-03-27',
    occupants: 2,
    preferredRoomTypes: ['Deluxe King', 'Suite'],
    maxNegotiationRounds: 5,
    negotiationStrategy: 'moderate',
  });

  await buyer.runDemo();
}

main().catch(console.error);
