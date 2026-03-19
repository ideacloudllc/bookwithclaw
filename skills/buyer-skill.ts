import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

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
    console.log(`📊 [Buyer] Evaluating seller ask: $${(ask.price / 100).toFixed(2)}`);

    // Reject if exceeds budget ceiling
    if (ask.price > this.config.budgetCeiling) {
      return {
        action: 'reject',
        reasoning: `Price $${(ask.price / 100).toFixed(2)} exceeds budget ceiling $${(this.config.budgetCeiling / 100).toFixed(2)}`,
      };
    }

    // Accept if below 70% of budget
    if (ask.price <= this.config.budgetCeiling * 0.7) {
      return {
        action: 'accept',
        reasoning: `Great deal at $${(ask.price / 100).toFixed(2)}! Accepting.`,
      };
    }

    // Counter if between 70-100% of budget
    if (this.counterOfferCount < this.maxRounds) {
      const counterPrice = Math.floor(ask.price * 0.9); // Offer 10% less
      this.counterOfferCount++;
      return {
        action: 'counter',
        price: counterPrice,
        reasoning: `Countering with $${(counterPrice / 100).toFixed(2)}`,
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
   * Accept a deal
   */
  async acceptDeal(finalPrice: number): Promise<void> {
    if (!this.currentSessionId) {
      throw new Error('No active session');
    }

    console.log(`✅ [Buyer] Accepting deal at $${(finalPrice / 100).toFixed(2)}`);
    console.log(`💰 Session ${this.currentSessionId} complete!`);
  }

  getSessionId(): string | null {
    return this.currentSessionId;
  }
}

export default BuyerSkill;
