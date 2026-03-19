/**
 * Message type definitions and Zod schemas for agent-to-agent communication.
 * 
 * All messages must:
 * 1. Include signature (Ed25519 hex)
 * 2. Include timestamp
 * 3. Include type identifier
 * 4. Be JSON-serializable
 */

import { z } from 'zod';

// ===== Base Message Schema =====

export const BaseMessageSchema = z.object({
  type: z.string(),
  timestamp: z.number().int().positive(),
  signature: z.string().regex(/^[0-9a-f]*$/),
  sender_id: z.string(),
  session_id: z.string(),
  round_number: z.number().int().nonnegative(),
});

// ===== Hotel Vertical Messages =====

/**
 * BUYER INTENT: Buyer announces what they're looking for.
 * State: OPEN → MATCHING
 */
export const BuyerIntentMessageSchema = BaseMessageSchema.extend({
  type: z.literal('buyer_intent'),
  vertical: z.literal('hotels'),
  
  // Hotel-specific fields
  check_in_date: z.string().date(),
  check_out_date: z.string().date(),
  budget_ceiling_cents: z.number().int().positive(), // Max cents willing to pay per night
  occupants: z.number().int().min(1),
  room_types: z.array(z.string()).min(1), // ["deluxe_king", "standard_queen"]
  preferred_terms: z.record(z.string(), z.any()).optional(),
});

export type BuyerIntentMessage = z.infer<typeof BuyerIntentMessageSchema>;

/**
 * SELLER ASK: Seller publishes what they're offering.
 * State: OPEN → MATCHING
 */
export const SellerAskMessageSchema = BaseMessageSchema.extend({
  type: z.literal('seller_ask'),
  vertical: z.literal('hotels'),
  
  // Hotel-specific fields
  room_id: z.string(),
  room_type: z.string(),
  available_from_date: z.string().date(),
  available_to_date: z.string().date(),
  max_occupants: z.number().int().min(1),
  floor_price_cents: z.number().int().nonnegative(), // Minimum per night
  base_price_cents: z.number().int().positive(), // Standard rate
  stake_amount_cents: z.number().int().nonnegative(), // Performance bond
  seller_reputation_score: z.number().int().min(0).max(100),
  terms: z.record(z.string(), z.any()).optional(),
});

export type SellerAskMessage = z.infer<typeof SellerAskMessageSchema>;

/**
 * BUYER COUNTER-OFFER: Buyer responds to ask with counter price.
 * State: NEGOTIATING
 */
export const BuyerCounterOfferMessageSchema = BaseMessageSchema.extend({
  type: z.literal('buyer_counter_offer'),
  vertical: z.literal('hotels'),
  
  ask_id: z.string(),
  offer_price_cents: z.number().int().positive(),
});

export type BuyerCounterOfferMessage = z.infer<typeof BuyerCounterOfferMessageSchema>;

/**
 * SELLER COUNTER-OFFER: Seller responds to buyer counter.
 * State: NEGOTIATING
 */
export const SellerCounterOfferMessageSchema = BaseMessageSchema.extend({
  type: z.literal('seller_counter_offer'),
  vertical: z.literal('hotels'),
  
  intent_id: z.string(),
  counter_price_cents: z.number().int().positive(),
});

export type SellerCounterOfferMessage = z.infer<typeof SellerCounterOfferMessageSchema>;

/**
 * DEAL ACCEPTED: Either party accepts the final offer.
 * State: NEGOTIATING → AGREED
 */
export const DealAcceptedMessageSchema = BaseMessageSchema.extend({
  type: z.literal('deal_accepted'),
  vertical: z.literal('hotels'),
  
  agreed_price_cents: z.number().int().positive(),
  check_in_date: z.string().date(),
  check_out_date: z.string().date(),
});

export type DealAcceptedMessage = z.infer<typeof DealAcceptedMessageSchema>;

/**
 * SESSION WALKAWAY: Either party abandons negotiation.
 * State: NEGOTIATING → FAILED
 */
export const SessionWalkawayMessageSchema = BaseMessageSchema.extend({
  type: z.literal('session_walkaway'),
  vertical: z.literal('hotels'),
  
  reason: z.string().optional(),
});

export type SessionWalkawayMessage = z.infer<typeof SessionWalkawayMessageSchema>;

/**
 * SETTLEMENT COMPLETE: Exchange confirms payment settled and booking complete.
 * State: SETTLING → COMPLETE
 */
export const SettlementCompleteMessageSchema = BaseMessageSchema.extend({
  type: z.literal('settlement_complete'),
  vertical: z.literal('hotels'),
  
  transaction_id: z.string(),
  booking_ref: z.string(),
  final_price_cents: z.number().int().positive(),
  check_in_date: z.string().date(),
  check_out_date: z.string().date(),
});

export type SettlementCompleteMessage = z.infer<typeof SettlementCompleteMessageSchema>;

/**
 * Union type for all messages.
 */
export type Message =
  | BuyerIntentMessage
  | SellerAskMessage
  | BuyerCounterOfferMessage
  | SellerCounterOfferMessage
  | DealAcceptedMessage
  | SessionWalkawayMessage
  | SettlementCompleteMessage;

/**
 * Parse and validate a message from JSON.
 * 
 * @param json - Message as JSON string
 * @returns Parsed message or null if invalid
 */
export function parseMessage(json: string): Message | null {
  try {
    const obj = JSON.parse(json);
    
    // Try to parse based on type
    switch (obj.type) {
      case 'buyer_intent':
        return BuyerIntentMessageSchema.parse(obj);
      case 'seller_ask':
        return SellerAskMessageSchema.parse(obj);
      case 'buyer_counter_offer':
        return BuyerCounterOfferMessageSchema.parse(obj);
      case 'seller_counter_offer':
        return SellerCounterOfferMessageSchema.parse(obj);
      case 'deal_accepted':
        return DealAcceptedMessageSchema.parse(obj);
      case 'session_walkaway':
        return SessionWalkawayMessageSchema.parse(obj);
      case 'settlement_complete':
        return SettlementCompleteMessageSchema.parse(obj);
      default:
        return null;
    }
  } catch {
    return null;
  }
}
