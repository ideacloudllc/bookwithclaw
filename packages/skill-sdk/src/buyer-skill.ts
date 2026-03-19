/**
 * Reference buyer skill for BookWithClaw.
 */

import { v4 as uuidv4 } from "uuid";

import { canonicalJSON, signMessage } from "./crypto";
import {
  BuyerCounterOffer,
  BuyerIntent,
  DealAccepted,
  Message,
  SettlementComplete,
} from "./messages";
import { ExchangeConnection } from "./websocket";

export interface BuyerSkillConfig {
  exchangeUrl: string;
  agentId: string;
  authToken: string;
  publicKey: string;
  privateKey: string;
  maxRounds?: number;
}

export interface HotelBuyerConfig {
  checkInDate: string; // YYYY-MM-DD
  checkOutDate: string; // YYYY-MM-DD
  budgetCeiling: number; // cents
  occupants: number;
  acceptableRoomTypes?: string[];
  preferredTerms?: Record<string, any>;
}

export interface SkillResult {
  success: boolean;
  agreedPrice?: number;
  bookingRef?: string;
  error?: string;
}

/**
 * Reference implementation of a hotel room buyer skill.
 */
export class BuyerSkill {
  private config: BuyerSkillConfig;
  private connection: ExchangeConnection | null = null;
  private currentRound = 0;
  private maxRounds: number;

  constructor(config: BuyerSkillConfig) {
    this.config = {
      ...config,
    };
    this.maxRounds = config.maxRounds || 10;
  }

  /**
   * Announce availability and seek matches (entry point)
   */
  async announce(hotelConfig: HotelBuyerConfig): Promise<SkillResult> {
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
      this.setupListeners();

      // Create and publish intent
      const intent = await this.createIntent(hotelConfig, sessionId);
      await this.sendMessage(intent);

      // Wait for settlement or timeout
      const result = await this.waitForSettlement(60000); // 60s timeout
      return result;
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    } finally {
      if (this.connection) {
        this.connection.close();
      }
    }
  }

  // Private helpers

  private async createIntent(
    config: HotelBuyerConfig,
    sessionId: string
  ): Promise<BuyerIntent> {
    const now = new Date().toISOString();
    const intentId = uuidv4();

    const payload = {
      intent_id: intentId,
      vertical: "hotels",
      buyer_agent_id: this.config.agentId,
      budget_ceiling: config.budgetCeiling,
      max_negotiation_rounds: this.maxRounds,
      preferred_terms: config.preferredTerms || {},
      vertical_fields: {
        checkin_date: config.checkInDate,
        checkout_date: config.checkOutDate,
        occupants: config.occupants,
        acceptable_room_types: config.acceptableRoomTypes || [],
      },
    };

    const payloadJson = canonicalJSON(payload);
    const signature = await signMessage(
      Buffer.from(payloadJson),
      this.config.privateKey
    );

    return {
      type: "BuyerIntent",
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

  private setupListeners(): void {
    if (!this.connection) return;

    this.connection.on("message", async (message: Message) => {
      if (message.type === "SellerAsk") {
        // Seller has replied with an ask
        await this.evaluateAsk(message as any);
      } else if (message.type === "SettlementComplete") {
        // Deal completed!
        this.emit("settlement_complete", message);
      } else if (message.type === "SettlementFailed") {
        // Deal failed
        this.emit("settlement_failed", message);
      }
    });
  }

  private async evaluateAsk(ask: any): Promise<void> {
    // Simple evaluation: if price is acceptable, accept
    // In real implementation, would do more sophisticated logic

    const sessionId = ask.payload.session_id;
    const askPrice = ask.payload.price;

    if (askPrice <= this.config.maxRounds * 100) {
      // Accept if price is reasonable
      const acceptMsg: DealAccepted = {
        type: "DealAccepted",
        round_num: this.currentRound + 1,
        timestamp: new Date().toISOString(),
        signature: "",
        payload: {
          session_id: sessionId,
          agent_id: this.config.agentId,
          agreed_price: askPrice,
        },
      };

      // Sign before sending
      const payload = canonicalJSON(acceptMsg.payload);
      acceptMsg.signature = await signMessage(
        Buffer.from(payload),
        this.config.privateKey
      );

      await this.sendMessage(acceptMsg);
    }
  }

  private async waitForSettlement(timeoutMs: number): Promise<SkillResult> {
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        resolve({
          success: false,
          error: "Settlement timeout",
        });
      }, timeoutMs);

      const checkSettlement = (message: any) => {
        if (message.type === "SettlementComplete") {
          clearTimeout(timeout);
          this.connection?.removeListener("message", checkSettlement);
          resolve({
            success: true,
            agreedPrice: message.payload.agreed_price,
            bookingRef: message.payload.booking_ref,
          });
        }
      };

      if (this.connection) {
        this.connection.on("message", checkSettlement);
      }
    });
  }

  private emit(event: string, data?: any): void {
    // Simple event emission for skill lifecycle
    console.log(`[BuyerSkill] ${event}:`, data);
  }
}
