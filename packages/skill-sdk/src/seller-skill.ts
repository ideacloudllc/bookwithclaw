/**
 * Reference seller skill for BookWithClaw.
 */

import { v4 as uuidv4 } from "uuid";

import { canonicalJSON, signMessage } from "./crypto";
import {
  BuyerCounterOffer,
  DealAccepted,
  Message,
  SellerAsk,
  SellerCounterOffer,
  SettlementComplete,
} from "./messages";
import { ExchangeConnection } from "./websocket";

export interface SellerSkillConfig {
  exchangeUrl: string;
  agentId: string;
  authToken: string;
  publicKey: string;
  privateKey: string;
  maxRounds?: number;
}

export interface HotelSellerConfig {
  checkInDate: string; // YYYY-MM-DD
  checkOutDate: string; // YYYY-MM-DD
  roomType: string;
  maxOccupants: number;
  floorPrice: number; // cents
  askPrice: number; // cents
  terms?: Record<string, any>;
  reputationScore?: number; // 0-100
  stakeAmount?: number; // cents
}

/**
 * Reference implementation of a hotel room seller skill.
 */
export class SellerSkill {
  private config: SellerSkillConfig;
  private connection: ExchangeConnection | null = null;
  private maxRounds: number;
  private activeDeals = new Map<string, any>();

  constructor(config: SellerSkillConfig) {
    this.config = {
      ...config,
    };
    this.maxRounds = config.maxRounds || 10;
  }

  /**
   * Start listening for buyer intents and respond with asks
   */
  async listen(hotelConfig: HotelSellerConfig): Promise<void> {
    try {
      const sessionId = uuidv4();

      // Connect to exchange
      this.connection = new ExchangeConnection({
        exchangeUrl: this.config.exchangeUrl,
        sessionId,
        authToken: this.config.authToken,
      });

      await this.connection.connect();

      // Set up message listeners
      this.setupListeners(hotelConfig);

      console.log("[SellerSkill] Listening for buyer intents...");

      // Keep connection alive
      await new Promise(() => {
        // Never resolves - listener runs indefinitely
      });
    } catch (error: any) {
      console.error("[SellerSkill] Error:", error.message);
    } finally {
      if (this.connection) {
        this.connection.close();
      }
    }
  }

  // Private helpers

  private setupListeners(hotelConfig: HotelSellerConfig): void {
    if (!this.connection) return;

    this.connection.on("message", async (message: Message) => {
      if (message.type === "BuyerIntent") {
        // New buyer seeking a room
        await this.handleBuyerIntent(message as any, hotelConfig);
      } else if (message.type === "BuyerCounterOffer") {
        // Buyer made a counter-offer
        await this.handleBuyerCounter(message as any, hotelConfig);
      } else if (message.type === "DealAccepted") {
        // Deal accepted!
        this.handleDealAccepted(message as any);
      } else if (message.type === "SettlementComplete") {
        // Settlement complete
        console.log(
          "[SellerSkill] Settlement complete:",
          (message as any).payload.booking_ref
        );
      }
    });
  }

  private async handleBuyerIntent(
    intent: any,
    hotelConfig: HotelSellerConfig
  ): Promise<void> {
    const sessionId = intent.payload.intent_id;
    const buyerPrice = intent.payload.budget_ceiling;

    // Check if this is a compatible request
    if (buyerPrice < hotelConfig.floorPrice) {
      // Too low, don't respond
      console.log("[SellerSkill] Ignoring low bid:", buyerPrice);
      return;
    }

    // Create ask response
    const ask = await this.createAsk(sessionId, hotelConfig);
    await this.sendMessage(ask);

    // Track this deal
    this.activeDeals.set(sessionId, {
      buyerId: intent.payload.buyer_agent_id,
      currentPrice: hotelConfig.askPrice,
      round: 1,
    });
  }

  private async handleBuyerCounter(
    counter: any,
    hotelConfig: HotelSellerConfig
  ): Promise<void> {
    const sessionId = counter.payload.session_id;
    const buyerPrice = counter.payload.counter_price;
    const deal = this.activeDeals.get(sessionId);

    if (!deal) return;

    // Simple strategy: move price down towards floor if buyer is reasonable
    if (buyerPrice >= hotelConfig.floorPrice) {
      // Accept the buyer's offer
      const acceptMsg: DealAccepted = {
        type: "DealAccepted",
        round_num: counter.round_num + 1,
        timestamp: new Date().toISOString(),
        signature: "",
        payload: {
          session_id: sessionId,
          agent_id: this.config.agentId,
          agreed_price: buyerPrice,
        },
      };

      // Sign before sending
      const payload = canonicalJSON(acceptMsg.payload);
      acceptMsg.signature = await signMessage(
        Buffer.from(payload),
        this.config.privateKey
      );

      await this.sendMessage(acceptMsg);
      console.log(`[SellerSkill] Accepted offer at ${buyerPrice}`);
    } else {
      // Counter-offer: move slightly down
      const newPrice = deal.currentPrice - 500; // Move down by $5

      const counterMsg: SellerCounterOffer = {
        type: "SellerCounterOffer",
        round_num: counter.round_num + 1,
        timestamp: new Date().toISOString(),
        signature: "",
        payload: {
          session_id: sessionId,
          seller_agent_id: this.config.agentId,
          round_num: counter.round_num + 1,
          counter_price: Math.max(newPrice, hotelConfig.floorPrice),
          terms: hotelConfig.terms || {},
        },
      };

      // Sign before sending
      const payload = canonicalJSON(counterMsg.payload);
      counterMsg.signature = await signMessage(
        Buffer.from(payload),
        this.config.privateKey
      );

      await this.sendMessage(counterMsg);
      deal.currentPrice = newPrice;
      deal.round = counter.round_num + 1;
    }
  }

  private handleDealAccepted(message: any): void {
    const sessionId = message.payload.session_id;
    const agreedPrice = message.payload.agreed_price;

    console.log(
      `[SellerSkill] Deal accepted for session ${sessionId} at $${(agreedPrice / 100).toFixed(2)}`
    );

    this.activeDeals.delete(sessionId);
  }

  private async createAsk(
    sessionId: string,
    config: HotelSellerConfig
  ): Promise<SellerAsk> {
    const now = new Date().toISOString();
    const askId = uuidv4();

    const payload = {
      ask_id: askId,
      vertical: "hotels",
      seller_agent_id: this.config.agentId,
      session_id: sessionId,
      price: config.askPrice,
      floor_price: config.floorPrice,
      terms: config.terms || {},
      seller_reputation_score: config.reputationScore || 75,
      stake_amount: config.stakeAmount || 0,
      vertical_fields: {
        checkin_date: config.checkInDate,
        checkout_date: config.checkOutDate,
        room_type: config.roomType,
        max_occupants: config.maxOccupants,
      },
    };

    const payloadJson = canonicalJSON(payload);
    const signature = await signMessage(
      Buffer.from(payloadJson),
      this.config.privateKey
    );

    return {
      type: "SellerAsk",
      round_num: 1,
      timestamp: now,
      signature,
      payload,
    };
  }

  private async sendMessage(message: Message): Promise<void> {
    if (!this.connection) {
      throw new Error("Not connected to exchange");
    }
    await this.connection.sendMessage(message);
  }
}
