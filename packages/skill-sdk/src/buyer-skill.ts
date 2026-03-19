/**
 * Hotel Room Buyer Skill - Reference implementation.
 * 
 * BuyerSkill is an AI agent that:
 * 1. Announces an intent to buy a hotel room
 * 2. Receives asks from sellers
 * 3. Evaluates asks and generates counter-offers
 * 4. Enforces budget ceiling constraint
 * 5. Accepts final offer when satisfied
 */

import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import { ExchangeConnection } from './websocket';
import {
  BuyerIntentMessage,
  SellerAskMessage,
  SellerCounterOfferMessage,
  DealAcceptedMessage,
  SettlementCompleteMessage,
  Message,
  BuyerCounterOfferMessageSchema,
  DealAcceptedMessageSchema,
  SessionWalkawayMessageSchema,
} from './messages';
import { signMessage } from './crypto';

export interface HotelBuyerConfig {
  agentId: string;
  publicKey: string;
  privateKey: string;
  checkInDate: string; // ISO date
  checkOutDate: string; // ISO date
  budgetCeilingCents: number; // Max cents per night
  occupants: number;
  acceptableRoomTypes: string[]; // ["deluxe_king", "standard_queen"]
  minAcceptablePrice?: number; // Auto-reject below this (cents)
}

export interface BuyerSkillOptions {
  exchangeUrl: string;
  authToken: string;
  config: HotelBuyerConfig;
}

export interface SessionResult {
  success: boolean;
  sessionId?: string;
  finalPrice?: number;
  error?: string;
}

/**
 * Buyer agent for hotel room negotiation.
 */
export class BuyerSkill extends EventEmitter {
  private connection: ExchangeConnection | null = null;
  private config: HotelBuyerConfig;
  private authToken: string;
  private sessionId: string | null = null;
  private currentRound = 0;
  private bestOfferCents: number | null = null;
  private bestOfferFromSeller = '';

  constructor(options: BuyerSkillOptions) {
    super();
    this.config = options.config;
    this.authToken = options.authToken;

    // Initialize WebSocket connection
    this.connection = new ExchangeConnection({
      exchangeUrl: options.exchangeUrl,
      sessionId: 'temp-session-id', // Will be set after announcing intent
      authToken: options.authToken,
    });

    // Set up message handlers
    this.connection.on('message', (msg) => this.handleMessage(msg));
    this.connection.on('error', (error) => this.emit('error', error));
    this.connection.on('disconnected', () => {
      this.emit('disconnected');
      // Auto-reconnect if not explicitly disconnected
      if (this.sessionId) {
        this.connection!.connect().catch((e) => this.emit('error', e));
      }
    });
  }

  /**
   * Main entry point: Announce intent to buy and start negotiation.
   * 
   * @returns Promise with session result (success, sessionId, finalPrice, or error)
   */
  public async announce(intent: Partial<BuyerIntentMessage> = {}): Promise<SessionResult> {
    try {
      // Generate session ID
      this.sessionId = `session_${uuidv4()}`;

      // Create intent message
      const now = Math.floor(Date.now() / 1000);
      const intentMessage: BuyerIntentMessage = {
        type: 'buyer_intent',
        vertical: 'hotels',
        timestamp: now,
        signature: '', // Will be signed below
        sender_id: this.config.agentId,
        session_id: this.sessionId,
        round_number: this.currentRound++,

        // Hotel-specific fields
        check_in_date: this.config.checkInDate,
        check_out_date: this.config.checkOutDate,
        budget_ceiling_cents: this.config.budgetCeilingCents,
        occupants: this.config.occupants,
        room_types: this.config.acceptableRoomTypes,
        preferred_terms: intent.preferred_terms,
      };

      // Sign message
      const messageBytes = Buffer.from(JSON.stringify(intentMessage, null, 2));
      intentMessage.signature = await signMessage(messageBytes, this.config.privateKey);

      // Connect to exchange
      this.connection!.url = `${this.connection!.url.split('/ws/')[0]}/ws/session/${this.sessionId}`;
      await this.connection!.connect();

      // Send intent
      await this.connection!.send(intentMessage);
      this.emit('intent_announced', { sessionId: this.sessionId });

      // Wait for deal to be made (max 120 seconds)
      return await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          resolve({
            success: false,
            sessionId: this.sessionId!,
            error: 'Negotiation timeout',
          });
        }, 120000);

        this.once('deal_accepted', (result) => {
          clearTimeout(timeout);
          resolve(result);
        });

        this.once('session_failed', (error) => {
          clearTimeout(timeout);
          resolve({
            success: false,
            sessionId: this.sessionId!,
            error,
          });
        });
      });
    } catch (error) {
      return {
        success: false,
        error: `Failed to announce intent: ${error}`,
      };
    }
  }

  /**
   * Disconnect from the exchange.
   */
  public disconnect(): void {
    if (this.connection) {
      this.connection.disconnect();
    }
  }

  /**
   * Handle incoming messages from the exchange.
   */
  private async handleMessage(msg: Message): Promise<void> {
    try {
      switch (msg.type) {
        case 'seller_ask':
          await this.handleSellerAsk(msg as SellerAskMessage);
          break;

        case 'seller_counter_offer':
          await this.handleSellerCounter(msg as SellerCounterOfferMessage);
          break;

        case 'settlement_complete':
          this.handleSettlementComplete(msg as SettlementCompleteMessage);
          break;

        case 'session_walkaway':
          this.emit('session_failed', 'Seller walked away');
          break;

        default:
          // Ignore other message types
          break;
      }
    } catch (error) {
      this.emit('error', error);
    }
  }

  /**
   * Handle seller ask - evaluate and decide whether to counter or accept.
   */
  private async handleSellerAsk(ask: SellerAskMessage): Promise<void> {
    // Check if ask is within budget
    if (ask.floor_price_cents > this.config.budgetCeilingCents) {
      // Too expensive, walk away
      await this.sendWalkaway('Price exceeds budget');
      this.emit('session_failed', 'Seller price exceeds budget');
      return;
    }

    // Store best offer
    this.bestOfferCents = ask.floor_price_cents;
    this.bestOfferFromSeller = ask.sender_id;

    // If floor price is near our budget, accept it
    // Otherwise, counter with a price between floor and our budget
    const counterPrice = Math.min(
      Math.floor((ask.floor_price_cents + this.config.budgetCeilingCents) / 2),
      this.config.budgetCeilingCents
    );

    if (counterPrice === this.bestOfferCents) {
      // Same price, accept the deal
      await this.acceptDeal(ask);
    } else {
      // Send counter-offer
      await this.sendCounterOffer(counterPrice);
    }
  }

  /**
   * Handle seller counter-offer.
   */
  private async handleSellerCounter(counter: SellerCounterOfferMessage): Promise<void> {
    // Update best offer
    this.bestOfferCents = counter.counter_price_cents;

    // If price is within budget, decide to accept or counter again
    if (counter.counter_price_cents <= this.config.budgetCeilingCents) {
      // Accept the deal (max 3 rounds)
      if (this.currentRound >= 3) {
        await this.sendDealAccepted(counter.counter_price_cents);
      } else {
        // Counter one more time
        const newOffer = counter.counter_price_cents - 500; // Reduce by $5
        if (newOffer >= this.config.budgetCeilingCents * 0.9) {
          await this.sendCounterOffer(newOffer);
        } else {
          // Accept current offer
          await this.sendDealAccepted(counter.counter_price_cents);
        }
      }
    } else {
      // Over budget, walk away
      await this.sendWalkaway('Counter-offer exceeds budget');
      this.emit('session_failed', 'Counter-offer exceeds budget');
    }
  }

  /**
   * Handle settlement complete message.
   */
  private handleSettlementComplete(msg: SettlementCompleteMessage): void {
    this.emit('deal_accepted', {
      success: true,
      sessionId: this.sessionId!,
      finalPrice: msg.final_price_cents,
    });
  }

  /**
   * Accept an ask and send deal_accepted message.
   */
  private async acceptDeal(ask: SellerAskMessage): Promise<void> {
    await this.sendDealAccepted(ask.floor_price_cents);
  }

  /**
   * Send deal_accepted message.
   */
  private async sendDealAccepted(priceCents: number): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: DealAcceptedMessage = {
      type: 'deal_accepted',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: this.sessionId!,
      round_number: this.currentRound++,

      agreed_price_cents: priceCents,
      check_in_date: this.config.checkInDate,
      check_out_date: this.config.checkOutDate,
    };

    const messageBytes = Buffer.from(JSON.stringify(msg, null, 2));
    msg.signature = await signMessage(messageBytes, this.config.privateKey);

    await this.connection!.send(msg);
    this.emit('deal_accepted', {
      success: true,
      sessionId: this.sessionId!,
      finalPrice: priceCents,
    });
  }

  /**
   * Send counter-offer message.
   */
  private async sendCounterOffer(priceCents: number): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: any = {
      type: 'buyer_counter_offer',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: this.sessionId!,
      round_number: this.currentRound++,

      ask_id: `ask_${uuidv4()}`,
      offer_price_cents: priceCents,
    };

    // Validate
    try {
      BuyerCounterOfferMessageSchema.parse(msg);
    } catch (error) {
      this.emit('error', new Error(`Invalid counter-offer: ${error}`));
      return;
    }

    const messageBytes = Buffer.from(JSON.stringify(msg, null, 2));
    msg.signature = await signMessage(messageBytes, this.config.privateKey);

    await this.connection!.send(msg);
    this.emit('counter_offer_sent', { priceCents });
  }

  /**
   * Send walkaway message.
   */
  private async sendWalkaway(reason: string): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: any = {
      type: 'session_walkaway',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: this.sessionId!,
      round_number: this.currentRound++,

      reason,
    };

    // Validate
    try {
      SessionWalkawayMessageSchema.parse(msg);
    } catch (error) {
      this.emit('error', new Error(`Invalid walkaway: ${error}`));
      return;
    }

    const messageBytes = Buffer.from(JSON.stringify(msg, null, 2));
    msg.signature = await signMessage(messageBytes, this.config.privateKey);

    await this.connection!.send(msg);
  }
}
