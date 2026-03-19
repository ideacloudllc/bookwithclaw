import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

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
    console.log(`🏨 [Seller] Publishing ask at $${(this.config.askPrice / 100).toFixed(2)}`);

    try {
      // In a real implementation, this would post to /order-book/ask
      // For now, we're demonstrating the structure
      const askId = uuidv4();
      
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
    console.log(`💰 [Seller] Evaluating buyer offer: $${(offer.price / 100).toFixed(2)}`);

    // Reject if below floor price
    if (offer.price < this.config.floorPrice) {
      return {
        action: 'reject',
        reasoning: `Offer $${(offer.price / 100).toFixed(2)} is below floor price $${(this.config.floorPrice / 100).toFixed(2)}`,
      };
    }

    // Accept if at or above 90% of asking price
    if (offer.price >= this.config.askPrice * 0.9) {
      return {
        action: 'accept',
        reasoning: `Good offer at $${(offer.price / 100).toFixed(2)}! Accepting.`,
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
        reasoning: `Countering with $${(counterPrice / 100).toFixed(2)}`,
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
    console.log(`✅ [Seller] Accepting deal at $${(finalPrice / 100).toFixed(2)}`);
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

  getActiveAsks(): string[] {
    return Array.from(this.activeAsks.keys());
  }
}

export default SellerSkill;
