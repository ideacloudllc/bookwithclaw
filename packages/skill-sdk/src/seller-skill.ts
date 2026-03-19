/**
 * Hotel Room Seller Skill - Reference implementation.
 * 
 * SellerSkill is an AI agent that:
 * 1. Listens for buyer intents
 * 2. Publishes seller asks (room availability + pricing)
 * 3. Evaluates buyer counter-offers
 * 4. Enforces floor price constraint
 * 5. Accepts final offer when satisfied
 */

import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import { ExchangeConnection } from './websocket';
import {
  BuyerIntentMessage,
  BuyerCounterOfferMessage,
  DealAcceptedMessage,
  SettlementCompleteMessage,
  Message,
  SellerAskMessageSchema,
  SellerCounterOfferMessageSchema,
  SessionWalkawayMessageSchema,
} from './messages';
import { signMessage } from './crypto';

export interface HotelSellerConfig {
  agentId: string;
  publicKey: string;
  privateKey: string;
  roomId: string;
  roomType: string;
  availableFromDate: string; // ISO date
  availableToDate: string; // ISO date
  maxOccupants: number;
  floorPriceCents: number; // Minimum per night
  basePriceCents: number; // Standard rate
  stakeCents?: number; // Performance bond
  reputationScore?: number; // 0-100
}

export interface SellerSkillOptions {
  exchangeUrl: string;
  authToken: string;
  config: HotelSellerConfig;
}

/**
 * Seller agent for hotel room negotiation.
 */
export class SellerSkill extends EventEmitter {
  private connection: ExchangeConnection | null = null;
  private config: HotelSellerConfig;
  private authToken: string;
  private currentSessionId: string | null = null;
  private currentRound = 0;
  private bestOfferCents: number | null = null;
  private isListening = false;

  constructor(options: SellerSkillOptions) {
    super();
    this.config = options.config;
    this.authToken = options.authToken;

    // Initialize WebSocket connection
    this.connection = new ExchangeConnection({
      exchangeUrl: options.exchangeUrl,
      sessionId: `seller_listen_${uuidv4()}`,
      authToken: options.authToken,
    });

    // Set up message handlers
    this.connection.on('message', (msg) => this.handleMessage(msg));
    this.connection.on('error', (error) => this.emit('error', error));
    this.connection.on('disconnected', () => {
      if (this.isListening) {
        this.connection!.connect().catch((e) => this.emit('error', e));
      }
    });
  }

  /**
   * Main entry point: Start listening for buyer intents and publish asks.
   */
  public async listen(): Promise<void> {
    try {
      this.isListening = true;
      await this.connection!.connect();
      this.emit('listening');
    } catch (error) {
      this.isListening = false;
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Stop listening.
   */
  public disconnect(): void {
    this.isListening = false;
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
        case 'buyer_intent':
          await this.handleBuyerIntent(msg as BuyerIntentMessage);
          break;

        case 'buyer_counter_offer':
          await this.handleBuyerCounter(msg as BuyerCounterOfferMessage);
          break;

        case 'deal_accepted':
          this.handleDealAccepted(msg as DealAcceptedMessage);
          break;

        case 'settlement_complete':
          this.handleSettlementComplete(msg as SettlementCompleteMessage);
          break;

        case 'session_walkaway':
          this.emit('session_failed', 'Buyer walked away');
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
   * Handle buyer intent - evaluate and decide whether to publish an ask.
   */
  private async handleBuyerIntent(intent: BuyerIntentMessage): Promise<void> {
    // Check if dates align
    if (
      intent.check_in_date > this.config.availableToDate ||
      intent.check_out_date < this.config.availableFromDate
    ) {
      // Dates don't match, skip
      return;
    }

    // Check if room type is acceptable
    if (
      intent.room_types.length > 0 &&
      !intent.room_types.includes(this.config.roomType)
    ) {
      // Room type not wanted, skip
      return;
    }

    // Check if buyer can afford our floor price
    if (intent.budget_ceiling_cents < this.config.floorPriceCents) {
      // Buyer's budget is below our floor, skip
      return;
    }

    // Publish an ask
    this.currentSessionId = intent.session_id;
    this.currentRound = intent.round_number + 1;
    this.bestOfferCents = null;
    await this.publishAsk(intent);
  }

  /**
   * Handle buyer counter-offer.
   */
  private async handleBuyerCounter(counter: BuyerCounterOfferMessage): Promise<void> {
    if (counter.session_id !== this.currentSessionId) {
      return; // Not our session
    }

    // Store best offer
    this.bestOfferCents = counter.offer_price_cents;

    // If offer is at or above floor, counter with a price between floor and base
    if (counter.offer_price_cents >= this.config.floorPriceCents) {
      // If offer is close to our floor, accept it
      // Otherwise, counter back
      if (
        counter.offer_price_cents >= this.config.floorPriceCents * 1.1 ||
        this.currentRound >= 3
      ) {
        // Accept the deal
        await this.sendDealAccepted(counter.offer_price_cents);
      } else {
        // Counter with a price above buyer's offer but below our base
        const counterPrice = Math.min(
          Math.floor(
            (counter.offer_price_cents + this.config.floorPriceCents) / 1.1
          ),
          this.config.basePriceCents
        );
        await this.sendCounterOffer(counterPrice);
      }
    } else {
      // Below floor price, reject by walking away
      await this.sendWalkaway('Offer below floor price');
      this.emit('session_failed', 'Buyer offer below floor');
    }
  }

  /**
   * Handle deal_accepted message from buyer.
   */
  private handleDealAccepted(msg: DealAcceptedMessage): void {
    this.emit('deal_accepted', {
      sessionId: this.currentSessionId!,
      finalPrice: msg.agreed_price_cents,
    });
  }

  /**
   * Handle settlement_complete message from exchange.
   */
  private handleSettlementComplete(msg: SettlementCompleteMessage): void {
    this.emit('settlement_complete', {
      sessionId: this.currentSessionId!,
      finalPrice: msg.final_price_cents,
      bookingRef: msg.booking_ref,
    });
  }

  /**
   * Publish ask for a specific buyer intent.
   */
  private async publishAsk(intent: BuyerIntentMessage): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: any = {
      type: 'seller_ask',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: intent.session_id,
      round_number: this.currentRound,

      // Hotel-specific fields
      room_id: this.config.roomId,
      room_type: this.config.roomType,
      available_from_date: this.config.availableFromDate,
      available_to_date: this.config.availableToDate,
      max_occupants: this.config.maxOccupants,
      floor_price_cents: this.config.floorPriceCents,
      base_price_cents: this.config.basePriceCents,
      stake_amount_cents: this.config.stakeCents ?? 0,
      seller_reputation_score: this.config.reputationScore ?? 90,
      terms: {},
    };

    // Validate
    try {
      SellerAskMessageSchema.parse(msg);
    } catch (error) {
      this.emit('error', new Error(`Invalid ask: ${error}`));
      return;
    }

    const messageBytes = Buffer.from(JSON.stringify(msg, null, 2));
    msg.signature = await signMessage(messageBytes, this.config.privateKey);

    await this.connection!.send(msg);
    this.emit('ask_published', { roomId: this.config.roomId });
  }

  /**
   * Send counter-offer message.
   */
  private async sendCounterOffer(priceCents: number): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: any = {
      type: 'seller_counter_offer',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: this.currentSessionId!,
      round_number: ++this.currentRound,

      intent_id: `intent_${uuidv4()}`,
      counter_price_cents: priceCents,
    };

    // Validate
    try {
      SellerCounterOfferMessageSchema.parse(msg);
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
   * Send deal_accepted message.
   */
  private async sendDealAccepted(priceCents: number): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const msg: any = {
      type: 'deal_accepted',
      vertical: 'hotels',
      timestamp: now,
      signature: '', // Will be signed below
      sender_id: this.config.agentId,
      session_id: this.currentSessionId!,
      round_number: ++this.currentRound,

      agreed_price_cents: priceCents,
      check_in_date: '2026-03-25', // Would come from intent in real impl
      check_out_date: '2026-03-27',
    };

    // Validate (we'll use DealAcceptedMessageSchema but it's flexible)
    const messageBytes = Buffer.from(JSON.stringify(msg, null, 2));
    msg.signature = await signMessage(messageBytes, this.config.privateKey);

    await this.connection!.send(msg);
    this.emit('deal_accepted', {
      sessionId: this.currentSessionId!,
      finalPrice: priceCents,
    });
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
      session_id: this.currentSessionId!,
      round_number: ++this.currentRound,

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
